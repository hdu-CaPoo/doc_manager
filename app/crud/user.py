# 用户相关的CRUD操作 负责与数据库交互
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

from app.core.security import verify_password


# 通过邮箱查找用户（用于检查邮箱是否已被注册）
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# 创建新用户
def create_user(db: Session, user: UserCreate):
    # 1. 把明文密码加密
    hashed_password = get_password_hash(user.password)

    # 2. 创建数据库模型实例
    db_user = User(
        email=user.email, hashed_password=hashed_password, nickname=user.nickname
    )

    # 3. 添加到会话并提交
    db.add(db_user)
    db.commit()

    # 4. 刷新实例（为了获取数据库自动生成的 id 和 created_at）
    db.refresh(db_user)
    return db_user


def authenticate(db: Session, email: str, password: str):
    # 1. 先查有没有这个邮箱
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    # 2. 再查密码对不对
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_password(db: Session, db_user: User, new_password: str):
    # 这一步非常重要：必须加密！
    hashed_password = get_password_hash(new_password)
    db_user.hashed_password = hashed_password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_avatar(db: Session, db_user: User, avatar_path: str):
    db_user.avatar_url = avatar_path
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
