from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import EmailStr, BaseModel

from app.api.deps import get_db
from app.service.vercode_service import VercodeService # 引入 Service 层

router = APIRouter()

class EmailSchema(BaseModel):
    email: EmailStr
    type: str # "register" or "reset"

@router.post("/send-verification-code")
async def send_code(
    email_in: EmailSchema,
    background_tasks: BackgroundTasks, # 必须在 API 参数里声明
    db: Session = Depends(get_db)
):
    try:
        vercode_service = VercodeService(db)
        # 把 background_tasks 传进去
        return vercode_service.send_verification_code(
            email=email_in.email, 
            type_str=email_in.type,
            background_tasks=background_tasks 
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))