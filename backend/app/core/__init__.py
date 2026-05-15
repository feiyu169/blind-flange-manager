"""盲板管理系统 - 核心配置"""

from app.core.config import settings
from app.core.database import Base, engine, get_db, async_session_factory

__all__ = ["settings", "Base", "engine", "get_db", "async_session_factory"]
