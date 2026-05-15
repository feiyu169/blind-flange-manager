"""流程 API"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.workflow import (
    WorkflowApprove,
    WorkflowCancel,
    WorkflowCreate,
    WorkflowListResponse,
    WorkflowLogResponse,
    WorkflowResponse,
)
from app.services.auth import get_current_user, require_roles
from app.services.workflow import (
    approve_workflow,
    cancel_workflow,
    complete_workflow,
    create_workflow,
    get_workflow,
    get_workflow_logs,
    list_workflows,
    start_workflow,
)

router = APIRouter()


@router.post("", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create(
    data: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建流程"""
    workflow = await create_workflow(db, data, current_user.id)
    return WorkflowResponse.model_validate(workflow)


@router.get("", response_model=WorkflowListResponse)
async def list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    type: Optional[str] = Query(None, description="流程类型"),
    status: Optional[str] = Query(None, description="流程状态"),
    applicant_id: Optional[int] = Query(None, description="申请人 ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取流程列表"""
    result = await list_workflows(db, page, page_size, type, status, applicant_id)
    return WorkflowListResponse(
        items=[WorkflowResponse.model_validate(item) for item in result["items"]],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取流程详情"""
    workflow = await get_workflow(db, workflow_id)
    return WorkflowResponse.model_validate(workflow)


@router.put("/{workflow_id}/approve", response_model=WorkflowResponse)
async def approve(
    workflow_id: int,
    data: WorkflowApprove,
    current_user: User = Depends(require_roles("admin")),
    db: AsyncSession = Depends(get_db),
):
    """审批流程"""
    workflow = await approve_workflow(db, workflow_id, data, current_user.id)
    return WorkflowResponse.model_validate(workflow)


@router.put("/{workflow_id}/start", response_model=WorkflowResponse)
async def start(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """开始执行流程"""
    workflow = await start_workflow(db, workflow_id, current_user.id)
    return WorkflowResponse.model_validate(workflow)


@router.put("/{workflow_id}/complete", response_model=WorkflowResponse)
async def complete(
    workflow_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """完成流程"""
    workflow = await complete_workflow(db, workflow_id, current_user.id, notes)
    return WorkflowResponse.model_validate(workflow)


@router.put("/{workflow_id}/cancel", response_model=WorkflowResponse)
async def cancel(
    workflow_id: int,
    data: WorkflowCancel,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消流程"""
    workflow = await cancel_workflow(db, workflow_id, data, current_user.id)
    return WorkflowResponse.model_validate(workflow)


@router.get("/{workflow_id}/logs", response_model=List[WorkflowLogResponse])
async def get_logs(
    workflow_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取流程日志"""
    logs = await get_workflow_logs(db, workflow_id)
    return [WorkflowLogResponse.model_validate(log) for log in logs]
