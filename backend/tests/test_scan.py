"""扫码服务测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.user import User


@pytest.fixture
async def test_blind_flange(db: AsyncSession) -> BlindFlange:
    """创建测试盲板"""
    blind_flange = BlindFlange(
        code="BF-SCAN-001",
        name="扫码测试盲板",
        status="in_stock",
    )
    db.add(blind_flange)
    await db.commit()
    await db.refresh(blind_flange)
    return blind_flange


async def test_scan_success(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试扫码成功"""
    response = await client.get(
        "/api/v1/scan/BF-SCAN-001",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "BF-SCAN-001"


async def test_scan_not_found(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试扫码不存在的盲板"""
    response = await client.get(
        "/api/v1/scan/NONEXIST",
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_get_qrcode(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试获取二维码"""
    response = await client.get(
        "/api/v1/scan/BF-SCAN-001/qrcode",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


async def test_scan_history(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试扫码历史"""
    # 先扫码
    await client.get(
        "/api/v1/scan/BF-SCAN-001",
        headers=auth_headers,
    )

    # 获取扫码历史
    response = await client.get(
        "/api/v1/scan/history",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["blind_flange_id"] == test_blind_flange.id
    assert data[0]["success"] == True


async def test_scan_history_not_found(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试扫码失败历史"""
    # 扫码不存在的盲板
    await client.get(
        "/api/v1/scan/NONEXIST",
        headers=auth_headers,
    )

    # 获取扫码历史
    response = await client.get(
        "/api/v1/scan/history",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["success"] == False
    assert data[0]["error_message"] is not None
