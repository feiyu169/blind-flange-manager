"""仪表盘服务"""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.inspection import InspectionPlan
from app.models.inventory import InventoryAlert, InventoryRecord
from app.models.workflow import Workflow, WorkflowLog


async def get_dashboard_overview(db: AsyncSession) -> dict:
    """获取仪表盘概览"""
    now = datetime.utcnow()

    # 待审批流程数
    pending_result = await db.execute(
        select(func.count())
        .select_from(Workflow)
        .where(Workflow.status == "pending")
    )
    pending_count = pending_result.scalar()

    # 进行中流程数
    in_progress_result = await db.execute(
        select(func.count())
        .select_from(Workflow)
        .where(Workflow.status == "in_progress")
    )
    in_progress_count = in_progress_result.scalar()

    # 异常盲板数（状态为 maintenance 或 scrapped）
    abnormal_result = await db.execute(
        select(func.count())
        .select_from(BlindFlange)
        .where(BlindFlange.status.in_(["maintenance", "scrapped"]))
    )
    abnormal_count = abnormal_result.scalar()

    # 库存预警数
    alert_result = await db.execute(select(InventoryAlert))
    alerts = alert_result.scalars().all()

    low_stock_count = 0
    for alert in alerts:
        # 获取该类型的所有盲板
        blind_flange_result = await db.execute(
            select(BlindFlange)
            .where(BlindFlange.specification == alert.blind_flange_type)
        )
        blind_flanges = blind_flange_result.scalars().all()

        for bf in blind_flanges:
            # 计算当前库存
            in_result = await db.execute(
                select(func.coalesce(func.sum(InventoryRecord.quantity), 0))
                .where(
                    InventoryRecord.blind_flange_id == bf.id,
                    InventoryRecord.type == "in",
                )
            )
            total_in = in_result.scalar()

            out_result = await db.execute(
                select(func.coalesce(func.sum(InventoryRecord.quantity), 0))
                .where(
                    InventoryRecord.blind_flange_id == bf.id,
                    InventoryRecord.type == "out",
                )
            )
            total_out = out_result.scalar()

            current_stock = total_in - total_out
            if current_stock < alert.min_stock:
                low_stock_count += 1

    # 待巡检数
    due_inspection_result = await db.execute(
        select(func.count())
        .select_from(InspectionPlan)
        .where(
            InspectionPlan.is_active == True,
            InspectionPlan.next_inspected_at < now,
        )
    )
    due_inspection_count = due_inspection_result.scalar()

    # 盲板总数
    total_blind_flange_result = await db.execute(
        select(func.count()).select_from(BlindFlange)
    )
    total_blind_flange = total_blind_flange_result.scalar()

    # 各状态盲板数
    status_counts = {}
    for status_val in ["in_stock", "installed", "maintenance", "scrapped"]:
        count_result = await db.execute(
            select(func.count())
            .select_from(BlindFlange)
            .where(BlindFlange.status == status_val)
        )
        status_counts[status_val] = count_result.scalar()

    return {
        "pending_workflows": pending_count,
        "in_progress_workflows": in_progress_count,
        "abnormal_blind_flanges": abnormal_count,
        "low_stock_alerts": low_stock_count,
        "due_inspections": due_inspection_count,
        "total_blind_flanges": total_blind_flange,
        "blind_flange_status_counts": status_counts,
    }


async def get_recent_activities(
    db: AsyncSession,
    limit: int = 20,
) -> List[dict]:
    """获取最近操作记录"""
    # 获取最近的流程日志
    result = await db.execute(
        select(WorkflowLog)
        .order_by(WorkflowLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()

    activities = []
    for log in logs:
        # 获取流程信息
        workflow_result = await db.execute(
            select(Workflow).where(Workflow.id == log.workflow_id)
        )
        workflow = workflow_result.scalar_one_or_none()

        activities.append({
            "id": log.id,
            "type": "workflow",
            "action": log.action,
            "workflow_id": log.workflow_id,
            "workflow_type": workflow.type if workflow else None,
            "operator_id": log.operator_id,
            "notes": log.notes,
            "created_at": log.created_at,
        })

    return activities
