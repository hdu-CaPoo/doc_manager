from fastapi import APIRouter, Depends
from fastapi import UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserOut
from app.service.user_service import UserService

router = APIRouter()

# 定义请求体：只需要新密码
class AdminResetPassword(BaseModel):
    new_password: str # 限制一下长度比如 min_length=6

@router.put("/{user_id}/reset-password")
def reset_password_by_admin(
    user_id: int,
    password_in: AdminResetPassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    return user_service.reset_password_by_admin(
        user_id=user_id,
        new_password=password_in.new_password,
        current_user=current_user
    )

@router.post("/me/avatar", response_model=UserOut)
def upload_my_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_service = UserService(db)
    return user_service.upload_my_avatar(file=file, current_user=current_user)