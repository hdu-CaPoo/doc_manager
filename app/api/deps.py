from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User
from app.schemas.token import TokenPayload

# 1. 定义 OAuth2 的 Token 获取地址
# 这告诉 Swagger UI：如果需要 Token，去 "/auth/login" 这个接口拿
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/auth/login"
)

def get_db() -> Generator[Session, None, None]: 
    try:
        db = SessionLocal()
        yield db
    finally:
        db = SessionLocal()
        db.close()

# 2. 核心函数：获取当前登录用户
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(reusable_oauth2) # 依赖：从请求头自动提取 Token
) -> User:
    try:
        # 3. 解密 Token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        # 4. 检查 Token 里有没有 User ID (sub)
        if token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # 5. 根据 ID 去数据库查用户
    user = db.query(User).filter(User.id == int(token_data.sub)).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user