"""测试配置"""

import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.user import User

# 测试数据库 URL（使用 SQLite 内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 创建测试引擎
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

# 创建测试会话工厂
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """设置测试数据库"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """获取测试数据库会话"""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """获取测试客户端"""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    """创建测试用户"""
    user = User(
        username="testuser",
        password_hash=get_password_hash("testpassword"),
        real_name="测试用户",
        role="operator",
        phone="13800138000",
        email="test@example.com",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession) -> User:
    """创建管理员用户"""
    user = User(
        username="admin",
        password_hash=get_password_hash("adminpassword"),
        real_name="管理员",
        role="admin",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """获取认证 headers"""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(admin_user: User) -> dict:
    """获取管理员认证 headers"""
    token = create_access_token(data={"sub": str(admin_user.id)})
    return {"Authorization": f"Bearer {token}"}
