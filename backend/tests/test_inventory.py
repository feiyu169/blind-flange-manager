"""库存测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.inventory import InventoryAlert
from app.models.user import User


@pytest.fixture
async def test_blind_flange(db: AsyncSession) -> BlindFlange:
    """创建测试盲板"""
    blind_flange = BlindFlange(
        code="BF-INV-001",
        name="库存测试盲板",
        specification="DN100",
        status="in_stock",
    )
    db.add(blind_flange)
    await db.commit()
    await db.refresh(blind_flange)
    return blind_flange


@pytest.fixture
async def test_alert(db: AsyncSession) -> InventoryAlert:
    """创建测试预警配置"""
    alert = InventoryAlert(
        blind_flange_type="DN100",
        min_stock=10,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


async def test_create_inventory_in(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试入库"""
    response = await client.post(
        "/api/v1/inventory",
        json={
            "blind_flange_id": test_blind_flange.id,
            "type": "in",
            "quantity": 100,
            "reason": "初始入库",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "in"
    assert data["quantity"] == 100


async def test_create_inventory_out(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试出库"""
    # 先入库
    await client.post(
        "/api/v1/inventory",
        json={
            "blind_flange_id": test_blind_flange.id,
            "type": "in",
            "quantity": 100,
            "reason": "初始入库",
        },
        headers=auth_headers,
    )

    # 出库
    response = await client.post(
        "/api/v1/inventory",
        json={
            "blind_flange_id": test_blind_flange.id,
            "type": "out",
            "quantity": 50,
            "reason": "领用",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "out"
    assert data["quantity"] == 50


async def test_create_inventory_out_insufficient(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试出库库存不足"""
    response = await client.post(
        "/api/v1/inventory",
        json={
            "blind_flange_id": test_blind_flange.id,
            "type": "out",
            "quantity": 100,
            "reason": "领用",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_list_inventory_records(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试获取库存记录列表"""
    # 先入库
    await client.post(
        "/api/v1/inventory",
        json={
            "blind_flange_id": test_blind_flange.id,
            "type": "in",
            "quantity": 100,
            "reason": "初始入库",
        },
        headers=auth_headers,
    )

    response = await client.get("/api/v1/inventory", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


async def test_get_inventory_summary(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试获取库存汇总"""
    # 先入库
    await client.post(
        "/api/v1/inventory",
        json={
            "blind_flange_id": test_blind_flange.id,
            "type": "in",
            "quantity": 100,
            "reason": "初始入库",
        },
        headers=auth_headers,
    )

    response = await client.get("/api/v1/inventory/summary", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1


async def test_create_inventory_alert(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试创建库存预警配置"""
    response = await client.post(
        "/api/v1/inventory/alert-config",
        json={
            "blind_flange_type": "DN200",
            "min_stock": 20,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["blind_flange_type"] == "DN200"
    assert data["min_stock"] == 20


async def test_list_inventory_alerts(client: AsyncClient, test_user: User, test_alert: InventoryAlert, auth_headers: dict):
    """测试获取预警配置列表"""
    response = await client.get("/api/v1/inventory/alert-config", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


async def test_update_inventory_alert(client: AsyncClient, test_user: User, test_alert: InventoryAlert, auth_headers: dict):
    """测试更新库存预警配置"""
    response = await client.put(
        f"/api/v1/inventory/alert-config/{test_alert.id}",
        json={"min_stock": 30},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["min_stock"] == 30
