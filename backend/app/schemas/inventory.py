"""库存 Schema"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class InventoryType(str, Enum):
    """库存操作类型"""
    IN = "in"
    OUT = "out"
    ADJUST = "adjust"


class InventoryRecordBase(BaseModel):
    """库存记录基础 Schema"""
    blind_flange_id: int = Field(..., description="盲板 ID")
    type: InventoryType = Field(..., description="操作类型")
    quantity: int = Field(..., gt=0, description="数量")
    reason: Optional[str] = Field(None, max_length=200, description="原因")


class InventoryRecordCreate(InventoryRecordBase):
    """创建库存记录 Schema"""
    pass


class InventoryRecordInDB(InventoryRecordBase):
    """数据库中的库存记录 Schema"""
    id: int
    operator_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryRecordResponse(InventoryRecordInDB):
    """库存记录响应 Schema"""
    pass


class InventoryRecordListResponse(BaseModel):
    """库存记录列表响应"""
    items: List[InventoryRecordResponse]
    total: int
    page: int
    page_size: int


class InventoryAlertBase(BaseModel):
    """库存预警配置基础 Schema"""
    blind_flange_type: str = Field(..., max_length=100, description="盲板类型")
    min_stock: int = Field(..., ge=0, description="最低库存阈值")
    max_stock: Optional[int] = Field(None, ge=0, description="最高库存阈值")


class InventoryAlertCreate(InventoryAlertBase):
    """创建库存预警配置 Schema"""
    pass


class InventoryAlertUpdate(BaseModel):
    """更新库存预警配置 Schema"""
    min_stock: Optional[int] = Field(None, ge=0, description="最低库存阈值")
    max_stock: Optional[int] = Field(None, ge=0, description="最高库存阈值")


class InventoryAlertInDB(InventoryAlertBase):
    """数据库中的库存预警配置 Schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryAlertResponse(InventoryAlertInDB):
    """库存预警配置响应 Schema"""
    pass


class InventoryAlertListResponse(BaseModel):
    """库存预警配置列表响应"""
    items: List[InventoryAlertResponse]
    total: int


class InventorySummary(BaseModel):
    """库存汇总"""
    blind_flange_id: int
    blind_flange_code: str
    blind_flange_name: str
    total_in: int
    total_out: int
    current_stock: int
    alert_threshold: Optional[int]
    is_alert: bool


class InventorySummaryListResponse(BaseModel):
    """库存汇总列表响应"""
    items: List[InventorySummary]
    total: int
    page: int
    page_size: int
