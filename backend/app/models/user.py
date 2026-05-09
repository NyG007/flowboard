# ============================================================
# FlowBoard — User Model
# ============================================================

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class User(Base):
    """
    Model de usuário — base de toda autenticação e ownership.
    
    Decisões de segurança:
    - UUID como PK: impossível enumerar usuários via ID sequencial
    - hashed_password: NUNCA armazenamos senha em texto puro
    - is_active: soft-disable sem deletar dados
    - is_verified: controle de email verification
    """

    # UUID v4 como primary key — gerado pelo Python, não pelo banco
    # Vantagem: o ID existe antes do INSERT (útil para refs entre objetos)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Email único — usado como login identifier
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,  # Index para login queries rápidas
        nullable=False,
    )

    # Nome completo para exibição
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Username único para @mentions no sistema de colaboração
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    # URL do avatar — pode ser externa (Google OAuth) ou interna
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Hash bcrypt da senha — nunca o valor real
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Controles de conta
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps — server_default usa o relógio do banco (consistência)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relacionamentos
    owned_boards: Mapped[list["Board"]] = relationship(
        "Board",
        back_populates="owner",
        cascade="all, delete-orphan",  # Deleta boards ao deletar usuário
    )
    board_memberships: Mapped[list["BoardMember"]] = relationship(
        "BoardMember",
        back_populates="user",
    )
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(
        "CalendarEvent",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"