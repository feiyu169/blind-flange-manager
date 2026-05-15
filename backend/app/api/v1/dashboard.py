"""仪表盘 API"""

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.services.auth import get_current_user
from app.services.dashboard import get_dashboard_overview, get_recent_activities

router = APIRouter()


@router.get("/overview")
async def overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取仪表盘概览"""
    data = await get_dashboard_overview(db)
    return data


@router.get("/recent-activities")
async def recent_activities(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取最近操作记录"""
    activities = await get_recent_activities(db, limit)
    return {"items": activities, "total": len(activities)}
