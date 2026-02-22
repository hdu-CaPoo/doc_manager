from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.document import Document

# 1. 查询类操作

def get_document_by_id(db: Session, document_id: int) -> Optional[Document]:
    """根据ID获取文档（不区分是否删除）"""
    return db.query(Document).filter(Document.id == document_id).first()

def get_document_by_name(db: Session, project_id: int, filename: str) -> Optional[Document]:
    """根据文件名查找未删除的文档"""
    return db.query(Document).filter(
        Document.project_id == project_id,
        Document.original_filename == filename,
        Document.is_deleted == False
    ).first()

def get_trash_document_by_id(db: Session, document_id: int) -> Optional[Document]:
    """根据ID获取回收站中的文档"""
    return db.query(Document).filter(
        Document.id == document_id,
        Document.is_deleted == True
    ).first()

def get_project_documents(db: Session, project_id: int) -> List[Document]:
    """获取项目下的所有正常文档"""
    return db.query(Document).filter(
        Document.project_id == project_id, 
        Document.is_deleted == False
    ).all()

def get_trash_documents(db: Session, project_id: int) -> List[Document]:
    """获取项目下的所有回收站文档"""
    return db.query(Document).filter(
        Document.project_id == project_id,
        Document.is_deleted == True
    ).all()

# 2. 写入类操作

def create_document(
    db: Session, 
    project_id: int,
    uploader_id: int,
    filename: str,
    physical_path: str,
    size: int,
    summary: str,
    file_hash: str
) -> Document:
    """创建新文档记录"""
    db_doc = Document(
        project_id=project_id,
        uploader_id=uploader_id,
        original_filename=filename,
        physical_path=physical_path,
        size_bytes=size,
        summary=summary,
        file_hash=file_hash,
        status="active",
        is_deleted=False
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

def update_document(
    db: Session, 
    db_obj: Document, 
    new_physical_path: str,
    new_size: int,
    new_summary: str,
    new_hash: str
) -> Document:
    """更新文档内容（覆盖上传）"""
    db_obj.physical_path = new_physical_path #type: ignore
    db_obj.size_bytes = new_size#type: ignore
    db_obj.summary = new_summary#type: ignore
    db_obj.file_hash = new_hash#type: ignore
    # 如果有 updated_at 字段，ORM通常会自动更新，或者手动在这里更新
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# 3. 状态变更类操作

def soft_delete_document(db: Session, db_obj: Document) -> Document:
    """软删除：移入回收站"""
    db_obj.is_deleted = True #type: ignore
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def restore_document(db: Session, db_obj: Document) -> Document:
    """恢复文档"""
    db_obj.is_deleted = False #type: ignore
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def hard_delete_document(db: Session, db_obj: Document):
    """硬删除：从数据库物理删除记录"""
    db.delete(db_obj)
    db.commit()