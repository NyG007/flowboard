from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
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
    assignee_id: Optional[str] = None
    cover_color: Optional[str] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[str] = None
    cover_color: Optional[str] = None
    column_id: Optional[str] = None   # ← mover para outra coluna
    position: Optional[int] = None
    is_completed: Optional[bool] = None
    is_archived: Optional[bool] = None

class TaskResponse(BaseModel):
    id: str
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
    column_id: str
    creator_id: Optional[str] = None
    assignee_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/column/{column_id}", response_model=List[TaskResponse])
def list_tasks(
    column_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas as tasks de uma coluna, ordenadas por posição."""
    return db.query(Task).filter(
        Task.column_id == column_id,
        Task.is_archived == False
    ).order_by(Task.position).all()


@router.post("/column/{column_id}", response_model=TaskResponse, status_code=201)
def create_task(
    column_id: str,
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    col = db.query(BoardColumn).filter(BoardColumn.id == column_id).first()
    if not col:
        raise HTTPException(404, "Coluna não encontrada")

    # Posição = último + 1
    last = db.query(Task).filter(
        Task.column_id == column_id
    ).order_by(Task.position.desc()).first()
    position = (last.position + 1) if last else 0

    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority,
        labels=data.labels,
        due_date=data.due_date,
        assignee_id=data.assignee_id,
        cover_color=data.cover_color,
        position=position,
        column_id=column_id,
        creator_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: str,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task não encontrada")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task não encontrada")
    db.delete(task)
    db.commit()