from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from typing import List
from app.schemas.user import UserBase
# Create: 只需要 title, content, (可选 priority)。
# Update: 可以改 status (比如改为 Closed)，或者改 content。
# Out: 返回所有信息 + 提问者的名字。


# 2. 返回给前端的信息
class IssueCreate(BaseModel):
    title: str
    content: str
    priority: Optional[str] = "low"  # low, medium, high


class IssueUpdate(BaseModel):
    status: Optional[str] = None  # open or closed
    content: Optional[str] = None
    priority: Optional[str] = None  # low, medium, high


# 1. 创建评论 (前端发来的)
class CommentCreate(BaseModel):
    content: str


# 2. 返回评论 (后端给前端的)
class CommentOut(BaseModel):
    id: int
    issue_id: int
    user_id: int
    content: str
    created_at: datetime

    user: UserBase  # 嵌套显示回复人信息

    class Config:
        orm_mode = True


class IssueOut(BaseModel):
    id: int
    project_id: int
    creator_id: int
    title: str
    content: str
    status: str
    priority: str
    created_at: datetime
    # 新增这个字段，默认是空列表
    comments: List[CommentOut] = []

    class Config:
        orm_mode = True

    class Config:
        orm_mode = True
