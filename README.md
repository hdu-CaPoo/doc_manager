# 凌云文档管理系统 (Lingyun Doc Manager)

一个基于 **FastAPI (后端)** 和 **Vue 3 + Vite (前端)** 构建的现代化文档管理与协作平台。

## 📖 项目简介

凌云文档管理系统旨在提供一个轻量级、高效的团队文档协作环境。支持多项目管理、文档在线编辑（Markdown）、团队成员权限控制以及问题追踪等功能。

## 🛠️ 技术栈

### 后端 (Backend)
- **核心框架**: [FastAPI](https://fastapi.tiangolo.com/) - 高性能 Python Web 框架
- **数据库 ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) - 强大的数据库工具包
- **数据迁移**: Alembic - 数据库版本控制
- **身份认证**: OAuth2 + JWT (Using `python-jose`)
- **邮件服务**: fastapi-mail - 用于发送验证码及通知
- **数据验证**: Pydantic

### 前端 (Frontend)
- **核心框架**: [Vue 3](https://vuejs.org/) (Composition API)
- **构建工具**: [Vite](https://vitejs.dev/)
- **UI 组件库**: [Element Plus](https://element-plus.org/)
- **状态管理**: [Pinia](https://pinia.vuejs.org/)
- **路由管理**: Vue Router
- **HTTP 客户端**: Axios
- **Markdown 编辑器**: [Vditor](https://gh.qssn70.cn/Vanessa219/vditor) - 所见即所得 Markdown 编辑器

## ✨ 主要功能

- **用户系统**
  - 用户注册与登录 (JWT 认证)
  - 邮箱验证码校验
  - 密码重置功能
  - 个人资料及头像管理 (支持文件上传)

- **项目管理**
  - 创建与管理多个项目
  - 项目分类与检索

- **文档协作**
  - 在线 Markdown 编辑与预览
  - 文档的增删改查
  - 实时保存与版本管理 (根据实现情况)

- **团队协作**
  - 团队成员邀请与管理
  - 细粒度的权限控制 (待完善)

- **问题追踪 (Issue Tracking)**
  - 项目内问题/Bug 反馈
  - 问题状态流转与管理

## 📂 目录结构

```
doc_manager/
├── alembic/              # 数据库迁移脚本
├── app/                  # 后端应用源码
│   ├── api/              # API 路由定义
│   ├── core/             # 核心配置 (Config, Security, Email)
│   ├── crud/             # 数据库 CRUD 操作
│   ├── db/               # 数据库连接与会话
│   ├── emailtpl/         # 邮件模板 (HTML)
│   ├── models/           # SQLAlchemy 数据模型
│   ├── schemas/          # Pydantic 数据模式
│   ├── service/          # 业务逻辑层
│   └── main.py           # 后端入口文件
├── doc_frontend/         # 前端应用源码
│   ├── src/              # Vue 源代码
│   ├── public/           # 静态资源
│   └── vite.config.js    # Vite 配置文件
├── uploads/              # 用户上传文件存储目录
├── .env                  # 环境变量配置文件 (需自行创建)
└── requirements.txt      # 后端依赖列表
```

## 🚀 快速开始

### 前置要求
- Python 3.10+
- Node.js 18+ & npm/yarn/pnpm
- PostgreSQL 或 MySQL (或其他 SQLAlchemy 支持的数据库)

### 1. 后端设置 (Backend Setup)

1.  **进入项目根目录 (如果是在 doc_manager 下)**
    ```bash
    cd doc_manager
    ```

2.  **创建虚拟环境并激活**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/macOS
    source venv/bin/activate
    ```

3.  **安装依赖**
    ```bash
    pip install -r app/requirements.txt
    ```

4.  **配置环境变量**
    在根目录下创建一个 `.env` 文件，参照以下格式填入你的配置：
    ```env
    # 数据库配置 (示例为 SQLite，生产环境建议使用 PostgreSQL/MySQL)
    DATABASE_URL=sqlite:///./sql_app.db
    # 或者: postgresql://user:password@localhost/dbname

    # 安全配置 (生成一个强随机字符串)
    SECRET_KEY=your_super_secret_key_here
    
    # 邮件服务配置 (用于发送验证码)
    MAIL_USERNAME=your_email@example.com
    MAIL_PASSWORD=your_email_password
    MAIL_FROM=your_email@example.com
    MAIL_PORT=465
    MAIL_SERVER=smtp.example.com
    MAIL_FROM_NAME=凌云文档系统
    ```

5.  **运行数据库迁移**
    ```bash
    alembic upgrade head
    ```

6.  **启动后端服务器**
    ```bash
    uvicorn app.main:app --reload
    ```
    后端 API 将运行在 `http://127.0.0.1:8000`。
    API 文档地址: `http://127.0.0.1:8000/docs`

### 2. 前端设置 (Frontend Setup)

1.  **进入前端目录**
    ```bash
    cd doc_frontend
    ```

2.  **安装依赖**
    ```bash
    npm install
    ```

3.  **启动开发服务器**
    ```bash
    npm run dev
    ```
    前端应用将运行在 `http://localhost:5173`。

## ⚠️ 注意事项

- **跨域配置 (CORS)**: 后端 `app/main.py` 中默认配置了允许所有来源 (`allow_origins=["*"]`) 以方便开发。生产环境部署时，请务必将其修改为前端的实际域名。
- **uploads 目录**: 确保项目根目录下的 `uploads` 文件夹存在且有写入权限，用于存储用户上传的头像等文件。

## 📄 许可证

[MIT License](LICENSE)
