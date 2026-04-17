"""任务模型"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_TITLE = "awaiting_title"
    AWAITING_OUTLINE = "awaiting_outline"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(Base):
    """创作任务"""
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    topic: Mapped[str] = mapped_column(Text, nullable=False)
    matrix_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    image_source: Mapped[str] = mapped_column(String(50), default="random")
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus),
        default=TaskStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # 工作流状态（JSON）
    state_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Task {self.id} [{self.status.value}]>"
