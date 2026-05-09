# ============================================================
# FlowBoard — API v1 Router Aggregator
# Centraliza todos os sub-routers da versão 1 da API.
# Para adicionar uma nova feature: importe e inclua aqui.
# ============================================================

from fastapi import APIRouter
from app.api.v1.endpoints import auth

api_router = APIRouter()

# Incluir todos os routers de endpoints
api_router.include_router(auth.router)

# Phase 4 e 5 adicionarão:
# api_router.include_router(boards.router)
# api_router.include_router(tasks.router)
# api_router.include_router(calendar.router)
# api_router.include_router(notifications.router)