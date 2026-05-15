"""仪表盘测试"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def test_get_dashboard_overview(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试获取仪表盘概览"""
    response = await client.get("/api/v1/dashboard/overview", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "pending_workflows" in data
    assert "in_progress_workflows" in data
    assert "abnormal_blind_flanges" in data
    assert "low_stock_alerts" in data
    assert "due_inspections" in data
    assert "total_blind_flanges" in data
    assert "blind_flange_status_counts" in data


async def test_get_recent_activities(client: AsyncClient, test_user: User, auth_headers: dict):
    """测试获取最近操作记录"""
    response = await client.get("/api/v1/dashboard/recent-activities", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
