"""流程服务"""

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blind_flange import BlindFlange
from app.models.workflow import Workflow, WorkflowLog
from app.schemas.workflow import (
    WorkflowApprove,
    WorkflowCancel,
    WorkflowCreate,
)

# 流程状态机
VALID_TRANSITIONS = {
    "pending": ["approved", "rejected", "cancelled"],
    "approved": ["in_progress", "cancelled"],
    "in_progress": ["completed", "cancelled"],
    "completed": [],
    "rejected": [],
    "cancelled": [],
}


def validate_status_transition(current_status: str, new_status: str) -> bool:
    """验证状态转换是否合法"""
    return new_status in VALID_TRANSITIONS.get(current_status, [])


async def create_workflow(
    db: AsyncSession,
    data: WorkflowCreate,
    applicant_id: int,
) -> Workflow:
    """创建流程"""
    # 检查盲板是否存在
    result = await db.execute(select(BlindFlange).where(BlindFlange.id == data.blind_flange_id))
    blind_flange = result.scalar_one_or_none()
    if not blind_flange:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="盲板不存在",
        )

    # 检查是否有未完成的流程
    result = await db.execute(
        select(Workflow).where(
            Workflow.blind_flange_id == data.blind_flange_id,
            Workflow.status.in_(["pending", "approved", "in_progress"]),
        )
    )
    existing_workflow = result.scalar_one_or_none()
    if existing_workflow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该盲板已有未完成的流程 (ID: {existing_workflow.id})",
        )

    workflow = Workflow(
        type=data.type,
        blind_flange_id=data.blind_flange_id,
        applicant_id=applicant_id,
        notes=data.notes,
    )
    db.add(workflow)
    await db.flush()

    # 记录日志
    log = WorkflowLog(
        workflow_id=workflow.id,
        action="apply",
        operator_id=applicant_id,
        notes=data.notes,
    )
    db.add(log)
    await db.flush()

    await db.refresh(workflow)
    return workflow


async def get_workflow(
    db: AsyncSession,
    workflow_id: int,
) -> Workflow:
    """获取流程详情"""
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="流程不存在",
        )
    return workflow


async def list_workflows(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    type: Optional[str] = None,
    status: Optional[str] = None,
    applicant_id: Optional[int] = None,
) -> dict:
    """获取流程列表"""
    query = select(Workflow)

    # 类型筛选
    if type:
        query = query.where(Workflow.type == type)

    # 状态筛选
    if status:
        query = query.where(Workflow.status == status)

    # 申请人筛选
    if applicant_id:
        query = query.where(Workflow.applicant_id == applicant_id)

    # 计算总数
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 分页查询
    query = query.order_by(Workflow.id.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def approve_workflow(
    db: AsyncSession,
    workflow_id: int,
    data: WorkflowApprove,
    approver_id: int,
) -> Workflow:
    """审批流程"""
    workflow = await get_workflow(db, workflow_id)

    # 验证状态转换
    new_status = "approved" if data.approved else "rejected"
    if not validate_status_transition(workflow.status, new_status):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法从 {workflow.status} 转换到 {new_status}",
        )

    workflow.status = new_status
    workflow.approver_id = approver_id
    workflow.approved_at = datetime.utcnow()

    # 记录日志
    log = WorkflowLog(
        workflow_id=workflow.id,
        action="approve" if data.approved else "reject",
        operator_id=approver_id,
        notes=data.notes,
    )
    db.add(log)
    await db.flush()

    await db.refresh(workflow)
    return workflow


async def start_workflow(
    db: AsyncSession,
    workflow_id: int,
    operator_id: int,
) -> Workflow:
    """开始执行流程"""
    workflow = await get_workflow(db, workflow_id)

    if not validate_status_transition(workflow.status, "in_progress"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法从 {workflow.status} 转换到 in_progress",
        )

    workflow.status = "in_progress"
    workflow.started_at = datetime.utcnow()

    # 记录日志
    log = WorkflowLog(
        workflow_id=workflow.id,
        action="start",
        operator_id=operator_id,
    )
    db.add(log)
    await db.flush()

    await db.refresh(workflow)
    return workflow


async def complete_workflow(
    db: AsyncSession,
    workflow_id: int,
    operator_id: int,
    notes: Optional[str] = None,
) -> Workflow:
    """完成流程"""
    workflow = await get_workflow(db, workflow_id)

    if not validate_status_transition(workflow.status, "completed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法从 {workflow.status} 转换到 completed",
        )

    workflow.status = "completed"
    workflow.completed_at = datetime.utcnow()

    # 记录日志
    log = WorkflowLog(
        workflow_id=workflow.id,
        action="complete",
        operator_id=operator_id,
        notes=notes,
    )
    db.add(log)
    await db.flush()

    # 更新盲板状态
    result = await db.execute(select(BlindFlange).where(BlindFlange.id == workflow.blind_flange_id))
    blind_flange = result.scalar_one_or_none()
    if blind_flange:
        if workflow.type == "install":
            blind_flange.status = "installed"
        elif workflow.type == "uninstall":
            blind_flange.status = "in_stock"
        await db.flush()

    await db.refresh(workflow)
    return workflow


async def cancel_workflow(
    db: AsyncSession,
    workflow_id: int,
    data: WorkflowCancel,
    operator_id: int,
) -> Workflow:
    """取消流程"""
    workflow = await get_workflow(db, workflow_id)

    if not validate_status_transition(workflow.status, "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无法从 {workflow.status} 转换到 cancelled",
        )

    workflow.status = "cancelled"
    workflow.cancelled_at = datetime.utcnow()
    workflow.cancel_reason = data.reason

    # 记录日志
    log = WorkflowLog(
        workflow_id=workflow.id,
        action="cancel",
        operator_id=operator_id,
        notes=data.reason,
    )
    db.add(log)
    await db.flush()

    await db.refresh(workflow)
    return workflow


async def get_workflow_logs(
    db: AsyncSession,
    workflow_id: int,
) -> List[WorkflowLog]:
    """获取流程日志"""
    result = await db.execute(
        select(WorkflowLog)
        .where(WorkflowLog.workflow_id == workflow_id)
        .order_by(WorkflowLog.created_at.desc())
    )
    return result.scalars().all()
