#JWT 相关的 Pydantic 模型
from pydantic import BaseModel
from typing import Optional

# 返回给前端的 Token 结构
class Token(BaseModel):
    access_token: str
    token_type: str

# 用于解析 Token 内部数据的结构
class TokenPayload(BaseModel):
    sub: Optional[str] = None # sub 通常存放 User ID