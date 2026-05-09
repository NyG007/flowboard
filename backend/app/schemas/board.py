from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
import uuid
from app.models.board import BoardRole


class BoardCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    color: str = Field(default="#3b82f6", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str | None = None
    is_public: bool = False


class BoardUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: str | None = None
    is_archived: bool | None = None


class BoardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    color: str
    icon: str | None
    is_archived: bool
    is_public: bool
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ColumnCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#6b7280", pattern=r"^#[0-9A-Fa-f]{6}$")
    position: int = Field(default=0, ge=0)
    wip_limit: int | None = Field(None, ge=1)


class ColumnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    color: str
    position: int
    wip_limit: int | None
    board_id: uuid.UUID