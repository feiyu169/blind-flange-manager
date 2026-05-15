"""用户认证测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User


@pytest.fixture
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
    await db.flush()
    await db.refresh(user)
    return user


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    """创建管理员用户"""
    user = User(
        username="admin",
        password_hash=get_password_hash("adminpassword"),
        real_name="管理员",
        role="admin",
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def test_login_success(client: AsyncClient, test_user: User):
    """测试登录成功"""
    response = await client.post(
        "/api/v1/users/login",
        json={"username": "testuser", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testuser"


async def test_login_wrong_password(client: AsyncClient, test_user: User):
    """测试登录密码错误"""
    response = await client.post(
        "/api/v1/users/login",
        json={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_login_nonexistent_user(client: AsyncClient):
    """测试登录不存在的用户"""
    response = await client.post(
        "/api/v1/users/login",
        json={"username": "nonexistent", "password": "password"},
    )
    assert response.status_code == 401


async def test_get_me(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试获取当前用户信息"""
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "operator"


async def test_get_me_unauthorized(client: AsyncClient):
    """测试未认证获取用户信息"""
    response = await client.get("/api/v1/users/me")
    # HTTPBearer 在没有 token 时返回 403
    assert response.status_code in [401, 403]


async def test_update_me(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试更新当前用户信息"""
    response = await client.put(
        "/api/v1/users/me",
        json={"real_name": "新名字", "phone": "13900139000"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["real_name"] == "新名字"
    assert data["phone"] == "13900139000"


async def test_create_user_admin(client: AsyncClient, admin_user: User, admin_auth_headers: dict):
    """测试管理员创建用户"""
    response = await client.post(
        "/api/v1/users",
        json={
            "username": "newuser",
            "password": "newpassword",
            "real_name": "新用户",
            "role": "operator",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["role"] == "operator"


async def test_create_user_duplicate(client: AsyncClient, test_user: User, admin_auth_headers: dict):
    """测试创建重复用户名"""
    response = await client.post(
        "/api/v1/users",
        json={
            "username": "testuser",
            "password": "password",
            "real_name": "重复用户",
            "role": "operator",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 400


async def test_list_users_admin(client: AsyncClient, admin_user: User, admin_auth_headers: dict):
    """测试管理员获取用户列表"""
    response = await client.get("/api/v1/users", headers=admin_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


async def test_list_users_non_admin(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试非管理员获取用户列表"""
    response = await client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 403
