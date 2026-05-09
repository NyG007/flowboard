from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models.user import User  # noqa: F401 — garante criação da tabela
from app.api.v1.endpoints.auth import router as auth_router

# Criar tabelas automaticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FlowBoard API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:80",
        "http://localhost:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "healthy"}

app.include_router(auth_router, prefix="/api/v1")
