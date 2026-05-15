"""库存模型"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class InventoryRecord(Base):
    """库存记录表"""

    __tablename__ = "inventory_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blind_flange_id: Mapped[int] = mapped_column(Integer, ForeignKey("blind_flanges.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # in/out/adjust
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    operator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<InventoryRecord(id={self.id}, blind_flange_id={self.blind_flange_id}, type='{self.type}')>"


class InventoryAlert(Base):
    """库存预警配置表"""

    __tablename__ = "inventory_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blind_flange_type: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    min_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    max_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<InventoryAlert(id={self.id}, blind_flange_type='{self.blind_flange_type}')>"
