from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.column import BoardColumn
from app.models.board import Board
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/boards", tags=["columns"])

class ColumnCreate(BaseModel):
    title: str
    color: str = "#94a3b8"
    wip_limit: Optional[int] = None

class ColumnUpdate(BaseModel):
    title: Optional[str] = None
    color: Optional[str] = None
    position: Optional[int] = None
    wip_limit: Optional[int] = None

class ColumnResponse(BaseModel):
    id: str
    title: str
    color: str
    position: int
    wip_limit: Optional[int] = None
    board_id: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/{board_id}/columns", response_model=List[ColumnResponse])
def list_columns(
    board_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retorna todas as colunas de um board, ordenadas por posição."""
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(404, "Board não encontrado")
    return db.query(BoardColumn).filter(
        BoardColumn.board_id == board_id
    ).order_by(BoardColumn.position).all()


@router.post("/{board_id}/columns", response_model=ColumnResponse, status_code=201)
def create_column(
    board_id: str,
    data: ColumnCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(404, "Board não encontrado")
    if board.owner_id != current_user.id:
        raise HTTPException(403, "Sem permissão")

    # Posição = último + 1
    last = db.query(BoardColumn).filter(
        BoardColumn.board_id == board_id
    ).order_by(BoardColumn.position.desc()).first()
    position = (last.position + 1) if last else 0

    col = BoardColumn(
        title=data.title,
        color=data.color,
        position=position,
        wip_limit=data.wip_limit,
        board_id=board_id,
    )
    db.add(col)
    db.commit()
    db.refresh(col)
    return col


@router.patch("/{board_id}/columns/{column_id}", response_model=ColumnResponse)
def update_column(
    board_id: str,
    column_id: str,
    data: ColumnUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    col = db.query(BoardColumn).filter(
        BoardColumn.id == column_id,
        BoardColumn.board_id == board_id
    ).first()
    if not col:
        raise HTTPException(404, "Coluna não encontrada")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(col, field, value)
    db.commit()
    db.refresh(col)
    return col


@router.delete("/{board_id}/columns/{column_id}", status_code=204)
def delete_column(
    board_id: str,
    column_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    col = db.query(BoardColumn).filter(
        BoardColumn.id == column_id,
        BoardColumn.board_id == board_id
    ).first()
    if not col:
        raise HTTPException(404, "Coluna não encontrada")
    db.delete(col)
    db.commit()