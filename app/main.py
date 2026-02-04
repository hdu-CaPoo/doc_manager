from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles

from app.api import (
    auth,
    projects,
    documents,
    member,
    issues,
    utils,
    users,
)  # <--- 导入 documents 和 member


from fastapi.middleware.cors import CORSMiddleware  # 导入 CORS 中间件

import os

app = FastAPI(title="凌云文档管理系统")

# 允许所有来源访问（开发阶段比较方便）
# 生产环境建议把 allow_origins 改为具体的 ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许的前端域名/IP
    allow_credentials=True,  # 允许携带 Cookie/凭证
    allow_methods=["*"],  # 允许的方法 (GET, POST, PUT, DELETE...)
    allow_headers=["*"],  # 允许的请求头
)

# 注册路由
# prefix="/auth" 意味着这个文件里的接口都要加上 /auth 前缀
# tags=["认证"] 用于在 Swagger 文档里分类
app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(projects.router, prefix="/projects", tags=["项目管理"])
app.include_router(documents.router, tags=["文档管理"])  # prefix 用 /docs 比较短
app.include_router(member.router, prefix="/members", tags=["成员管理"])
app.include_router(
    issues.router, tags=["问题反馈"]
)  # 不加 prefix，因为你的路径里已经自带了 /projects/...
app.include_router(utils.router, prefix="/utils", tags=["工具接口"])
app.include_router(users.router, prefix="/users", tags=["用户管理"])


@app.get("/")
def read_root():
    return {"message": "欢迎使用凌云文档管理系统 API"}


# ==========================================
# 修复：使用绝对路径挂载
# ==========================================

# 1. 获取当前项目根目录的绝对路径
# __file__ 是 app/main.py
# dirname 是 app/
# 再 dirname 一次就是项目的根目录 doc_manager/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. 拼接出 uploads 的绝对路径
# 结果应该是类似: C:\Users\15589\Desktop\doc_manager\uploads
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# 打印一下路径，方便我们在终端确认 (调试用)
print(f"DEBUG: 正在挂载静态目录 -> {UPLOAD_DIR}")

# 3. 确保目录存在
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 4. 挂载
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

# 如果直接运行该脚本
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
