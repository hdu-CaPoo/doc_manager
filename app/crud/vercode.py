from sqlalchemy.orm import Session
from app.models.vercode import VerificationCode
from datetime import datetime, timedelta
import random


def create_verification_code(db: Session, email: str, type_str: str):
    # 1. 生成 6 位随机数字
    code = str(random.randint(100000, 999999))

    # 2. 设定期限 (比如 10 分钟后过期)
    expires_at = datetime.now() + timedelta(minutes=10)

    # 3. 如果该邮箱之前有未使用的同类型码，可以将它们设为已使用 (失效旧码)
    # db.query(VerificationCode).filter(...) ... (为了简单先省略)

    db_code = VerificationCode(
        email=email, code=code, type=type_str, expires_at=expires_at
    )
    db.add(db_code)
    db.commit()
    return code  # 返回生成的码用于发送邮件


def verify_code(db: Session, email: str, code: str, type_str: str):
    """
    验证代码是否有效
    """
    db_code = (
        db.query(VerificationCode)
        .filter(
            VerificationCode.email == email,
            VerificationCode.code == code,
            VerificationCode.type == type_str,
            VerificationCode.is_used == False,
            VerificationCode.expires_at > datetime.now(),  # 必须没过期
        )
        .first()
    )

    if db_code:
        # 验证成功后，标记为已使用
        db_code.is_used = True
        db.commit()
        return True
    return False
