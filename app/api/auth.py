from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut
from app.api.deps import get_db
from app.schemas.token import Token  # 导入 Token schema
from app.crud.user import (
    create_user,
    get_user_by_email,
    authenticate,
    update_password,
)  # 导入 authenticate
from app.crud.vercode import verify_code

from app.core.config import settings
from app.core.security import create_access_token
from app.api.deps import get_current_user

from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm  # 导入这个表单依赖

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # 验证验证码
    if not verify_code(db, user_in.email, user_in.verification_code, "register"):
        raise HTTPException(status_code=400, detail="验证码无效或已过期")

    # 1. 检查邮箱是否已经存在
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册",
        )

    # 2. 创建用户
    new_user = create_user(db, user=user_in)
    return new_user


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),  # 这是关键，它是表单格式
):
    """
    OAuth2 兼容的 token 登录接口，获取 access token
    """
    # 1. 验证用户 (注意：OAuth2 表单里 username 字段对应我们的 email)
    user = authenticate(db, email=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 如果验证通过，设置过期时间
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # 3. 生成 Token (把用户 ID 放入 Token)
    return {
        "access_token": create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


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
    reset_in: ResetPasswordSchema, db: Session = Depends(get_db)
):
    # 1. 核心逻辑：必须校验验证码
    # type="reset" 对应我们在发送验证码时填写的类型
    if not verify_code(db, reset_in.email, reset_in.verification_code, "reset"):
        raise HTTPException(status_code=400, detail="验证码无效或已过期")

    # 2. 查找用户
    user = get_user_by_email(db, reset_in.email)
    if not user:
        raise HTTPException(status_code=404, detail="该邮箱未注册")

    # 3. 更新密码
    update_password(db, user, reset_in.new_password)

    return {"msg": "密码重置成功，请使用新密码登录"}
