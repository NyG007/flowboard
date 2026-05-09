# ============================================================
# FlowBoard — Authentication Endpoints
# Rotas finas: apenas validam, delegam ao service, retornam.
# ============================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, Token, TokenRefresh, LoginRequest
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Cria uma nova conta de usuário."""
    user = await AuthService.register(db, data)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login — retorna JWT tokens",
)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Autentica o usuário e retorna access + refresh tokens."""
    return await AuthService.login(db, data)


@router.post(
    "/refresh",
    response_model=Token,
    summary="Renovar tokens via refresh token",
)
async def refresh(
    data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Renova o par de tokens usando o refresh token."""
    return await AuthService.refresh_tokens(db, data.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Retorna usuário autenticado",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Retorna os dados do usuário autenticado."""
    return current_user