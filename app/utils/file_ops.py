import os
import uuid
import shutil
import hashlib
from fastapi import UploadFile

# --- 修改这里：统一变量名为 UPLOAD_ROOT ---
UPLOAD_ROOT = "uploads" 
AVATAR_ROOT = "uploads/avatars"

# 确保根目录存在
# --- 修改这里：使用 UPLOAD_ROOT ---
if not os.path.exists(UPLOAD_ROOT):
    os.makedirs(UPLOAD_ROOT)

def save_upload_file(upload_file: UploadFile, project_id: int) -> str:
    """
    保存文件到：uploads/{project_id}/{uuid-filename}
    """
    # 1. 构建该项目的专属目录路径
    # 例如: uploads/1/
    # --- 这里就不会报错了 ---
    project_dir = os.path.join(UPLOAD_ROOT, str(project_id))
    
    # 2. 如果目录不存在，创建它
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    
    # 3. 生成唯一的文件名
    filename = upload_file.filename
    ext = os.path.splitext(filename)[1]
    # 如果文件没后缀，给个默认的（可选）
    if not ext:
        ext = ""
        
    unique_filename = f"{uuid.uuid4()}{ext}"
    
    # 4. 拼接最终的物理路径
    file_path = os.path.join(project_dir, unique_filename)
    
    # 5. 写入磁盘
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    return file_path

def get_file_summary(file_path: str, limit: int = 200) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read(limit)
            return content
    except Exception:
        return "无法读取摘要 (非文本文件或编码错误)"
    
def calculate_file_hash(file: UploadFile) -> str:
    """
    计算文件的 MD5 哈希值
    注意：读取完流之后，必须把指针重置回开头 (seek(0))，
    否则后面保存文件时会读不到内容。
    """
    hash_md5 = hashlib.md5()
    
    # 分块读取，防止大文件撑爆内存
    while chunk := file.file.read(4096):
        hash_md5.update(chunk)
    
    # 关键步骤：重置文件指针！
    file.file.seek(0)
    
    return hash_md5.hexdigest()


# 确保目录存在
if not os.path.exists(AVATAR_ROOT):
    os.makedirs(AVATAR_ROOT)

def save_avatar(upload_file: UploadFile, user_id: int) -> str:
    """
    保存头像：uploads/avatars/user_{id}.jpg
    策略：直接用 user_id 命名，这样用户多次上传会自动覆盖旧头像，节省空间。
    """
    # 1. 检查文件类型 (简单检查后缀)
    filename = upload_file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    # 只允许常见图片格式
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        raise ValueError("仅支持图片格式 (jpg, png, gif, webp)")
    
    # 2. 构建文件名: user_1.png
    unique_filename = f"user_{user_id}{ext}"
    file_path = os.path.join(AVATAR_ROOT, unique_filename)
    
    # 3. 写入磁盘
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    return f"/static/avatars/{unique_filename}"