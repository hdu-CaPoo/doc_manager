from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.user import User
from app.crud.user import get_user_by_id, update_password


from app.utils.file_ops import save_avatar
from app.crud.user import update_avatar

from app.core.exceptions import ResourceNotFound, PermissionDenied, InvalidFileError, InternalServerError


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def reset_password_by_admin(self, user_id: int, new_password: str, current_user: User):
        """
        平台管理员强制重置用户密码
        """
        # 1. 权限检查：只有超级管理员 (superuser) 能做这个操作
        if not current_user.is_superuser: #type: ignore
            raise PermissionDenied("权限不足，只有平台管理员可执行此操作")

        # 2. 检查目标用户是否存在
        target_user = get_user_by_id(self.db, user_id)
        if not target_user:
            raise ResourceNotFound("用户不存在")

        # 3. 强制更新密码 (无需验证码)
        update_password(self.db, target_user, new_password)

        return {"msg": f"用户 {target_user.nickname or target_user.email} 的密码已重置"}
    
    def upload_my_avatar(self, file: UploadFile, current_user: User):
        """
        用户上传/更新自己的头像
        """
        try:
            # 1. 保存文件到磁盘
            # 注意：这里我们捕获 ValueError，因为我们在 utils 里写了格式检查
            saved_path = save_avatar(file, user_id=current_user.id) #type: ignore
        except ValueError as e:
            raise InvalidFileError(str(e))
        except Exception as e:
            raise InternalServerError(f"头像上传失败: {str(e)}")

        # 2. 更新数据库中的 avatar_path 字段
        updated_user = update_avatar(self.db, current_user, saved_path)

        return updated_user