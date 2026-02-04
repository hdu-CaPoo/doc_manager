#json传入数据校验

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 1. 基础模型：包含大家都需要的字段
class UserBase(BaseModel):
    email: EmailStr
    nickname: Optional[str] = None

# 2. 注册时需要的模型 (前端 -> 后端)
# 用户注册时必须传 password
class UserCreate(UserBase):
    password: str
    verification_code: str

# 3. 返回给用户的模型 (后端 -> 前端)
# 绝对不能返回 password！所以这里不包含 password 字段
class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    avatar_url: Optional[str]
    
    # 这是一个配置项，告诉 Pydantic：“你可以从 ORM 模型（数据库对象）里读取数据”
    class Config:
        orm_mode = True 