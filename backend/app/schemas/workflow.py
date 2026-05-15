"""流程 Schema"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class WorkflowType(str, Enum):
    """流程类型"""
    INSTALL = "install"
    UNINSTALL = "uninstall"
    INSPECT = "inspect"


class WorkflowStatus(str, Enum):
    """流程状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowBase(BaseModel):
    """流程基础 Schema"""
    type: WorkflowType = Field(..., description="流程类型")
    blind_flange_id: int = Field(..., description="盲板 ID")
    notes: Optional[str] = Field(None, description="备注")


class WorkflowCreate(WorkflowBase):
    """创建流程 Schema"""
    pass


class WorkflowUpdate(BaseModel):
    """更新流程 Schema"""
    notes: Optional[str] = Field(None, description="备注")


class WorkflowApprove(BaseModel):
    """审批流程 Schema"""
    approved: bool = Field(..., description="是否通过")
    notes: Optional[str] = Field(None, description="审批意见")


class WorkflowCancel(BaseModel):
    """取消流程 Schema"""
    reason: str = Field(..., max_length=200, description="取消原因")


class WorkflowInDB(WorkflowBase):
    """数据库中的流程 Schema"""
    id: int
    status: str
    applicant_id: int
    approver_id: Optional[int]
    applied_at: datetime
    approved_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    cancel_reason: Optional[str]
    timeout_at: Optional[datetime]

    class Config:
        from_attributes = True


class WorkflowResponse(WorkflowInDB):
    """流程响应 Schema"""
    pass


class WorkflowListResponse(BaseModel):
    """流程列表响应"""
    items: List[WorkflowResponse]
    total: int
    page: int
    page_size: int


class WorkflowLogResponse(BaseModel):
    """流程日志响应"""
    id: int
    workflow_id: int
    action: str
    operator_id: int
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
