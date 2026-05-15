"""扫码日志 Schema"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ScanLogResponse(BaseModel):
    """扫码日志响应"""
    id: int
    blind_flange_id: Optional[int]
    user_id: int
    success: bool
    error_message: Optional[str]
    scanned_at: datetime

    class Config:
        from_attributes = True
