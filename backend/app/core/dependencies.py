# ============================================================
# FlowBoard — FastAPI Dependencies
# Funções reutilizáveis injetadas via Depends() nas rotas.
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

# OAuth2PasswordBearer: extrai o token do header Authorization: Bearer <token>
# tokenUrl: endpoint onde o frontend obtém o token (para o Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency principal de autenticação.
    
    Fluxo:
    1. Extrai o Bearer token do header
    2. Decodifica e valida o JWT
    3. Busca o usuário no banco
    4. Verifica se está ativo
    5. Retorna o User ou lança 401
    
    Uso nas rotas:
        async def my_route(current_user: User = Depends(get_current_user)):
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)

        # Garante que é um access token (não refresh)
        if payload.get("type") != "access":
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Busca o usuário no banco (async query)
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )

    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency para rotas exclusivas de superusuários (admin panel).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissões insuficientes",
        )
    return current_user