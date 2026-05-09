from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.models.board import Board
from app.models.column import BoardColumn
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/boards", tags=["boards"])

# ── Schemas ───────────────────────────────────────────────
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
    id: str
    title: str
    description: Optional[str] = None
    color: str
    icon: Optional[str] = None
    is_archived: bool
    is_public: bool
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ── Endpoints ─────────────────────────────────────────────
@router.get("", response_model=List[BoardResponse])
def list_boards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todos os boards do usuário logado."""
    return db.query(Board).filter(
        Board.owner_id == current_user.id,
        Board.is_archived == False
    ).order_by(Board.created_at.desc()).all()


@router.post("", response_model=BoardResponse, status_code=201)
def create_board(
    data: BoardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria um novo board e já adiciona 3 colunas padrão."""
    board = Board(
        title=data.title,
        description=data.description,
        color=data.color,
        icon=data.icon,
        is_public=data.is_public,
        owner_id=current_user.id,
    )
    db.add(board)
    db.flush()  # gera o ID sem commitar

    # Criar colunas padrão automaticamente
    default_columns = [
        ("A Fazer", "#94a3b8", 0),
        ("Em Progresso", "#6366f1", 1),
        ("Concluído", "#22c55e", 2),
    ]
    for title, color, position in default_columns:
        col = BoardColumn(
            title=title,
            color=color,
            position=position,
            board_id=board.id,
        )
        db.add(col)

    db.commit()
    db.refresh(board)
    return board


@router.get("/{board_id}", response_model=BoardResponse)
def get_board(
    board_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(404, "Board não encontrado")
    if board.owner_id != current_user.id and not board.is_public:
        raise HTTPException(403, "Sem permissão")
    return board


@router.patch("/{board_id}", response_model=BoardResponse)
def update_board(
    board_id: str,
    data: BoardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(404, "Board não encontrado")
    if board.owner_id != current_user.id:
        raise HTTPException(403, "Sem permissão")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(board, field, value)
    board.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(board)
    return board


@router.delete("/{board_id}", status_code=204)
def delete_board(
    board_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(404, "Board não encontrado")
    if board.owner_id != current_user.id:
        raise HTTPException(403, "Sem permissão")
    db.delete(board)
    db.commit()