"""巡检模型"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InspectionPlan(Base):
    """巡检计划表"""

    __tablename__ = "inspection_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blind_flange_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    cycle_days: Mapped[int] = mapped_column(Integer, nullable=False)
    last_inspected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_inspected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    assigned_to: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<InspectionPlan(id={self.id}, blind_flange_id={self.blind_flange_id})>"


class InspectionRecord(Base):
    """巡检记录表"""

    __tablename__ = "inspection_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blind_flange_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    inspection_plan_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    inspector_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # normal/abnormal
    images: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inspected_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<InspectionRecord(id={self.id}, blind_flange_id={self.blind_flange_id})>"
