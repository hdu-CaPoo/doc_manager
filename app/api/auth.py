from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token # 导入 Token schema
from app.core.config import settings
from app.core.security import create_access_token
from app.service.auth_service import AuthService # 引入 Service 层

from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm # 导入这个表单依赖

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    
    auth_service = AuthService(db)

    try:
        new_user = auth_service.register(
            email=user_in.email, 
            password=user_in.password, 
            verification_code=user_in.verification_code
        )
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends() # 这是关键，它是表单格式
):
    try:
        auth_service = AuthService(db)
        user = auth_service.login(email=form_data.username, password=form_data.password)
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        # 3. 生成 Token (把用户 ID 放入 Token)
        return {
            "access_token": create_access_token(
                subject=user.id, expires_delta=access_token_expires
            ),
            "token_type": "bearer",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserOut)
def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user

@router.get("/logout")
def logout():
    """
    注销接口（前端只需删除本地 Token 即可）
    """
    return {"msg": "Successfully logged out"}

class ResetPasswordSchema(BaseModel):
    email: EmailStr
    verification_code: str
    new_password: str

@router.post("/reset-password")
def reset_password_by_self(
    reset_in: ResetPasswordSchema,
    db: Session = Depends(get_db)
):
    try:
        auth_service = AuthService(db)
        auth_service.reset_password(
            email=reset_in.email,
            verification_code=reset_in.verification_code,
            new_password=reset_in.new_password
        )
        return {"msg": "密码重置成功，请使用新密码登录"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
