"""巡检 Schema"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class InspectionStatus(str, Enum):
    """巡检状态"""
    NORMAL = "normal"
    ABNORMAL = "abnormal"


class InspectionPlanBase(BaseModel):
    """巡检计划基础 Schema"""
    blind_flange_id: int = Field(..., description="盲板 ID")
    cycle_days: int = Field(..., gt=0, description="巡检周期（天）")
    assigned_to: Optional[int] = Field(None, description="指定巡检人 ID")


class InspectionPlanCreate(InspectionPlanBase):
    """创建巡检计划 Schema"""
    pass


class InspectionPlanUpdate(BaseModel):
    """更新巡检计划 Schema"""
    cycle_days: Optional[int] = Field(None, gt=0, description="巡检周期（天）")
    assigned_to: Optional[int] = Field(None, description="指定巡检人 ID")
    is_active: Optional[bool] = Field(None, description="是否启用")


class InspectionPlanInDB(InspectionPlanBase):
    """数据库中的巡检计划 Schema"""
    id: int
    last_inspected_at: Optional[datetime]
    next_inspected_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InspectionPlanResponse(InspectionPlanInDB):
    """巡检计划响应 Schema"""
    pass


class InspectionPlanListResponse(BaseModel):
    """巡检计划列表响应"""
    items: List[InspectionPlanResponse]
    total: int
    page: int
    page_size: int


class InspectionRecordBase(BaseModel):
    """巡检记录基础 Schema"""
    blind_flange_id: int = Field(..., description="盲板 ID")
    inspection_plan_id: Optional[int] = Field(None, description="巡检计划 ID")
    status: InspectionStatus = Field(..., description="巡检状态")
    images: Optional[List[str]] = Field(None, description="图片列表")
    notes: Optional[str] = Field(None, description="备注")


class InspectionRecordCreate(InspectionRecordBase):
    """创建巡检记录 Schema"""
    pass


class InspectionRecordInDB(InspectionRecordBase):
    """数据库中的巡检记录 Schema"""
    id: int
    inspector_id: int
    inspected_at: datetime

    class Config:
        from_attributes = True


class InspectionRecordResponse(InspectionRecordInDB):
    """巡检记录响应 Schema"""
    pass


class InspectionRecordListResponse(BaseModel):
    """巡检记录列表响应"""
    items: List[InspectionRecordResponse]
    total: int
    page: int
    page_size: int


class DueInspection(BaseModel):
    """待巡检项"""
    plan_id: int
    blind_flange_id: int
    blind_flange_code: str
    blind_flange_name: str
    cycle_days: int
    last_inspected_at: Optional[datetime]
    next_inspected_at: Optional[datetime]
    assigned_to: Optional[int]
    is_overdue: bool


class DueInspectionListResponse(BaseModel):
    """待巡检列表响应"""
    items: List[DueInspection]
    total: int
