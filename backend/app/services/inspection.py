"""巡检服务"""

from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.inspection import InspectionPlan, InspectionRecord
from app.schemas.inspection import (
    InspectionPlanCreate,
    InspectionPlanUpdate,
    InspectionRecordCreate,
)


async def create_inspection_plan(
    db: AsyncSession,
    data: InspectionPlanCreate,
) -> InspectionPlan:
    """创建巡检计划"""
    # 检查盲板是否存在
    result = await db.execute(select(BlindFlange).where(BlindFlange.id == data.blind_flange_id))
    blind_flange = result.scalar_one_or_none()
    if not blind_flange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="盲板不存在",
        )

    # 检查是否已有活跃的巡检计划
    result = await db.execute(
        select(InspectionPlan).where(
            InspectionPlan.blind_flange_id == data.blind_flange_id,
            InspectionPlan.is_active == True,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该盲板已有活跃的巡检计划",
        )

    plan = InspectionPlan(
        blind_flange_id=data.blind_flange_id,
        cycle_days=data.cycle_days,
        assigned_to=data.assigned_to,
        next_inspected_at=datetime.utcnow() + timedelta(days=data.cycle_days),
    )
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    return plan


async def get_inspection_plan(
    db: AsyncSession,
    plan_id: int,
) -> InspectionPlan:
    """获取巡检计划详情"""
    result = await db.execute(select(InspectionPlan).where(InspectionPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="巡检计划不存在",
        )
    return plan


async def list_inspection_plans(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    is_active: Optional[bool] = None,
) -> dict:
    """获取巡检计划列表"""
    query = select(InspectionPlan)

    # 状态筛选
    if is_active is not None:
        query = query.where(InspectionPlan.is_active == is_active)

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页查询
    query = query.order_by(InspectionPlan.id.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def update_inspection_plan(
    db: AsyncSession,
    plan_id: int,
    data: InspectionPlanUpdate,
) -> InspectionPlan:
    """更新巡检计划"""
    plan = await get_inspection_plan(db, plan_id)

    update_data = data.model_dump(exclude_unset=True)

    # 如果更新了周期，重新计算下次巡检时间
    if "cycle_days" in update_data and plan.last_inspected_at:
        plan.next_inspected_at = plan.last_inspected_at + timedelta(days=update_data["cycle_days"])

    for key, value in update_data.items():
        setattr(plan, key, value)

    await db.flush()
    await db.refresh(plan)
    return plan


async def delete_inspection_plan(
    db: AsyncSession,
    plan_id: int,
) -> None:
    """删除巡检计划"""
    plan = await get_inspection_plan(db, plan_id)
    await db.delete(plan)
    await db.flush()


async def get_due_inspections(
    db: AsyncSession,
) -> List[dict]:
    """获取待巡检列表"""
    now = datetime.utcnow()

    # 查询所有活跃的巡检计划
    result = await db.execute(
        select(InspectionPlan)
        .where(InspectionPlan.is_active == True)
        .order_by(InspectionPlan.next_inspected_at)
    )
    plans = result.scalars().all()

    due_items = []
    for plan in plans:
        # 获取盲板信息
        blind_flange_result = await db.execute(
            select(BlindFlange).where(BlindFlange.id == plan.blind_flange_id)
        )
        blind_flange = blind_flange_result.scalar_one_or_none()
        if not blind_flange:
            continue

        is_overdue = bool(plan.next_inspected_at and plan.next_inspected_at < now)

        due_items.append({
            "plan_id": plan.id,
            "blind_flange_id": plan.blind_flange_id,
            "blind_flange_code": blind_flange.code,
            "blind_flange_name": blind_flange.name,
            "cycle_days": plan.cycle_days,
            "last_inspected_at": plan.last_inspected_at,
            "next_inspected_at": plan.next_inspected_at,
            "assigned_to": plan.assigned_to,
            "is_overdue": is_overdue,
        })

    return due_items


async def create_inspection_record(
    db: AsyncSession,
    data: InspectionRecordCreate,
    inspector_id: int,
) -> InspectionRecord:
    """创建巡检记录"""
    # 检查盲板是否存在
    result = await db.execute(select(BlindFlange).where(BlindFlange.id == data.blind_flange_id))
    blind_flange = result.scalar_one_or_none()
    if not blind_flange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="盲板不存在",
        )

    record = InspectionRecord(
        blind_flange_id=data.blind_flange_id,
        inspection_plan_id=data.inspection_plan_id,
        inspector_id=inspector_id,
        status=data.status,
        images=data.images,
        notes=data.notes,
    )
    db.add(record)

    # 更新巡检计划的上次巡检时间和下次巡检时间
    if data.inspection_plan_id:
        plan_result = await db.execute(
            select(InspectionPlan).where(InspectionPlan.id == data.inspection_plan_id)
        )
        plan = plan_result.scalar_one_or_none()
        if plan:
            plan.last_inspected_at = datetime.utcnow()
            plan.next_inspected_at = datetime.utcnow() + timedelta(days=plan.cycle_days)

    await db.flush()
    await db.refresh(record)
    return record


async def get_inspection_record(
    db: AsyncSession,
    record_id: int,
) -> InspectionRecord:
    """获取巡检记录详情"""
    result = await db.execute(select(InspectionRecord).where(InspectionRecord.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="巡检记录不存在",
        )
    return record


async def list_inspection_records(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    blind_flange_id: Optional[int] = None,
    inspector_id: Optional[int] = None,
    status: Optional[str] = None,
) -> dict:
    """获取巡检记录列表"""
    query = select(InspectionRecord)

    # 盲板筛选
    if blind_flange_id:
        query = query.where(InspectionRecord.blind_flange_id == blind_flange_id)

    # 巡检人筛选
    if inspector_id:
        query = query.where(InspectionRecord.inspector_id == inspector_id)

    # 状态筛选
    if status:
        query = query.where(InspectionRecord.status == status)

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页查询
    query = query.order_by(InspectionRecord.id.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
