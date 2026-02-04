from sqlalchemy.orm import Session
from app.models.document import Document


# 1. 新增：根据文件名查找
def get_document_by_name(db: Session, project_id: int, filename: str):
    return (
        db.query(Document)
        .filter(
            Document.project_id == project_id,
            Document.original_filename == filename,
            Document.is_deleted == False,  # 只查未删除的文件
        )
        .first()
    )


# 查看回收站内文件
def get_trash_documents(db: Session, project_id: int):
    return (
        db.query(Document)
        .filter(
            Document.project_id == project_id,
            Document.is_deleted == True,  # 只查已删除的文件
        )
        .all()
    )


# 2. 修改：创建文档（增加 file_hash 参数）
def create_document(
    db: Session,
    project_id: int,
    uploader_id: int,
    filename: str,
    physical_path: str,
    size: int,
    summary: str,
    file_hash: str,
):
    db_doc = Document(
        project_id=project_id,
        uploader_id=uploader_id,
        original_filename=filename,
        physical_path=physical_path,
        size_bytes=size,  # 注意：数据库字段叫 size_bytes，参数叫 size
        summary=summary,
        file_hash=file_hash,
        status="active",
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc


# 3. 新增：更新文档（覆盖逻辑）
def update_document(
    db: Session,
    db_obj: Document,
    new_physical_path: str,
    new_size: int,
    new_summary: str,
    new_hash: str,
):
    db_obj.physical_path = new_physical_path
    db_obj.size_bytes = new_size
    db_obj.summary = new_summary
    db_obj.file_hash = new_hash
    # 更新时间也会自动变（如果是配置了 onupdate）

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# 4. 获取某个项目的所有文档
def get_project_documents(db: Session, project_id: int):
    return (
        db.query(Document)
        .filter(Document.project_id == project_id, Document.is_deleted == False)
        .all()
    )


# 5.1. 移入回收站 (Soft Delete)
def soft_delete_document(db: Session, db_obj: Document):
    db_obj.is_deleted = True
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# 5.2. 恢复 (Restore)
def restore_document(db: Session, db_obj: Document):
    db_obj.is_deleted = False
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


# 5.3. 彻底删除 (Hard Delete) - 只有这个才删物理文件
def hard_delete_document(db: Session, db_obj: Document):
    db.delete(db_obj)
    db.commit()
