# ============================================================
# FlowBoard — Activity Log Model (audit trail)
# Registra toda ação relevante para histórico e notificações
# ============================================================

import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class ActivityLog(Base):

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Tipo de ação: "task_created", "task_moved", "comment_added", etc.
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Descrição legível para humanos: "João moveu 'Fix bug' para Done"
    description: Mapped[str] = mapped_column(Text, nullable=False)

    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("task.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,  # Index para queries de "últimas atividades"
    )

    task: Mapped["Task"] = relationship("Task", back_populates="activity_logs")
    user: Mapped["User"] = relationship("User")