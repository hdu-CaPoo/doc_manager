# 这是用户模型文件 定义了用户表的结构和关系
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nickname = Column(String)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    avatar_url = Column(String, nullable=True) # 可以为空，默认没头像
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    projects_owned = relationship("Project", back_populates="owner")
    project_memberships = relationship("ProjectMember", back_populates="user")