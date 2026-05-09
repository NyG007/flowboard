from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.session import get_db
from app.models.task import Task
from app.models.column import BoardColumn
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "no_priority"
    labels: List[str] = []
    due_date: Optional[datetime] = None
    assignee_id: Optional[uuid.UUID] = None
    cover_color: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[uuid.UUID] = None
    cover_color: Optional[str] = None
    column_id: Optional[uuid.UUID] = None
    position: Optional[int] = None
    is_completed: Optional[bool] = None
    is_archived: Optional[bool] = None


class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    position: int
    priority: str
    labels: List[str]
    cover_color: Optional[str] = None
    estimate_hours: Optional[int] = None
    is_completed: bool
    is_archived: bool
    due_date: Optional[datetime] = None
    column_id: uuid.UUID
    creator_id: Optional[uuid.UUID] = None
    assignee_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/column/{column_id}", response_model=List[TaskResponse])
async def list_tasks(
    column_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Task)
        .where(Task.column_id == column_id, Task.is_archived == False)
        .order_by(Task.position)
    )
    return result.scalars().all()


@router.post("/column/{column_id}", response_model=TaskResponse, status_code=201)
async def create_task(
    column_id: uuid.UUID,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(BoardColumn).where(BoardColumn.id == column_id))
    col = result.scalar_one_or_none()
    if not col:
        raise HTTPException(404, "Coluna não encontrada")

    result = await db.execute(
        select(func.max(Task.position)).where(Task.column_id == column_id)
    )
    last_position = result.scalar() or -1

    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority,
        labels=data.labels,
        due_date=data.due_date,
        assignee_id=data.assignee_id,
        cover_color=data.cover_color,
        position=last_position + 1,
        column_id=column_id,
        creator_id=current_user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task não encontrada")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(404, "Task não encontrada")
    await db.delete(task)
    await db.commit()
    