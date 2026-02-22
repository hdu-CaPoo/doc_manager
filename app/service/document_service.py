from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.crud.member import get_member
from app.crud.project import get_project
from app.crud.document import create_document, get_project_documents, get_document_by_name, update_document, get_document_by_id, get_trash_documents, get_trash_document_by_id # 导入 CRUD
from app.crud.document import (
    soft_delete_document as crud_soft_delete, # 改个名
    restore_document as crud_restore,         # 改个名
    hard_delete_document as crud_hard_delete  # 改个名
)
from app.models.user import User
from app.utils.file_ops import save_upload_file, get_file_summary, calculate_file_hash # 导入 hash 函数
from app.schemas.document import ContentUpdate
from app.core.exceptions import ResourceNotFound, PermissionDenied, FileConflictError, InvalidFileError, InternalServerError

import hashlib
import os

class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def upload_document(self, project_id: int, file: UploadFile, current_user: User, overwrite: bool = False):
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 检查用户是否是项目成员
        
        member = get_member(self.db, project_id, current_user.id) # type: ignore
        if not member:
            raise PermissionDenied("你不是该项目的成员，无法上传文档")
        
        # 3. 计算文件哈希值，检查是否已存在同名文件
        file_hash = calculate_file_hash(file) # 计算哈希值
        existing_doc = get_document_by_name(self.db, project_id, file.filename) # type: ignore
        
        if existing_doc:
            # 情况 A: 文件名相同，Hash 也相同 -> 绝对的重复上传
            if existing_doc.hash == file_hash:
                raise FileConflictError("你已经上传过同样的文件了，无需重复上传")

            # 情况 B: 文件名相同，Hash 不同 -> 内容变了，但没有开启覆盖开关
            if not overwrite:
                raise FileConflictError("同名文件已存在，请选择覆盖或更改文件名")
            else:
                # 如果选择覆盖，先软删除原有文档
                crud_soft_delete(self.db, existing_doc.id) # type: ignore
        
        # --- 开始上传流程 ---
    
        try:
            physical_path = save_upload_file(file, project_id=project_id)
            file_size = os.path.getsize(physical_path)
        except Exception as e:
            raise InternalServerError(f"文件上传失败: {str(e)}")

        summary = get_file_summary(physical_path)
        if len(summary) < 10:
            os.remove(physical_path)
            raise InvalidFileError("文档内容过少")

        # 4. 分支处理：是更新旧记录，还是创建新记录？
        if existing_doc and overwrite:
            # --- 重点检查这里 ---
            # 获取旧文件的路径
            old_path = existing_doc.physical_path
            
            # 尝试删除旧文件
            if os.path.exists(old_path):  # type: ignore
                try:
                    os.remove(old_path)  # type: ignore
                    print(f"成功删除旧文件: {old_path}") # 调试用
                except Exception as e:
                    print(f"删除旧文件失败: {e}") # 打印错误，但不中断流程

            # 更新数据库记录
            doc = update_document(
                db=self.db,
                db_obj=existing_doc,
                new_physical_path=physical_path, # 这里是指向新上传的文件
                new_size=file_size,
                new_summary=summary,
                new_hash=file_hash
            )
        else:
            # 创建新记录
            doc = create_document(
                db=self.db,
                project_id=project_id,
                uploader_id=current_user.id,# type: ignore
                filename=file.filename,# type: ignore
                physical_path=physical_path,
                size=file_size,
                summary=summary,
                file_hash=file_hash
            )
        
        return doc

    def list_document(self, project_id: int, current_user: User):
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 检查用户是否是项目成员
        member = get_member(self.db, project_id, current_user.id) # type: ignore
        if not member:
            raise PermissionDenied("你不是该项目的成员，无法查看文档")
        
        # 3. 获取文档列表
        documents = get_project_documents(self.db, project_id)
        return documents
    
    def delete_document(self, document_id: int, current_user: User):
        #1. 检查该文档是否存在
        doc = get_document_by_id(self.db, document_id)
        if not doc:
            raise ResourceNotFound("文档不存在")
        
        #2. 权限检验 该用户有没有权限删除该文档
        #document.uploader_id  上传者ID   current_user.id 当前用户ID   document.project.owner_id 项目所有者ID
        #删除满足的条件 上传者亲自删除或者管理员来删除
        member = get_member(self.db, doc.project_id, current_user.id) # type: ignore
        if not (doc.uploader_id == current_user.id or doc.project.owner_id == current_user.id): # type: ignore
            raise PermissionDenied("没有权限删除该文档")
        
        #3. 软删除
        crud_soft_delete(self.db, doc)
        return ("文档已移入回收站")
    
    def restore_document(self, document_id: int, current_user: User):
        #1. 检查文档是否在回收站
        doc = get_trash_document_by_id(self.db, document_id)
        if not doc:
            raise ResourceNotFound("回收站内没有该文档")
        
        #2. 权限检验 该用户有没有权限恢复该文档
        member = get_member(self.db, doc.project_id, current_user.id) # type: ignore
        if not (doc.uploader_id == current_user.id or doc.project.owner_id == current_user.id): # type: ignore
            raise PermissionDenied("没有权限恢复该文档")
        
        #3. 恢复
        crud_restore(self.db, doc)
        return ("文档已恢复")
    
    def hard_delete_document(self, document_id: int, current_user: User):
        #1. 检查文档是否在回收站
        doc = get_trash_document_by_id(self.db, document_id)
        if not doc:
            raise ResourceNotFound("回收站内没有该文档")
        
        #2. 权限检验 该用户有没有权限彻底删除该文档
        member = get_member(self.db, doc.project_id, current_user.id) # type: ignore
        if not (doc.uploader_id == current_user.id or doc.project.owner_id == current_user.id): # type: ignore
            raise PermissionDenied("没有权限删除该文档")
        
        #3. 彻底删除（物理文件 + 数据库记录）
        crud_hard_delete(self.db, doc)

        physical_path = doc.physical_path
        if os.path.exists(physical_path): # type: ignore
            try:
                os.remove(physical_path) # type: ignore
                print(f"成功删除物理文件: {physical_path}") # 调试用
            except Exception as e:
                print(f"删除物理文件失败: {e}")
                raise InternalServerError(f"删除物理文件失败: {str(e)}")

        return ("文档已被彻底删除")
    
    def list_trashed_documents(self, project_id: int, current_user: User):
        # 1. 检查项目是否存在
        project = get_project(self.db, project_id)
        if not project:
            raise ResourceNotFound("项目不存在")
        
        # 2. 检查用户是否是项目成员
        member = get_member(self.db, project_id, current_user.id) # type: ignore
        if not member:
            raise PermissionDenied("你不是该项目的成员，无法查看回收站")
        
        # 3. 获取回收站内文档列表
        trash_documents = get_trash_documents(self.db, project_id)
        return trash_documents


    #读取/修改文档内容详细
    def get_document_content(self, document_id: int, current_user: User)-> str:  #
        #1. 检查文档是否存在
        doc = get_document_by_id(self.db, document_id)
        if not doc:
            raise ResourceNotFound("文档不存在")
        
        #2. 权限检验 该用户有没有权限查看该文档
        member = get_member(self.db, doc.project_id, current_user.id) # type: ignore
        if not member:
            raise PermissionDenied("没有权限查看该文档")
        
        #3. 物理存在性检验
        if not os.path.exists(doc.physical_path): # type: ignore
            raise ResourceNotFound("物理文件丢失")

        # 4. 读取文件内容
        # 注意：这里限制一下文件后缀，防止读取了图片乱码
        if not doc.original_filename.lower().endswith(('.md', '.txt', '.markdown')):
            raise InvalidFileError("该文件不支持在线编辑")

        try:
            with open(doc.physical_path, "r", encoding="utf-8") as f: # type: ignore
                content = f.read() # type: ignore
            return content # type: ignore
        except Exception as e:
            raise InternalServerError(f"读取失败: {str(e)}")
        
    def update_document_content(self, document_id: int, update_in: ContentUpdate, current_user: User):
        #1. 检查文档是否存在
        doc = get_document_by_id(self.db, document_id)
        if not doc:
            raise ResourceNotFound("文档不存在")
        
        #2. 权限检验 该用户有没有权限修改该文档
        member = get_member(self.db, doc.project_id, current_user.id) # type: ignore
        if not member:
            raise PermissionDenied("没有权限修改该文档")
        
        #3. 物理存在性检验
        if not os.path.exists(doc.physical_path): # type: ignore
            raise ResourceNotFound("物理文件丢失")

        #4. 覆盖写入物理文件
        try:
            # 将字符串转为字节
            content_bytes = update_in.content.encode('utf-8')
            
            with open(doc.physical_path, "wb") as f: # type: ignore
                f.write(content_bytes) # type: ignore
                
            # 4. 重新计算 Hash 和 大小 (重要！保持元数据同步)
            new_size = len(content_bytes)
            new_hash = hashlib.md5(content_bytes).hexdigest()
            
            # 更新数据库
            doc.size_bytes = new_size# type: ignore
            doc.file_hash = new_hash# type: ignore
            # doc.updated_at = datetime.now() # 如果你有 updated_at 字段
            
            self.db.add(doc)
            self.db.commit()
            
            return {"msg": "保存成功"}
            
        except Exception as e:
            raise InternalServerError(f"保存失败: {str(e)}")
        

    def download_document(self, document_id: int, current_user: User):
        #1. 检查文档是否存在
        doc = get_document_by_id(self.db, document_id)
        if not doc:
            raise ResourceNotFound("文档不存在")
        
        #2. 权限检验 该用户有没有权限下载该文档
        member = get_member(self.db, doc.project_id, current_user.id) # type: ignore
        if not member:
            raise PermissionDenied("没有权限下载该文档")
        
        #3. 物理存在性检验
        if not os.path.exists(doc.physical_path): # type: ignore
            raise ResourceNotFound("物理文件丢失")

        return FileResponse(path=doc.physical_path, filename=doc.original_filename, media_type='application/octet-stream') # type: ignore