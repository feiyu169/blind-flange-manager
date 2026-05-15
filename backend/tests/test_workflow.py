"""流程测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.user import User
from app.models.workflow import Workflow


@pytest.fixture
async def test_blind_flange(db: AsyncSession) -> BlindFlange:
    """创建测试盲板"""
    blind_flange = BlindFlange(
        code="BF-WF-001",
        name="流程测试盲板",
        status="in_stock",
    )
    db.add(blind_flange)
    await db.commit()
    await db.refresh(blind_flange)
    return blind_flange


@pytest.fixture
async def test_workflow(db: AsyncSession, test_blind_flange: BlindFlange, test_user: User) -> Workflow:
    """创建测试流程"""
    workflow = Workflow(
        type="install",
        blind_flange_id=test_blind_flange.id,
        applicant_id=test_user.id,
        status="pending",
        notes="测试流程",
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)
    return workflow


async def test_create_workflow(client: AsyncClient, test_user: User, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试创建流程"""
    response = await client.post(
        "/api/v1/workflows",
        json={
            "type": "install",
            "blind_flange_id": test_blind_flange.id,
            "notes": "安装流程",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "install"
    assert data["status"] == "pending"


async def test_create_workflow_blind_flange_not_found(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试创建流程 - 盲板不存在"""
    response = await client.post(
        "/api/v1/workflows",
        json={
            "type": "install",
            "blind_flange_id": 999,
            "notes": "安装流程",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404


async def test_create_workflow_duplicate(client: AsyncClient, test_user: User, test_workflow: Workflow, test_blind_flange: BlindFlange, auth_headers: dict):
    """测试创建流程 - 重复创建"""
    response = await client.post(
        "/api/v1/workflows",
        json={
            "type": "uninstall",
            "blind_flange_id": test_blind_flange.id,
            "notes": "重复流程",
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_list_workflows(client: AsyncClient, test_user: User, test_workflow: Workflow, auth_headers: dict):
    """测试获取流程列表"""
    response = await client.get("/api/v1/workflows", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


async def test_get_workflow(client: AsyncClient, test_user: User, test_workflow: Workflow, auth_headers: dict):
    """测试获取流程详情"""
    response = await client.get(
        f"/api/v1/workflows/{test_workflow.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "install"
    assert data["status"] == "pending"


async def test_approve_workflow(client: AsyncClient, admin_user: User, test_workflow: Workflow, admin_auth_headers: dict):
    """测试审批流程"""
    response = await client.put(
        f"/api/v1/workflows/{test_workflow.id}/approve",
        json={
            "approved": True,
            "notes": "审批通过",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "approved"


async def test_reject_workflow(client: AsyncClient, admin_user: User, test_workflow: Workflow, admin_auth_headers: dict):
    """测试驳回流程"""
    response = await client.put(
        f"/api/v1/workflows/{test_workflow.id}/approve",
        json={
            "approved": False,
            "notes": "审批驳回",
        },
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "rejected"


async def test_start_workflow(client: AsyncClient, test_user: User, test_workflow: Workflow, admin_user: User, admin_auth_headers: dict, auth_headers: dict):
    """测试开始执行流程"""
    # 先审批
    await client.put(
        f"/api/v1/workflows/{test_workflow.id}/approve",
        json={"approved": True, "notes": "审批通过"},
        headers=admin_auth_headers,
    )

    # 开始执行
    response = await client.put(
        f"/api/v1/workflows/{test_workflow.id}/start",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"


async def test_complete_workflow(client: AsyncClient, test_user: User, test_workflow: Workflow, admin_user: User, admin_auth_headers: dict, auth_headers: dict):
    """测试完成流程"""
    # 先审批
    await client.put(
        f"/api/v1/workflows/{test_workflow.id}/approve",
        json={"approved": True, "notes": "审批通过"},
        headers=admin_auth_headers,
    )

    # 开始执行
    await client.put(
        f"/api/v1/workflows/{test_workflow.id}/start",
        headers=auth_headers,
    )

    # 完成流程
    response = await client.put(
        f"/api/v1/workflows/{test_workflow.id}/complete",
        json={"notes": "安装完成"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


async def test_cancel_workflow(client: AsyncClient, test_user: User, test_workflow: Workflow, auth_headers: dict):
    """测试取消流程"""
    response = await client.put(
        f"/api/v1/workflows/{test_workflow.id}/cancel",
        json={"reason": "取消原因"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


async def test_invalid_status_transition(client: AsyncClient, test_user: User, test_workflow: Workflow, auth_headers: dict):
    """测试无效状态转换"""
    # 尝试直接完成未审批的流程
    response = await client.put(
        f"/api/v1/workflows/{test_workflow.id}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 400


async def test_get_workflow_logs(client: AsyncClient, test_user: User, test_workflow: Workflow, auth_headers: dict):
    """测试获取流程日志"""
    # 先取消流程，产生日志
    await client.put(
        f"/api/v1/workflows/{test_workflow.id}/cancel",
        json={"reason": "测试取消"},
        headers=auth_headers,
    )

    response = await client.get(
        f"/api/v1/workflows/{test_workflow.id}/logs",
        headers=auth_headers,
    )
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) >= 1
