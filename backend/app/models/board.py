# ============================================================
# FlowBoard — Board, Column, BoardMember Models
# ============================================================

import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, Integer, Boolean, DateTime,
    ForeignKey, func, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.db.base import Base


class BoardRole(str, enum.Enum):
    """Roles de permissão dentro de um board."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Board(Base):
    """
    Board = espaço de trabalho principal (equivale a um projeto).
    Um usuário pode ter múltiplos boards e ser membro de boards de outros.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Cor de identificação visual do board (hex color)
    color: Mapped[str] = mapped_column(String(7), default="#3b82f6")

    # Emoji/ícone do board para UI
    icon: Mapped[str | None] = mapped_column(String(10), nullable=True)

    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    # Foreign key para o dono do board
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relacionamentos
    owner: Mapped["User"] = relationship("User", back_populates="owned_boards")
    columns: Mapped[list["Column"]] = relationship(
        "Column",
        back_populates="board",
        cascade="all, delete-orphan",
        order_by="Column.position",  # Sempre retorna na ordem correta
    )
    members: Mapped[list["BoardMember"]] = relationship(
        "BoardMember",
        back_populates="board",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Board '{self.title}'>"


class Column(Base):
    """
    Coluna do Kanban (ex: Todo, In Progress, Done).
    A posição define a ordem de exibição — é atualizada no drag and drop.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#6b7280")

    # Posição (ordem) dentro do board — começa em 0
    # Usamos Integer com gaps (0, 1000, 2000) para reordenação eficiente
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Limite de WIP (Work In Progress) — feature de Kanban profissional
    wip_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)

    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("board.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamentos
    board: Mapped["Board"] = relationship("Board", back_populates="columns")
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="column",
        cascade="all, delete-orphan",
        order_by="Task.position",
    )


class BoardMember(Base):
    """
    Tabela de junção entre User e Board com role.
    Permite controle granular de permissões por board.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    board_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("board.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Role determina o que o usuário pode fazer no board
    role: Mapped[BoardRole] = mapped_column(
        SAEnum(BoardRole), default=BoardRole.MEMBER, nullable=False
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relacionamentos
    user: Mapped["User"] = relationship("User", back_populates="board_memberships")
    board: Mapped["Board"] = relationship("Board", back_populates="members")