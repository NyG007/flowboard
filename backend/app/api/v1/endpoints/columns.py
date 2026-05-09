from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.column import BoardColumn
from app.models.board import Board
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/boards", tags=["columns"])


class ColumnCreate(BaseModel):
    title: str
    color: str = "#94a3b8"
    position: int = 0
    wip_limit: int | None = None


class ColumnUpdate(BaseModel):
    title: str | None = None
    color: str | None = None
    position: int | None = None
    wip_limit: int | None = None


@router.post("/{board_id}/columns", status_code=status.HTTP_201_CREATED)
async def create_column(board_id: uuid.UUID, data: ColumnCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    column = BoardColumn(
        board_id=board_id,
        title=data.title,
        color=data.color,
        position=data.position,
        wip_limit=data.wip_limit,
    )
    db.add(column)
    await db.commit()
    await db.refresh(column)
    return column


@router.get("/{board_id}/columns")
async def list_columns(board_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BoardColumn).where(BoardColumn.board_id == board_id).order_by(BoardColumn.position)
    )
    return result.scalars().all()


@router.patch("/{board_id}/columns/{column_id}")
async def update_column(board_id: uuid.UUID, column_id: uuid.UUID, data: ColumnUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BoardColumn).where(BoardColumn.id == column_id, BoardColumn.board_id == board_id))
    column = result.scalar_one_or_none()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(column, field, value)

    await db.commit()
    await db.refresh(column)
    return column


@router.delete("/{board_id}/columns/{column_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(board_id: uuid.UUID, column_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BoardColumn).where(BoardColumn.id == column_id, BoardColumn.board_id == board_id))
    column = result.scalar_one_or_none()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")

    await db.delete(column)
    await db.commit()