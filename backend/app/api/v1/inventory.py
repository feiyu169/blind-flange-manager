"""库存 API"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.inventory import (
    InventoryAlertCreate,
    InventoryAlertListResponse,
    InventoryAlertResponse,
    InventoryAlertUpdate,
    InventoryRecordCreate,
    InventoryRecordListResponse,
    InventoryRecordResponse,
    InventorySummaryListResponse,
)
from app.services.auth import get_current_user
from app.services.inventory import (
    create_inventory_alert,
    create_inventory_record,
    get_inventory_alerts,
    get_inventory_summary,
    list_inventory_alerts,
    list_inventory_records,
    update_inventory_alert,
)

router = APIRouter()


@router.post("", response_model=InventoryRecordResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: InventoryRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建库存记录"""
    record = await create_inventory_record(db, data, current_user.id)
    return InventoryRecordResponse.model_validate(record)


@router.get("", response_model=InventoryRecordListResponse)
async def list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    blind_flange_id: Optional[int] = Query(None, description="盲板 ID"),
    type: Optional[str] = Query(None, description="操作类型"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取库存记录列表"""
    result = await list_inventory_records(db, page, page_size, blind_flange_id, type)
    return InventoryRecordListResponse(
        items=[InventoryRecordResponse.model_validate(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/summary", response_model=InventorySummaryListResponse)
async def summary(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取库存汇总"""
    result = await get_inventory_summary(db, page, page_size, keyword)
    return InventorySummaryListResponse(**result)


@router.get("/alerts")
async def alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取库存预警"""
    alert_items = await get_inventory_alerts(db)
    return {"items": alert_items, "total": len(alert_items)}


@router.post("/alert-config", response_model=InventoryAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    data: InventoryAlertCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建库存预警配置"""
    alert = await create_inventory_alert(db, data)
    return InventoryAlertResponse.model_validate(alert)


@router.put("/alert-config/{alert_id}", response_model=InventoryAlertResponse)
async def update_alert(
    alert_id: int,
    data: InventoryAlertUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新库存预警配置"""
    alert = await update_inventory_alert(db, alert_id, data)
    return InventoryAlertResponse.model_validate(alert)


@router.get("/alert-config", response_model=InventoryAlertListResponse)
async def list_alerts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取预警配置列表"""
    alerts = await list_inventory_alerts(db)
    return InventoryAlertListResponse(
        items=[InventoryAlertResponse.model_validate(alert) for alert in alerts],
        total=len(alerts),
    )
