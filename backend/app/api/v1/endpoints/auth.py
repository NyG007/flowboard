from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import hashlib
import secrets
import jwt
import os

from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE  = 60 * 24
REFRESH_TOKEN_EXPIRE = 60 * 24 * 7

security = HTTPBearer()

# ── Schemas ───────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    username: str
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime  # ← datetime em vez de str

    class Config:
        from_attributes = True

# ── Helpers ───────────────────────────────────────────────
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, hash_val = hashed.split(":")
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest() == hash_val
    except Exception:
        return False

def create_token(data: dict, expires_minutes: int) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

from datetime import timedelta

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(401, "Token inválido")
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Token inválido")
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Token inválido")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "Usuário não encontrado")
    if not user.is_active:
        raise HTTPException(403, "Conta desativada")
    return user

# ── Endpoints ─────────────────────────────────────────────
@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email já cadastrado")
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Username já em uso")
    user = User(
        email=data.email,
        full_name=data.full_name,
        username=data.username,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "Email ou senha incorretos")
    if not user.is_active:
        raise HTTPException(403, "Conta desativada")
    return TokenResponse(
        access_token=create_token({"sub": str(user.id), "type": "access"}, ACCESS_TOKEN_EXPIRE),
        refresh_token=create_token({"sub": str(user.id), "type": "refresh"}, REFRESH_TOKEN_EXPIRE),
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(data.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(401, "Token inválido")
        user = db.query(User).filter(User.id == payload["sub"]).first()
        if not user:
            raise HTTPException(401, "Usuário não encontrado")
        return TokenResponse(
            access_token=create_token({"sub": str(user.id), "type": "access"}, ACCESS_TOKEN_EXPIRE),
            refresh_token=create_token({"sub": str(user.id), "type": "refresh"}, REFRESH_TOKEN_EXPIRE),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expirado")
    except Exception:
        raise HTTPException(401, "Token inválido")

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
