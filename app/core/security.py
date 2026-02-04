# 处理密码加密和验证
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Any
from jose import jwt  # 注意这里导入的是 jose
from app.core.config import settings
from passlib.context import CryptContext


# 定义哈希算法，这里使用 bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 1. 验证密码：比较“用户输入的明文”和“数据库里的密文”是否匹配
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# 2. 加密密码：把“明文”变成“密文”
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# jJWT 相关的函数
def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    # 1. 设置过期时间
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # 2. 准备要加密的数据 (Payload)
    # sub (Subject) 是 JWT 标准字段，通常放用户唯一标识 (ID 或 Email)
    to_encode = {"exp": expire, "sub": str(subject)}

    # 3. 生成加密字符串
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
