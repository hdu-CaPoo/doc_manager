# app/services/auth_service.py
from sqlalchemy.orm import Session
from app.crud.user import get_user_by_email, update_password, create_user, authenticate # 引用 Infra 层
from app.crud.vercode import verify_code # 引用 Infra 层

from app.schemas.user import UserCreate
# 即使是 update_password 这种看起来像 CRUD 的，如果包含加密逻辑，其实可以算 Service 或 Domain 逻辑
# 这里假设 update_password 只是纯 DB 操作，加密在 Service 做，或者 update_password 内部封装好了

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, email: str, password: str, verification_code: str):
        # 1. 验证验证码
        is_code_valid = verify_code(self.db, email, verification_code, "register")
        if not is_code_valid:
            raise ValueError("验证码无效或已过期") 
        
        # 2. 检查用户是否已存在
        user = get_user_by_email(self.db, email)
        if user:
            raise ValueError("该邮箱已被注册")
        
        # 3. 创建用户
        # 实例化 Pydantic 对象 ---
        user_in = UserCreate(
            email=email, 
            password=password, 
            verification_code=verification_code
        )
        
        new_user = create_user(self.db, user_in)
        return new_user
    

    def login(self, email: str, password: str):
        # 1. 验证用户
        user = get_user_by_email(self.db, email=email)
        if not user:
            raise ValueError("该邮箱未注册")
        
        # 2. 验证密码 (这里假设 authenticate 函数内部已经封装了密码验证逻辑)
        if not authenticate(self.db, email=email, password=password):
            raise ValueError("邮箱或密码错误")
        
        return user
    
    def reset_password(self, email: str, verification_code: str, new_password: str):
        # 步骤 1: 校验验证码 (业务规则)
        # 调用 Infra 层去查验证码是否有效
        is_code_valid = verify_code(self.db, email, verification_code, "reset")
        if not is_code_valid:
            # 抛出业务异常 (BaseException)，让上层捕获
            raise ValueError("验证码无效或已过期") 

        # 步骤 2: 检查用户是否存在 (业务规则)
        user = get_user_by_email(self.db, email)
        if not user:
            raise ValueError("该邮箱未注册")

        # 步骤 3: 执行更新 (业务行为)
        # update_password 内部可能包含了加密逻辑，或者在这里显式调用 hash_password
        updated_user = update_password(self.db, user, new_password)
        
        return updated_user