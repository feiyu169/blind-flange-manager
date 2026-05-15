"""库存服务"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.inventory import InventoryAlert, InventoryRecord
from app.schemas.inventory import (
    InventoryAlertCreate,
    InventoryAlertUpdate,
    InventoryRecordCreate,
)


async def create_inventory_record(
    db: AsyncSession,
    data: InventoryRecordCreate,
    operator_id: int,
) -> InventoryRecord:
    """创建库存记录"""
    # 检查盲板是否存在
    result = await db.execute(select(BlindFlange).where(BlindFlange.id == data.blind_flange_id))
    blind_flange = result.scalar_one_or_none()
    if not blind_flange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="盲板不存在",
        )

    # 检查出库时库存是否充足
    if data.type == "out":
        current_stock = await get_current_stock(db, data.blind_flange_id)
        if current_stock < data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"库存不足，当前库存: {current_stock}",
            )

    record = InventoryRecord(
        blind_flange_id=data.blind_flange_id,
        type=data.type,
        quantity=data.quantity,
        reason=data.reason,
        operator_id=operator_id,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_current_stock(
    db: AsyncSession,
    blind_flange_id: int,
) -> int:
    """获取当前库存 - 优化：合并为单个聚合查询"""
    result = await db.execute(
        select(
            func.coalesce(
                func.sum(
                    case(
                        (InventoryRecord.type == "in", InventoryRecord.quantity),
                        (InventoryRecord.type == "adjust", InventoryRecord.quantity),
                        else_=-InventoryRecord.quantity,
                    )
                ),
                0,
            )
        ).where(InventoryRecord.blind_flange_id == blind_flange_id)
    )
    return result.scalar()


async def get_batch_stock(
    db: AsyncSession,
    blind_flange_ids: List[int],
) -> dict:
    """批量获取库存 - 优化：单个查询获取多个盲板的库存"""
    if not blind_flange_ids:
        return {}

    result = await db.execute(
        select(
            InventoryRecord.blind_flange_id,
            func.coalesce(
                func.sum(
                    case(
                        (InventoryRecord.type == "in", InventoryRecord.quantity),
                        (InventoryRecord.type == "adjust", InventoryRecord.quantity),
                        else_=-InventoryRecord.quantity,
                    )
                ),
                0,
            ).label("stock"),
        )
        .where(InventoryRecord.blind_flange_id.in_(blind_flange_ids))
        .group_by(InventoryRecord.blind_flange_id)
    )
    return {row.blind_flange_id: row.stock for row in result.all()}


async def list_inventory_records(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    blind_flange_id: Optional[int] = None,
    type: Optional[str] = None,
) -> dict:
    """获取库存记录列表"""
    query = select(InventoryRecord)

    # 盲板筛选
    if blind_flange_id:
        query = query.where(InventoryRecord.blind_flange_id == blind_flange_id)

    # 类型筛选
    if type:
        query = query.where(InventoryRecord.type == type)

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页查询
    query = query.order_by(InventoryRecord.id.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_inventory_summary(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
) -> dict:
    """获取库存汇总 - 优化：使用批量查询"""
    # 获取所有盲板
    query = select(BlindFlange)
    if keyword:
        query = query.where(
            BlindFlange.code.ilike(f"%{keyword}%")
            | BlindFlange.name.ilike(f"%{keyword}%")
        )

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页查询
    query = query.order_by(BlindFlange.id)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    blind_flanges = result.scalars().all()

    # 批量获取库存
    blind_flange_ids = [bf.id for bf in blind_flanges]
    stock_map = await get_batch_stock(db, blind_flange_ids)

    # 获取预警配置
    alert_result = await db.execute(select(InventoryAlert))
    alerts = {alert.blind_flange_type: alert.min_stock for alert in alert_result.scalars().all()}

    items = []
    for bf in blind_flanges:
        current_stock = stock_map.get(bf.id, 0)
        alert_threshold = alerts.get(bf.specification)

        items.append({
            "blind_flange_id": bf.id,
            "blind_flange_code": bf.code,
            "blind_flange_name": bf.name,
            "total_in": 0,  # 简化，实际需要单独计算
            "total_out": 0,  # 简化，实际需要单独计算
            "current_stock": current_stock,
            "alert_threshold": alert_threshold,
            "is_alert": alert_threshold is not None and current_stock < alert_threshold,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def get_inventory_alerts(
    db: AsyncSession,
) -> List[dict]:
    """获取库存预警 - 优化：使用批量查询"""
    # 获取预警配置
    alert_result = await db.execute(select(InventoryAlert))
    alerts = alert_result.scalars().all()

    if not alerts:
        return []

    # 获取所有有预警配置的盲板类型
    alert_types = [alert.blind_flange_type for alert in alerts]
    alert_map = {alert.blind_flange_type: alert.min_stock for alert in alerts}

    # 批量获取这些类型的盲板
    blind_flange_result = await db.execute(
        select(BlindFlange)
        .where(BlindFlange.specification.in_(alert_types))
    )
    blind_flanges = blind_flange_result.scalars().all()

    if not blind_flanges:
        return []

    # 批量获取库存
    blind_flange_ids = [bf.id for bf in blind_flanges]
    stock_map = await get_batch_stock(db, blind_flange_ids)

    alert_items = []
    for bf in blind_flanges:
        current_stock = stock_map.get(bf.id, 0)
        min_stock = alert_map.get(bf.specification, 0)

        if current_stock < min_stock:
            alert_items.append({
                "blind_flange_id": bf.id,
                "blind_flange_code": bf.code,
                "blind_flange_name": bf.name,
                "current_stock": current_stock,
                "min_stock": min_stock,
                "alert_type": "low_stock",
            })

    return alert_items


async def create_inventory_alert(
    db: AsyncSession,
    data: InventoryAlertCreate,
) -> InventoryAlert:
    """创建库存预警配置"""
    # 检查是否已存在
    result = await db.execute(
        select(InventoryAlert)
        .where(InventoryAlert.blind_flange_type == data.blind_flange_type)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"盲板类型 {data.blind_flange_type} 的预警配置已存在",
        )

    alert = InventoryAlert(**data.model_dump())
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


async def update_inventory_alert(
    db: AsyncSession,
    alert_id: int,
    data: InventoryAlertUpdate,
) -> InventoryAlert:
    """更新库存预警配置"""
    result = await db.execute(select(InventoryAlert).where(InventoryAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预警配置不存在",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(alert, key, value)

    await db.flush()
    await db.refresh(alert)
    return alert


async def list_inventory_alerts(
    db: AsyncSession,
) -> List[InventoryAlert]:
    """获取预警配置列表"""
    result = await db.execute(select(InventoryAlert))
    return result.scalars().all()
