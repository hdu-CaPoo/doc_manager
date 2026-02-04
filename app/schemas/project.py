from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# 1. 基础模型 (共享字段)
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


# 2. 创建时需要的字段
class ProjectCreate(ProjectBase):
    pass  # 只需要 name 和 description


# 3. 更新时需要的字段
class ProjectUpdate(ProjectBase):
    name: Optional[str] = None  # 都是可选的


# 4. 返回给前端的字段
class ProjectOut(ProjectBase):
    id: int
    invitation_code: str
    owner_id: int
    created_at: datetime

    # 可选：如果你想在列表里直接返回 Owner 的详细信息
    # owner: UserOut

    class Config:
        orm_mode = True
