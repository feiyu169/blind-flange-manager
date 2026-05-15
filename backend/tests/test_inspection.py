"""巡检测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.inspection import InspectionPlan
from app.models.user import User


@pytest.fixture
async def test_blind_flange(db: AsyncSession) -> BlindFlange:
    """创建测试盲板"""
    blind_flange = BlindFlange(
        code="BF-INS-001",
        name="巡检测试盲板",
        status="installed",
    )
    db.add(blind_flange)
    await db.commit()
    await db.refresh(blind_flange)
    return blind_flange


@pytest.fixture
async def test_plan(db: AsyncSession, test_blind_flange: BlindFlange, test_user: User) -> InspectionPlan:
    """创建测试巡检计划"""
    plan = InspectionPlan(
        blind_flange_id=test_blind_flange.id,
        cycle_days=30,
        assigned_to=test_user.id,
        is_active=True,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


async def test_create_inspection_plan(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试创建巡检计划"""
    response = await client.post(
        "/api/v1/inspections/plans",
        json={
            "blind_flange_id": test_blind_flange.id,
            "cycle_days": 30,
            "assigned_to": test_user.id,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["cycle_days"] == 30
    assert data["is_active"] == True


async def test_create_inspection_plan_blind_flange_not_found(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试创建巡检计划 - 盲板不存在"""
    response = await client.post(
        "/api/v1/inspections/plans",
        json={
            "blind_flange_id": 999,
            "cycle_days": 30,
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_list_inspection_plans(client: AsyncClient, test_user: User, test_plan: InspectionPlan, auth_headers: dict):
    """测试获取巡检计划列表"""
    response = await client.get("/api/v1/inspections/plans", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


async def test_update_inspection_plan(client: AsyncClient, test_user: User, test_plan: InspectionPlan, auth_headers: dict):
    """测试更新巡检计划"""
    response = await client.put(
        f"/api/v1/inspections/plans/{test_plan.id}",
        json={"cycle_days": 60},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cycle_days"] == 60


async def test_delete_inspection_plan(client: AsyncClient, test_user: User, test_plan: InspectionPlan, auth_headers: dict):
    """测试删除巡检计划"""
    response = await client.delete(
        f"/api/v1/inspections/plans/{test_plan.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


async def test_get_due_inspections(client: AsyncClient, test_user: User, test_plan: InspectionPlan, auth_headers: dict):
    """测试获取待巡检列表"""
    response = await client.get("/api/v1/inspections/plans/due/list", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


async def test_create_inspection_record(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, test_plan: InspectionPlan, auth_headers: dict):
    """测试创建巡检记录"""
    response = await client.post(
        "/api/v1/inspections/records",
        json={
            "blind_flange_id": test_blind_flange.id,
            "inspection_plan_id": test_plan.id,
            "status": "normal",
            "notes": "巡检正常",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "normal"


async def test_list_inspection_records(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, test_plan: InspectionPlan, auth_headers: dict):
    """测试获取巡检记录列表"""
    # 先创建记录
    await client.post(
        "/api/v1/inspections/records",
        json={
            "blind_flange_id": test_blind_flange.id,
            "inspection_plan_id": test_plan.id,
            "status": "normal",
            "notes": "巡检正常",
        },
        headers=auth_headers,
    )

    response = await client.get("/api/v1/inspections/records", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
