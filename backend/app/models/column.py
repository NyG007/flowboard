import uuid
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class BoardColumn(Base):
    __tablename__ = "board_column"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#94a3b8")
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wip_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("board.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    board: Mapped["Board"] = relationship("Board", back_populates="columns")
    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="column", cascade="all, delete-orphan", order_by="Task.position"
    )