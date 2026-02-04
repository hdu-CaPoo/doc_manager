from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 1. 基础信息
class DocumentBase(BaseModel):
    pass # 上传时主要靠 Form Data，这里暂时为空

# 2. 返回给前端的信息
class DocumentOut(DocumentBase):
    id: int
    original_filename: str
    # physical_path 绝对不要返回给前端！这是安全隐患。
    summary: Optional[str]
    size_bytes: int
    status: str
    created_at: datetime
    uploader_id: int
    project_id: int

    class Config:
        orm_mode = True