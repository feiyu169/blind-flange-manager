"""盲板 Schema"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class BlindFlangeStatus(str, Enum):
    """盲板状态"""
    IN_STOCK = "in_stock"
    INSTALLED = "installed"
    MAINTENANCE = "maintenance"
    SCRAPPED = "scrapped"


class BlindFlangeBase(BaseModel):
    """盲板基础 Schema"""
    code: str = Field(..., max_length=50, description="盲板编码")
    name: str = Field(..., max_length=100, description="盲板名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    material: Optional[str] = Field(None, max_length=50, description="材质")
    pressure_rating: Optional[str] = Field(None, max_length=20, description="压力等级")
    size: Optional[str] = Field(None, max_length=20, description="尺寸")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")
    pipeline_no: Optional[str] = Field(None, max_length=50, description="管道编号")
    flange_no: Optional[str] = Field(None, max_length=50, description="法兰编号")
    status: BlindFlangeStatus = Field(BlindFlangeStatus.IN_STOCK, description="状态")
    image_url: Optional[str] = Field(None, max_length=500, description="图片 URL")
    notes: Optional[str] = Field(None, description="备注")


class BlindFlangeCreate(BlindFlangeBase):
    """创建盲板 Schema"""
    pass


class BlindFlangeUpdate(BaseModel):
    """更新盲板 Schema"""
    name: Optional[str] = Field(None, max_length=100, description="盲板名称")
    specification: Optional[str] = Field(None, max_length=100, description="规格型号")
    material: Optional[str] = Field(None, max_length=50, description="材质")
    pressure_rating: Optional[str] = Field(None, max_length=20, description="压力等级")
    size: Optional[str] = Field(None, max_length=20, description="尺寸")
    location: Optional[str] = Field(None, max_length=200, description="安装位置")
    pipeline_no: Optional[str] = Field(None, max_length=50, description="管道编号")
    flange_no: Optional[str] = Field(None, max_length=50, description="法兰编号")
    status: Optional[BlindFlangeStatus] = Field(None, description="状态")
    image_url: Optional[str] = Field(None, max_length=500, description="图片 URL")
    notes: Optional[str] = Field(None, description="备注")


class BlindFlangeInDB(BlindFlangeBase):
    """数据库中的盲板 Schema"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlindFlangeResponse(BlindFlangeInDB):
    """盲板响应 Schema"""
    pass


class BlindFlangeListResponse(BaseModel):
    """盲板列表响应"""
    items: List[BlindFlangeResponse]
    total: int
    page: int
    page_size: int


class BlindFlangeStatusLogResponse(BaseModel):
    """盲板状态变更日志响应"""
    id: int
    blind_flange_id: int
    old_status: Optional[str]
    new_status: str
    operator_id: int
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BlindFlangeImportItem(BaseModel):
    """导入项"""
    code: str = Field(..., description="盲板编码")
    name: str = Field(..., description="盲板名称")
    specification: Optional[str] = Field(None, description="规格型号")
    material: Optional[str] = Field(None, description="材质")
    pressure_rating: Optional[str] = Field(None, description="压力等级")
    size: Optional[str] = Field(None, description="尺寸")
    location: Optional[str] = Field(None, description="安装位置")
    pipeline_no: Optional[str] = Field(None, description="管道编号")
    flange_no: Optional[str] = Field(None, description="法兰编号")
    notes: Optional[str] = Field(None, description="备注")


class BlindFlangeImportResponse(BaseModel):
    """导入响应"""
    success_count: int
    fail_count: int
    errors: List[str]
