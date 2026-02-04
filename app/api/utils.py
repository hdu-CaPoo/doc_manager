from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import EmailStr, BaseModel

from app.api.deps import get_db
from app.crud.vercode import create_verification_code
from app.core.email import send_verification_email
from app.crud.user import get_user_by_email  # 用来检查邮箱是否已注册

router = APIRouter()


class EmailSchema(BaseModel):
    email: EmailStr
    type: str  # "register" or "reset"


@router.post("/send-verification-code")
async def send_code(
    email_in: EmailSchema,
    background_tasks: BackgroundTasks,  # 关键：后台任务
    db: Session = Depends(get_db),
):
    # 1. 逻辑检查
    user = get_user_by_email(db, email_in.email)

    if email_in.type == "register":
        if user:
            raise HTTPException(status_code=400, detail="该邮箱已注册")
    elif email_in.type == "reset":
        if not user:
            raise HTTPException(status_code=404, detail="该邮箱未注册")
    else:
        raise HTTPException(status_code=400, detail="无效的类型")

    # 2. 生成验证码存入数据库
    code = create_verification_code(db, email_in.email, email_in.type)

    # 3. 发送邮件 (使用后台任务，不阻塞接口响应)
    background_tasks.add_task(
        send_verification_email, email_in.email, code, email_in.type
    )

    return {"msg": "验证码已发送，请检查邮箱"}
