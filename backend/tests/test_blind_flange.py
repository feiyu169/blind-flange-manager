"""盲板测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.user import User


@pytest.fixture
async def test_blind_flange(db: AsyncSession) -> BlindFlange:
    """创建测试盲板"""
    blind_flange = BlindFlange(
        code="BF-001",
        name="测试盲板",
        specification="DN100",
        material="碳钢",
        pressure_rating="PN16",
        size="100mm",
        location="车间A-管道1",
        pipeline_no="P-001",
        flange_no="F-001",
        status="in_stock",
    )
    db.add(blind_flange)
    await db.commit()
    await db.refresh(blind_flange)
    return blind_flange


async def test_create_blind_flange(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试创建盲板"""
    response = await client.post(
        "/api/v1/blind-flanges",
        json={
            "code": "BF-NEW",
            "name": "新盲板",
            "specification": "DN200",
            "material": "不锈钢",
            "status": "in_stock",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "BF-NEW"
    assert data["name"] == "新盲板"


async def test_create_blind_flange_duplicate(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试创建重复编码的盲板"""
    response = await client.post(
        "/api/v1/blind-flanges",
        json={
            "code": "BF-001",
            "name": "重复盲板",
            "status": "in_stock",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_list_blind_flanges(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试获取盲板列表"""
    response = await client.get("/api/v1/blind-flanges", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


async def test_list_blind_flanges_with_filter(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试筛选盲板列表"""
    response = await client.get(
        "/api/v1/blind-flanges",
        params={"status": "in_stock", "keyword": "测试"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


async def test_get_blind_flange(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试获取盲板详情"""
    response = await client.get(
        f"/api/v1/blind-flanges/{test_blind_flange.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "BF-001"
    assert data["name"] == "测试盲板"


async def test_get_blind_flange_not_found(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试获取不存在的盲板"""
    response = await client.get("/api/v1/blind-flanges/999", headers=auth_headers)
    assert response.status_code == 404


async def test_update_blind_flange(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试更新盲板"""
    response = await client.put(
        f"/api/v1/blind-flanges/{test_blind_flange.id}",
        json={
            "name": "更新后的盲板",
            "location": "车间B-管道2",
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "更新后的盲板"
    assert data["location"] == "车间B-管道2"


async def test_update_blind_flange_status(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试更新盲板状态"""
    response = await client.put(
        f"/api/v1/blind-flanges/{test_blind_flange.id}",
        json={"status": "installed"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "installed"

    # 检查状态变更日志
    response = await client.get(
        f"/api/v1/blind-flanges/{test_blind_flange.id}/status-logs",
        headers=auth_headers,
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) >= 1


async def test_delete_blind_flange(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试删除盲板"""
    response = await client.delete(
        f"/api/v1/blind-flanges/{test_blind_flange.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204

    # 确认已删除
    response = await client.get(
        f"/api/v1/blind-flanges/{test_blind_flange.id}",
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_scan_blind_flange(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试扫码获取盲板信息"""
    response = await client.get(
        "/api/v1/scan/BF-001",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "BF-001"


async def test_scan_blind_flange_not_found(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试扫码不存在的盲板"""
    response = await client.get(
        "/api/v1/scan/NONEXIST",
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_get_qrcode(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试获取二维码"""
    response = await client.get(
        "/api/v1/scan/BF-001/qrcode",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
