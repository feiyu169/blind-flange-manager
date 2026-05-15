"""扫码日志模型"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScanLog(Base):
    """扫码日志表"""

    __tablename__ = "scan_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    blind_flange_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("blind_flanges.id"), nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    scanned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<ScanLog(id={self.id}, blind_flange_id={self.blind_flange_id}, success={self.success})>"
