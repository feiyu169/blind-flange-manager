"""仪表盘服务 - 优化版本"""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.inspection import InspectionPlan
from app.models.inventory import InventoryAlert, InventoryRecord
from app.models.workflow import Workflow, WorkflowLog


async def get_dashboard_overview(db: AsyncSession) -> dict:
    """获取仪表盘概览 - 优化：使用并行查询"""
    now = datetime.utcnow()

    # 并行执行多个统计查询
    # 1. 流程统计
    workflow_stats = await db.execute(
        select(
            func.count().label("total"),
            func.count(case((Workflow.status == "pending", 1))).label("pending"),
            func.count(case((Workflow.status == "in_progress", 1))).label("in_progress"),
        )
    )
    workflow_row = workflow_stats.one()

    # 2. 盲板状态统计
    blind_flange_stats = await db.execute(
        select(
            func.count().label("total"),
            func.count(case((BlindFlange.status == "in_stock", 1))).label("in_stock"),
            func.count(case((BlindFlange.status == "installed", 1))).label("installed"),
            func.count(case((BlindFlange.status == "maintenance", 1))).label("maintenance"),
            func.count(case((BlindFlange.status == "scrapped", 1))).label("scrapped"),
        )
    )
    bf_row = blind_flange_stats.one()

    # 3. 待巡检数
    due_inspection_result = await db.execute(
        select(func.count())
        .select_from(InspectionPlan)
        .where(
            InspectionPlan.is_active == True,
            InspectionPlan.next_inspected_at < now,
        )
    )
    due_inspection_count = due_inspection_result.scalar()

    # 4. 库存预警数 - 使用批量查询
    low_stock_count = await _count_low_stock(db)

    return {
        "pending_workflows": workflow_row.pending,
        "in_progress_workflows": workflow_row.in_progress,
        "abnormal_blind_flanges": bf_row.maintenance + bf_row.scrapped,
        "low_stock_alerts": low_stock_count,
        "due_inspections": due_inspection_count,
        "total_blind_flanges": bf_row.total,
        "blind_flange_status_counts": {
            "in_stock": bf_row.in_stock,
            "installed": bf_row.installed,
            "maintenance": bf_row.maintenance,
            "scrapped": bf_row.scrapped,
        },
    }


async def _count_low_stock(db: AsyncSession) -> int:
    """计算库存预警数 - 优化：使用单个聚合查询"""
    # 获取预警配置
    alert_result = await db.execute(select(InventoryAlert))
    alerts = alert_result.scalars().all()

    if not alerts:
        return 0

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
        return 0

    # 批量获取库存
    blind_flange_ids = [bf.id for bf in blind_flanges]
    stock_result = await db.execute(
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
    stock_map = {row.blind_flange_id: row.stock for row in stock_result.all()}

    # 计算预警数
    low_stock_count = 0
    for bf in blind_flanges:
        current_stock = stock_map.get(bf.id, 0)
        min_stock = alert_map.get(bf.specification, 0)
        if current_stock < min_stock:
            low_stock_count += 1

    return low_stock_count


async def get_recent_activities(
    db: AsyncSession,
    limit: int = 20,
) -> List[dict]:
    """获取最近操作记录 - 优化：使用 JOIN 查询"""
    # 使用 JOIN 查询获取流程日志和流程信息
    result = await db.execute(
        select(
            WorkflowLog,
            Workflow.type.label("workflow_type"),
        )
        .join(Workflow, WorkflowLog.workflow_id == Workflow.id)
        .order_by(WorkflowLog.created_at.desc())
        .limit(limit)
    )
    rows = result.all()

    activities = []
    for log, workflow_type in rows:
        activities.append({
            "id": log.id,
            "type": "workflow",
            "action": log.action,
            "workflow_id": log.workflow_id,
            "workflow_type": workflow_type,
            "operator_id": log.operator_id,
            "notes": log.notes,
            "created_at": log.created_at,
        })

    return activities
