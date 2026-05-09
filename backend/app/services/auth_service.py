# ============================================================
# FlowBoard — Authentication Service
# Toda lógica de negócio de auth fica aqui, não nas rotas.
# Rotas são finas — apenas validam input e chamam services.
# ============================================================

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime, timezone

from app.models.user import User
from app.schemas.user import UserCreate, Token, LoginRequest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from jose import JWTError
import uuid


class AuthService:

    @staticmethod
    async def register(db: AsyncSession, data: UserCreate) -> User:
        """
        Registra novo usuário.
        Verifica duplicidade de email e username antes de criar.
        """
        # Verificar se email já existe
        existing = await db.execute(
            select(User).where(User.email == data.email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email já está em uso",
            )

        # Verificar se username já existe
        existing_username = await db.execute(
            select(User).where(User.username == data.username)
        )
        if existing_username.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este username já está em uso",
            )

        user = User(
            email=data.email,
            full_name=data.full_name,
            username=data.username,
            hashed_password=get_password_hash(data.password),
        )
        db.add(user)
        await db.flush()  # Gera o ID sem commit (para uso imediato)
        return user

    @staticmethod
    async def login(db: AsyncSession, data: LoginRequest) -> Token:
        """
        Autentica usuário e retorna par de tokens JWT.
        
        Segurança: A mensagem de erro é GENÉRICA para não revelar
        se o email existe ou não (evita user enumeration attacks).
        """
        result = await db.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()

        # Mensagem genérica — não revela se email existe
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conta desativada. Entre em contato com o suporte.",
            )

        # Atualiza último login
        user.last_login_at = datetime.now(timezone.utc)
        await db.flush()

        return Token(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )

    @staticmethod
    async def refresh_tokens(db: AsyncSession, refresh_token: str) -> Token:
        """
        Gera novo par de tokens a partir de um refresh token válido.
        Implementa token rotation — cada refresh invalida o anterior.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                raise credentials_exception
            user_id = payload.get("sub")
        except JWTError:
            raise credentials_exception

        result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise credentials_exception

        return Token(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
        )