import os
from dotenv import load_dotenv
from pydantic import EmailStr

load_dotenv()

class Settings:
    PROJECT_NAME: str = "凌云文档管理系统"
    PROJECT_VERSION: str = "1.0.0"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")

    #JWT 相关配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key") # 最好从 env 读取
    ALGORITHM: str = "HS256" # 加密算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 # Token 有效期 30 分钟

    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: EmailStr = os.getenv("MAIL_FROM")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 465))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "DocSystem")


settings = Settings()