from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.crud.member import get_member
from app.utils.file_ops import save_upload_file, get_file_summary, calculate_file_hash # 导入 hash 函数
from app.crud.document import create_document, get_project_documents, get_document_by_name, update_document # 导入 CRUD

from app.crud.document import (
    soft_delete_document as crud_soft_delete, # 改个名
    restore_document as crud_restore,         # 改个名
    hard_delete_document as crud_hard_delete  # 改个名
)

from app.schemas.document import DocumentOut
from app.models.document import Document
from app.crud.project import get_project # 复用检查项目是否存在的逻辑
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.utils.file_ops import save_upload_file, get_file_summary

from pydantic import BaseModel
import hashlib

import os

router = APIRouter()
#/projects/{project_id}/docs/
@router.post("/projects/{project_id}/docs/upload", response_model=DocumentOut)
def upload_document(
    project_id: int,
    overwrite: bool = False, # <--- 新增参数：是否允许覆盖，默认为 False
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 检查项目是否存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    # 2. 计算新上传文件的 Hash
    new_hash = calculate_file_hash(file)

    # 3. 检查有没有同名文件
    existing_doc = get_document_by_name(db, project_id, file.filename)

    if existing_doc:
        # 情况 A: 文件名相同，Hash 也相同 -> 绝对的重复上传
        if existing_doc.file_hash == new_hash:
            raise HTTPException(status_code=400, detail="文件已存在且内容未变，请勿重复提交")
        
        # 情况 B: 文件名相同，Hash 不同 -> 内容变了，但没有开启覆盖开关
        if not overwrite:
            # 返回 409 Conflict，告诉前端："有冲突，如果你想覆盖，请带上 overwrite=true 重发"
            raise HTTPException(
                status_code=409, 
                detail=f"文件 '{file.filename}' 已存在。是否覆盖？"
            )
            
        # 情况 C: 开启了覆盖，准备进行更新操作
        # (此时我们应该先删掉旧的物理文件，但为了安全，我们先上传新的，再把旧的记录指过去)
        # 注意：这里我们选择生成一个新的物理文件，而不覆盖旧物理文件，防止写入失败导致文件损坏
    
    # --- 开始上传流程 ---
    
    try:
        physical_path = save_upload_file(file, project_id=project_id)
        file_size = os.path.getsize(physical_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

    summary = get_file_summary(physical_path)
    if len(summary) < 10:
        os.remove(physical_path)
        raise HTTPException(status_code=400, detail="文档内容过少")

    # 4. 分支处理：是更新旧记录，还是创建新记录？
    if existing_doc and overwrite:
        # --- 重点检查这里 ---
        # 获取旧文件的路径
        old_path = existing_doc.physical_path
        
        # 尝试删除旧文件
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
                print(f"成功删除旧文件: {old_path}") # 调试用
            except Exception as e:
                print(f"删除旧文件失败: {e}") # 打印错误，但不中断流程

        # 更新数据库记录
        doc = update_document(
            db=db,
            db_obj=existing_doc,
            new_physical_path=physical_path, # 这里是指向新上传的文件
            new_size=file_size,
            new_summary=summary,
            new_hash=new_hash
        )
    else:
        # 创建新记录
        doc = create_document(
            db=db,
            project_id=project_id,
            uploader_id=current_user.id,
            filename=file.filename,
            physical_path=physical_path,
            size=file_size,
            summary=summary,
            file_hash=new_hash
        )
    
    return doc

@router.get("/projects/{project_id}/docs/list", response_model=List[DocumentOut])
def list_documents(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 检查项目是否存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
        
    #2.权限检查
    if not get_member(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="你不是该项目成员")
    
    return get_project_documents(db, project_id)

@router.delete("/projects/{project_id}/docs/{document_id}/delete")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #1. 检查该文档是否存在
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    #2. 权限检验 该用户有没有权限删除该文档
    #document.uploader_id  上传者ID   current_user.id 当前用户ID   document.project.owner_id 项目所有者ID
    #删除满足的条件 上传者亲自删除或者管理员来删除
    if not (doc.uploader_id == current_user.id or doc.project.owner_id == current_user.id):
        raise HTTPException(status_code=403, detail="没有权限删除该文档")
    
    #3. 软删除：标记为已删除
    crud_soft_delete(db, doc)
    return {"msg": "文档已移入回收站"}

@router.get("/projects/{project_id}/docs/{document_id}/restore")
def restore_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #1. 检查文档是否存在于回收站
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.is_deleted == True
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="回收站中未找到该文档")

    #2. 权限检验 该用户有没有权限恢复该文档
    #document.uploader_id  上传者ID   current_user.id 当前用户ID   document.project.owner_id 项目所有者ID
    #恢复满足的条件 上传者亲自恢复或者管理员来恢复
    if not (doc.uploader_id == current_user.id or doc.project.owner_id == current_user.id):
        raise HTTPException(status_code=403, detail="没有权限恢复该文档")

    #3. 恢复：标记为未删除
    crud_restore(db, doc)
    return {"msg": "文档已从回收站恢复"}

@router.delete("/projects/{project_id}/docs/{document_id}/hard_delete")
def hard_delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #1.检查该文档是否在回收站中
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.is_deleted == True
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="回收站中未找到该文档")
    
    #2.权限检验 该用户有没有权限彻底删除该文档
    if not (doc.uploader_id == current_user.id or doc.project.owner_id == current_user.id):
        raise HTTPException(status_code=403, detail="没有权限彻底删除该文档")
    
    #3.彻底删除物理文件
    physical_path = doc.physical_path
    if os.path.exists(physical_path):
        try:
            os.remove(physical_path)
        except Exception as e:
            print(f"删除物理文件失败: {e}")
            raise HTTPException(status_code=500, detail=f"删除物理文件失败: {str(e)}")
        
    #4.从数据库中删除记录
    crud_hard_delete(db, doc)
    return {"msg": "文档已被彻底删除"}

@router.get("/projects/{project_id}/trashbin", response_model=List[DocumentOut])
def list_trashed_documents(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #1.检查项目是否存在
    project = get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    
    #2.权限检查
    if not get_member(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="你不是该项目成员")
    
    #3.获取回收站中的文档
    trashed_docs = db.query(Document).filter(
        Document.project_id == project_id,
        Document.is_deleted == True
    ).all()
    
    return trashed_docs

class ContentUpdate(BaseModel):
    content: str

# --- 接口 1: 读取文档内容 ---
@router.get("/projects/{project_id}/docs/{document_id}/content")
def get_document_content(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 查记录
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 2. 权限检查 (成员才能看)
    if not get_member(db, doc.project_id, current_user.id):
        raise HTTPException(status_code=403, detail="你不是该项目成员")

    # 3. 检查文件是否存在
    if not os.path.exists(doc.physical_path):
        raise HTTPException(status_code=404, detail="物理文件丢失")

    # 4. 读取文件内容
    # 注意：这里限制一下文件后缀，防止读取了图片乱码
    if not doc.original_filename.lower().endswith(('.md', '.txt', '.markdown')):
         raise HTTPException(status_code=400, detail="该文件不支持在线编辑")

    try:
        with open(doc.physical_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取失败: {str(e)}")

# --- 接口 2: 保存文档内容 ---
@router.put("/projects/{project_id}/docs/{document_id}/content")
def update_document_content(
    document_id: int,
    update_in: ContentUpdate, # 接收 JSON: {"content": "..."}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 查记录
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 2. 权限检查 (只有上传者或管理员能改? 或者所有成员都能改?)
    if not get_member(db, doc.project_id, current_user.id):
        raise HTTPException(status_code=403, detail="你不是该项目成员")

    # 3. 覆盖写入物理文件
    try:
        # 将字符串转为字节
        content_bytes = update_in.content.encode('utf-8')
        
        with open(doc.physical_path, "wb") as f:
            f.write(content_bytes)
            
        # 4. 重新计算 Hash 和 大小 (重要！保持元数据同步)
        new_size = len(content_bytes)
        new_hash = hashlib.md5(content_bytes).hexdigest()
        
        # 更新数据库
        doc.size_bytes = new_size
        doc.file_hash = new_hash
        # doc.updated_at = datetime.now() # 如果你有 updated_at 字段
        
        db.add(doc)
        db.commit()
        
        return {"msg": "保存成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")
    
#文件下载接口
@router.get("/projects/{project_id}/docs/{document_id}/download")
def download_document(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Check if document exists
    doc = db.query(Document).filter(Document.id == document_id, Document.project_id == project_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    #用户鉴权
    if not get_member(db, project_id, current_user.id):
        raise HTTPException(status_code=403, detail="你不是该项目成员")
    
    # 2. Check if physical file exists
    if not os.path.exists(doc.physical_path):
        raise HTTPException(status_code=404, detail="物理文件丢失")
    # 3. Return file response
    # filename argument sets the name of the downloaded file
    return FileResponse(path=doc.physical_path, filename=doc.original_filename)