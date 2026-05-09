from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
import uuid
from app.models.task import TaskPriority


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: TaskPriority = TaskPriority.NO_PRIORITY
    labels: list[str] = []
    due_date: datetime | None = None
    estimate_hours: float | None = Field(None, ge=0)
    assignee_id: uuid.UUID | None = None
    cover_color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    priority: TaskPriority | None = None
    labels: list[str] | None = None
    due_date: datetime | None = None
    estimate_hours: float | None = None
    assignee_id: uuid.UUID | None = None
    cover_color: str | None = None
    is_completed: bool | None = None
    column_id: uuid.UUID | None = None   # Para mover entre colunas
    position: int | None = None           # Para reordenar


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None
    position: int
    priority: TaskPriority
    labels: list[str]
    cover_color: str | None
    estimate_hours: float | None
    is_completed: bool
    is_archived: bool
    due_date: datetime | None
    column_id: uuid.UUID
    creator_id: uuid.UUID | None
    assignee_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime