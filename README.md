# 凌云文档管理系统 (LingYun Document Management System)

凌云文档管理系统是一个基于 **FastAPI** 和 **Vue 3** 构建的现代化、全栈式技术文档管理平台。它旨在为团队提供安全、高效的文档存储、在线协作、问题追踪及精细化的权限管理功能。

![项目展示图](<img width="2804" height="1360" alt="image" src="https://github.com/user-attachments/assets/41d9d22d-52bc-465b-8101-7ff6bddb0e73" />) <!-- 你可以在这里放一张展示页或后台的截图 -->

## ✨ 核心特性

*   **📚 文档管理**：支持 Markdown 文件的上传、下载、在线编辑与实时预览。
*   **👥 团队协作**：完善的 RBAC 权限控制（拥有者/管理员/成员），支持邀请码加入、成员管理及权限变更。
*   **🔒 安全可靠**：基于 JWT 的用户认证，支持注册验证码、密码找回及强制重置密码。
*   **💬 问题追踪**：内置 Issue 系统，支持提出问题、评论回复及状态管理，促进团队沟通。
*   **🗑️ 回收站机制**：文档软删除与恢复功能，防止误删，支持彻底删除。
*   **📧 邮件通知**：集成邮件服务，支持注册验证、密码重置及 Issue 状态变更通知。
*   **👤 个人中心**：支持用户头像上传与个人信息展示。

## 🛠️ 技术栈

### 后端 (Backend)
*   **框架**: FastAPI (Python)
*   **数据库**: PostgreSQL + SQLAlchemy (ORM)
*   **迁移工具**: Alembic
*   **认证**: OAuth2 + JWT (python-jose)
*   **邮件**: fastapi-mail

### 前端 (Frontend)
*   **框架**: Vue 3 + Vite
*   **UI 组件库**: Element Plus
*   **状态管理**: Pinia
*   **路由**: Vue Router
*   **HTTP 请求**: Axios
*   **Markdown 编辑**: Vditor / Marked.js

## 🚀 快速开始

### 环境要求
*   Python 3.9+
*   Node.js 16+
*   PostgreSQL

### 1. 后端部署

```bash
# 克隆仓库
git clone https://github.com/hdu-capoo.me/doc_manager.git
cd doc_manager

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量 (参考 .env.example)
cp .env.example .env
# 编辑 .env 文件，填入数据库和邮件配置

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload

### 2. 前端部署

```bash
cd doc_frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

### 3. 访问应用
前端地址: http://localhost:5173
后端 API 文档: http://localhost:8000/docs


### 项目结构
.
├── app/                # 后端核心代码
│   ├── api/            # API 路由接口
│   ├── core/           # 核心配置 (Config, Security, Email)
│   ├── crud/           # 数据库 CRUD 操作
│   ├── models/         # SQLAlchemy 数据模型
│   ├── schemas/        # Pydantic 数据验证模型
│   └── utils/          # 工具函数
├── doc_frontend/       # 前端 Vue 项目
│   ├── src/
│   │   ├── views/      # 页面组件
│   │   ├── components/ # 公共组件
│   │   └── utils/      # 请求封装等
├── alembic/            # 数据库迁移脚本
└── uploads/            # 静态文件存储 (文档/头像)
