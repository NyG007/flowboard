# ============================================================
# FlowBoard — User Schemas (Request/Response validation)
# Pydantic v2 schemas — separados dos models ORM.
# REGRA: Models ORM nunca saem direto das rotas. Sempre via Schema.
# ============================================================

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
import uuid


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")


class UserCreate(UserBase):
    """Schema para registro de novo usuário."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema para atualização de perfil — todos os campos opcionais."""
    full_name: str | None = Field(None, min_length=2, max_length=100)
    username: str | None = Field(None, min_length=3, max_length=50)
    avatar_url: str | None = None


class UserResponse(UserBase):
    """
    Schema de resposta — o que a API retorna ao cliente.
    NUNCA inclua hashed_password aqui.
    model_config com from_attributes=True permite converter ORM → Pydantic.
    """
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    avatar_url: str | None
    is_active: bool
    is_verified: bool
    created_at: datetime


class UserPublic(BaseModel):
    """Schema público — mínimo necessário para @mentions e avatars."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    full_name: str
    avatar_url: str | None


# ── Auth Schemas ──────────────────────────────────────────

class Token(BaseModel):
    """Resposta do endpoint de login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Request para renovar o access token."""
    refresh_token: str


class LoginRequest(BaseModel):
    """Credenciais de login."""
    email: EmailStr
    password: str