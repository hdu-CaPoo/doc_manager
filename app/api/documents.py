from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.schemas.document import DocumentOut, ContentUpdate
from app.api.deps import get_db, get_current_user
from app.models.user import User

from app.core.exceptions import FileConflictError

from app.service.document_service import DocumentService # 引入 Service 层

router = APIRouter()
#/projects/{project_id}/docs/
@router.post("/projects/{project_id}/docs/upload", response_model=DocumentOut)
def upload_document(
    project_id: int,
    overwrite: bool = False,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document_service = DocumentService(db)
    try:
        # 注意：Service 的 upload_document 返回的是 Document 模型对象
        doc = document_service.upload_document(
            project_id=project_id,
            current_user=current_user,
            file=file,
            overwrite=overwrite
        )
        return doc
        
    except FileConflictError as e:
        if "已存在" in str(e):
             raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail=f"文件 '{file.filename}' 已存在。是否覆盖？"
            )
        # 如果是其他业务错误（比如文件太小），直接抛出，让全局处理
        raise e
    

@router.get("/projects/{project_id}/docs/list", response_model=List[DocumentOut])
def list_documents(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document_service = DocumentService(db)
    docs = document_service.list_document(project_id=project_id, current_user=current_user)
    return docs

@router.delete("/projects/{project_id}/docs/{document_id}/delete")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document_service = DocumentService(db)
    document_service.delete_document(document_id=document_id, current_user=current_user)
    return {"msg": "文档已移入回收站"}

@router.get("/projects/{project_id}/docs/{document_id}/restore")
def restore_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document_service = DocumentService(db)
    document_service.restore_document(document_id=document_id, current_user=current_user)
    return {"msg": "文档已从回收站恢复"}

@router.delete("/projects/{project_id}/docs/{document_id}/hard_delete")
def hard_delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document_service = DocumentService(db)
    document_service.hard_delete_document(document_id=document_id, current_user=current_user)
    return {"msg": "文档已被永久删除"}

@router.get("/projects/{project_id}/trashbin", response_model=List[DocumentOut])
def list_trashed_documents(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document_service = DocumentService(db)
    trashed_docs = document_service.list_trashed_documents(project_id=project_id, current_user=current_user)
    return trashed_docs

@router.get("/projects/{project_id}/docs/{document_id}/content")
def get_document_content(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document_service = DocumentService(db)
    return document_service.get_document_content(document_id=document_id, current_user=current_user)

@router.put("/projects/{project_id}/docs/{document_id}/content")
def update_document_content(
    document_id: int,
    update_in: ContentUpdate, # 接收 JSON: {"content": "..."}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document_service = DocumentService(db)
    document_service.update_document_content(
        document_id=document_id, 
        update_in=update_in, 
        current_user=current_user
    )
    return {"msg": "文档内容已更新"}
    
#文件下载接口
@router.get("/projects/{project_id}/docs/{document_id}/download")
def download_document(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document_service = DocumentService(db)
    return document_service.download_document(document_id=document_id, current_user=current_user)