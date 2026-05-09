# ============================================================
# FlowBoard — Task Model (coração do Kanban)
# ============================================================

import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, Integer, Boolean, DateTime,
    ForeignKey, func, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import enum
from app.db.base import Base


class TaskPriority(str, enum.Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NO_PRIORITY = "no_priority"


class Task(Base):
    """
    Task = card do Kanban.
    
    Decisões de arquitetura:
    - position com gaps (0, 1000, 2000): reordenação sem UPDATE em cascata
    - due_date separado de created_at: permite tasks sem prazo
    - labels como array PostgreSQL: evita tabela extra para caso simples
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Posição dentro da coluna para drag and drop
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    priority: Mapped[TaskPriority] = mapped_column(
        SAEnum(TaskPriority),
        default=TaskPriority.NO_PRIORITY,
        nullable=False,
    )

    # Labels como array de strings PostgreSQL
    # Ex: ["bug", "frontend", "urgent"]
    labels: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)),
        default=list,
        nullable=False,
        server_default="{}",
    )

    # Cor de destaque do card
    cover_color: Mapped[str | None] = mapped_column(String(7), nullable=True)

    # Estimativa em horas (para relatórios de produtividade)
    estimate_hours: Mapped[float | None] = mapped_column(nullable=True)

    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Foreign keys
    column_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("column.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    column: Mapped["Column"] = relationship("Column", back_populates="tasks")
    creator: Mapped["User"] = relationship(
        "User", foreign_keys=[creator_id]
    )
    assignee: Mapped["User"] = relationship(
        "User", foreign_keys=[assignee_id]
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="ActivityLog.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<Task '{self.title}' [{self.priority}]>"