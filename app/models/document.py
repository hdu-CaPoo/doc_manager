# 这是文档模型文件 定义了文档表的结构和关系
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    uploader_id = Column(Integer, ForeignKey("users.id"))
    original_filename = Column(String, nullable=False)
    physical_path = Column(String, nullable=False, unique=True)
    summary = Column(String(255))
    size_bytes = Column(Integer)
    status = Column(String, default="active")
    file_hash = Column(String(64), index=True) # 存储 MD5 或 SHA256 用于去重
    is_deleted = Column(Boolean, default=False, index=True) # 软删除标志
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="documents") #这里的Project是字符串形式的类名 project是个对象的属性 反向关联到 Project类里面的 documents 属性
    uploader = relationship("User")