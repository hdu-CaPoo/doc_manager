from pydantic import BaseModel
from datetime import datetime
from app.schemas.user import UserBase # 复用用户的基本信息

# 1. 加入项目时的请求体
class JoinProject(BaseModel):
    invitation_code: str

# 2. 返回成员信息（包含用户详情）
class ProjectMemberOut(BaseModel):
    project_id: int
    user_id: int
    role: str
    joined_at: datetime
    
    # 这里有点技巧：我们希望直接返回 User 的名字，而不是光给个 ID
    user: UserBase 

    class Config:
        orm_mode = True