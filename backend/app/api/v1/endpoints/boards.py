from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.db.session import get_db
from app.models.board import Board
from app.models.column import BoardColumn
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/boards", tags=["boards"])


class BoardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    color: str = "#6366f1"
    icon: Optional[str] = None
    is_public: bool = False


class BoardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_archived: Optional[bool] = None


class BoardResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    color: str
    icon: Optional[str] = None
    is_archived: bool
    is_public: bool
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[BoardResponse])
async def list_boards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Board)
        .where(Board.owner_id == current_user.id, Board.is_archived == False)
        .order_by(Board.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=BoardResponse, status_code=201)
async def create_board(
    data: BoardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    board = Board(
        title=data.title,
        description=data.description,
        color=data.color,
        icon=data.icon,
        is_public=data.is_public,
        owner_id=current_user.id,
    )
    db.add(board)
    await db.flush()

    default_columns = [
        ("A Fazer", "#94a3b8", 0),
        ("Em Progresso", "#6366f1", 1),
        ("Concluído", "#22c55e", 2),
    ]
    for title, color, position in default_columns:
        db.add(BoardColumn(
            title=title,
            color=color,
            position=position,
            board_id=board.id,
        ))

    await db.commit()
    await db.refresh(board)
    return board


@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(404, "Board não encontrado")
    if board.owner_id != current_user.id and not board.is_public:
        raise HTTPException(403, "Sem permissão")
    return board


@router.patch("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: uuid.UUID,
    data: BoardUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(404, "Board não encontrado")
    if board.owner_id != current_user.id:
        raise HTTPException(403, "Sem permissão")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(board, field, value)

    await db.commit()
    await db.refresh(board)
    return board


@router.delete("/{board_id}", status_code=204)
async def delete_board(
    board_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(404, "Board não encontrado")
    if board.owner_id != current_user.id:
        raise HTTPException(403, "Sem permissão")
    await db.delete(board)
    await db.commit()