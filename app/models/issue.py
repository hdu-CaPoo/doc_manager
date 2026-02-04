from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Issue(Base):
    __tablename__ = "issues"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    status = Column(String, default="open")  # open or closed
    priority = Column(String, default="medium")  # low, medium, high
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project")
    creator = relationship("User")
    # --- 新增：关联评论 ---
    comments = relationship(
        "IssueComment", back_populates="issue", cascade="all, delete-orphan"
    )


# --- 新增：评论表 ---
class IssueComment(Base):
    __tablename__ = "issue_comments"

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"))  # 关联哪个问题
    user_id = Column(Integer, ForeignKey("users.id"))  # 谁回复的
    content = Column(String, nullable=False)  # 回复内容
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    issue = relationship("Issue", back_populates="comments")
    user = relationship("User")  # 方便获取回复者的昵称
