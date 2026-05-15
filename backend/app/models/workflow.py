"""流程模型"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Workflow(Base):
    """流程表"""

    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # install/uninstall/inspect
    blind_flange_id: Mapped[int] = mapped_column(Integer, ForeignKey("blind_flanges.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    applicant_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    approver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancel_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    timeout_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, type='{self.type}', status='{self.status}')>"


class WorkflowLog(Base):
    """流程日志表"""

    __tablename__ = "workflow_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workflow_id: Mapped[int] = mapped_column(Integer, ForeignKey("workflows.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    operator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<WorkflowLog(id={self.id}, workflow_id={self.workflow_id}, action='{self.action}')>"
