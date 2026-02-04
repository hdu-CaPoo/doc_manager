from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from app.core.config import settings
from pathlib import Path

# 配置 ConnectionConfig
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    # 模板文件夹路径 (稍后我们会创建这个文件夹)
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "emailtpl",
)

fast_mail = FastMail(conf)


async def send_verification_email(email_to: EmailStr, code: str, type_str: str):
    """
    发送验证码邮件 (异步)
    """
    subject = ""
    if type_str == "register":
        subject = "【凌云文档】注册验证码"
    elif type_str == "reset":
        subject = "【凌云文档】重置密码验证码"

    # 定义邮件内容数据，传给模板
    template_body = {
        "code": code,
        "project_name": settings.PROJECT_NAME,
        "valid_minutes": 10,  # 假设有效期10分钟
    }

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=template_body,
        subtype=MessageType.html,
    )

    # 发送邮件，使用 verification.html 模板
    await fast_mail.send_message(message, template_name="verification.html")


async def send_notification_email(
    email_to: EmailStr, subject: str, title: str, content: str, link: str
):
    """
    通用通知邮件
    """
    template_body = {
        "title": title,  # 比如 "你的 Issue 被回复了"
        "content": content,  # 比如 "张三回复说：xxx"
        "link": link,  # 点击跳转的链接
        "project_name": settings.PROJECT_NAME,
    }

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        template_body=template_body,
        subtype=MessageType.html,
    )

    # 需要再做一个 notification.html 模板
    await fast_mail.send_message(message, template_name="notification.html")
