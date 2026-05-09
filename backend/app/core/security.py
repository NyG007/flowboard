# ============================================================
# FlowBoard — Security Utilities
# Centraliza toda lógica criptográfica do sistema.
# REGRA: Nenhum outro arquivo deve importar jose ou passlib diretamente.
# ============================================================

from datetime import datetime, timedelta, timezone
from typing import Any
import uuid

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ──────────────────────────────────────────────────────────
# Password Hashing
# bcrypt é o gold standard para hash de senhas:
# - Lento por design (dificulta brute force)
# - Salted automaticamente (impede rainbow tables)
# - deprecated="auto": atualiza hashes antigos automaticamente
# ──────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha em texto puro corresponde ao hash armazenado.
    Usa comparação em tempo constante (evita timing attacks).
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gera hash bcrypt da senha.
    O salt é gerado automaticamente e embutido no hash resultante.
    """
    return pwd_context.hash(password)


# ──────────────────────────────────────────────────────────
# JWT Token Management
# Usamos dois tipos de token:
# - Access Token: curta duração (30min), enviado em cada request
# - Refresh Token: longa duração (7 dias), usado apenas para renovar
# ──────────────────────────────────────────────────────────

def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Cria um JWT Access Token.
    
    Args:
        subject: Geralmente o user UUID (str)
        expires_delta: Tempo de expiração customizado
    
    Payload inclui:
        - sub: subject (user id)
        - exp: expiration timestamp
        - iat: issued at timestamp
        - type: "access" (para distinguir de refresh tokens)
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "jti": str(uuid.uuid4()),  # JWT ID único — permite blacklisting futuro
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str | Any) -> str:
    """
    Cria um JWT Refresh Token com expiração longa.
    Refresh tokens NÃO devem ser enviados em cada request —
    apenas quando o access token expirar.
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decodifica e valida um JWT token.
    Lança JWTError se inválido ou expirado.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])