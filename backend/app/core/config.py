"""应用配置"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    APP_NAME: str = "盲板管理系统"
    DEBUG: bool = False

    # 数据库配置
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/blind_flange_manager"

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 配置 - 必须从环境变量读取，不提供默认值
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 小时

    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # 库存预警默认阈值
    DEFAULT_MIN_STOCK: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
