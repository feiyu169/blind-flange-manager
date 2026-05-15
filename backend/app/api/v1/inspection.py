"""巡检 API"""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.inspection import (
    DueInspectionListResponse,
    InspectionPlanCreate,
    InspectionPlanListResponse,
    InspectionPlanResponse,
    InspectionPlanUpdate,
    InspectionRecordCreate,
    InspectionRecordListResponse,
    InspectionRecordResponse,
)
from app.services.auth import get_current_user
from app.services.inspection import (
    create_inspection_plan,
    create_inspection_record,
    delete_inspection_plan,
    get_due_inspections,
    get_inspection_plan,
    get_inspection_record,
    list_inspection_plans,
    list_inspection_records,
    update_inspection_plan,
)

router = APIRouter()


# 巡检计划 API
@router.post("/plans", response_model=InspectionPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    data: InspectionPlanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建巡检计划"""
    plan = await create_inspection_plan(db, data)
    return InspectionPlanResponse.model_validate(plan)


@router.get("/plans", response_model=InspectionPlanListResponse)
async def list_plans(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取巡检计划列表"""
    result = await list_inspection_plans(db, page, page_size, is_active)
    return InspectionPlanListResponse(
        items=[InspectionPlanResponse.model_validate(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/plans/{plan_id}", response_model=InspectionPlanResponse)
async def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取巡检计划详情"""
    plan = await get_inspection_plan(db, plan_id)
    return InspectionPlanResponse.model_validate(plan)


@router.put("/plans/{plan_id}", response_model=InspectionPlanResponse)
async def update_plan(
    plan_id: int,
    data: InspectionPlanUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新巡检计划"""
    plan = await update_inspection_plan(db, plan_id, data)
    return InspectionPlanResponse.model_validate(plan)


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除巡检计划"""
    await delete_inspection_plan(db, plan_id)


@router.get("/plans/due/list", response_model=DueInspectionListResponse)
async def due_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取待巡检列表"""
    items = await get_due_inspections(db)
    return DueInspectionListResponse(
        items=items,
        total=len(items),
    )


# 巡检记录 API
@router.post("/records", response_model=InspectionRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    data: InspectionRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建巡检记录"""
    record = await create_inspection_record(db, data, current_user.id)
    return InspectionRecordResponse.model_validate(record)


@router.get("/records", response_model=InspectionRecordListResponse)
async def list_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    blind_flange_id: Optional[int] = Query(None, description="盲板 ID"),
    inspector_id: Optional[int] = Query(None, description="巡检人 ID"),
    status: Optional[str] = Query(None, description="巡检状态"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取巡检记录列表"""
    result = await list_inspection_records(db, page, page_size, blind_flange_id, inspector_id, status)
    return InspectionRecordListResponse(
        items=[InspectionRecordResponse.model_validate(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/records/{record_id}", response_model=InspectionRecordResponse)
async def get_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取巡检记录详情"""
    record = await get_inspection_record(db, record_id)
    return InspectionRecordResponse.model_validate(record)
