"""数据库初始化脚本 - 仅用于开发环境"""

import asyncio
import os

from app.core.database import Base, engine
from app.models import *  # noqa: F401, F403


async def init_db():
    """初始化数据库（创建表）"""
    print("正在创建数据库表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库表创建完成！")


if __name__ == "__main__":
    # 设置环境变量
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./blind_flange_manager.db")
    asyncio.run(init_db())
