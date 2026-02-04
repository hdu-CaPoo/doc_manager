from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.crud.user import get_user_by_id, update_password
from pydantic import BaseModel, constr

from fastapi import UploadFile, File
from app.schemas.user import UserOut
from app.utils.file_ops import save_avatar
from app.crud.user import update_avatar

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
    """
    平台管理员强制重置用户密码
    """
    # 1. 权限检查：只有超级管理员 (superuser) 能做这个操作
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="权限不足，只有平台管理员可执行此操作")

    # 2. 检查目标用户是否存在
    target_user = get_user_by_id(db, user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 3. 强制更新密码 (无需验证码)
    update_password(db, target_user, password_in.new_password)

    return {"msg": f"用户 {target_user.nickname or target_user.email} 的密码已重置"}

@router.post("/me/avatar", response_model=UserOut)
def upload_my_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    用户上传/更新自己的头像
    """
    try:
        # 1. 保存文件到磁盘
        # 注意：这里我们捕获 ValueError，因为我们在 utils 里写了格式检查
        saved_path = save_avatar(file, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"头像上传失败: {str(e)}")

    # 2. 更新数据库
    updated_user = update_avatar(db, current_user, saved_path)
    
    return updated_user