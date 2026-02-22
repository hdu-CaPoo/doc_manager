from sqlalchemy.orm import Session
from pydantic import EmailStr
from fastapi import BackgroundTasks

from app.crud.vercode import create_verification_code
from app.core.email import send_verification_email
from app.crud.user import get_user_by_email # 用来检查邮箱是否已注册

class VercodeService:
    def __init__(self, db: Session):
        self.db = db

    def send_verification_code(self, email: EmailStr, type_str: str, background_tasks: BackgroundTasks):
        # 1. 逻辑检查
        user = get_user_by_email(self.db, email)
        
        if type_str == "register":
            if user:
                raise ValueError("该邮箱已注册")
        elif type_str == "reset":
            if not user:
                raise ValueError("该邮箱未注册")
        else:
            raise ValueError("无效的类型")

        # 2. 生成验证码存入数据库
        code = create_verification_code(self.db, email, type_str)
        
        # 3. 发送邮件 (这里直接调用发送函数，实际项目中可以改成后台任务)
        background_tasks.add_task(send_verification_email, email, code, type_str)
        return {"msg": "验证码已发送，请检查邮箱"}