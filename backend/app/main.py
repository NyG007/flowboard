# ============================================================
# FlowBoard — FastAPI Application Entry Point
# This file creates and configures the FastAPI application.
# ============================================================

from app.api.v1.router import api_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager replaces deprecated @app.on_event handlers.
    Code BEFORE yield = startup logic.
    Code AFTER yield = shutdown logic.
    """
    # Startup: create DB tables (for development)
    # In production, Alembic migrations handle this
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ FlowBoard backend started successfully")
    yield
    # Shutdown: clean up resources
    await engine.dispose()
    print("🛑 FlowBoard backend shutting down")


# Create FastAPI app with metadata for Swagger UI
app = FastAPI(
    title=settings.APP_NAME,
    description="Professional productivity platform — Kanban, Calendar, Tasks",
    version="1.0.0",
    docs_url="/api/docs",         # Swagger UI at /api/docs
    redoc_url="/api/redoc",       # ReDoc at /api/redoc
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ──────────────────────────────────────────────────────────
# MIDDLEWARE — Order matters! Applied bottom-up (last added = first executed)
# ──────────────────────────────────────────────────────────

# 1. CORS — Must be first to handle preflight requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,         # Required for cookies (refresh tokens)
    allow_methods=["*"],            # GET, POST, PUT, DELETE, PATCH, OPTIONS
    allow_headers=["*"],            # Authorization, Content-Type, etc.
)

# 2. Trusted Host — Prevents Host header injection attacks (production only)
if settings.APP_ENV == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["flowboard.com", "api.flowboard.com"],
    )

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# ──────────────────────────────────────────────────────────
# ROUTERS — Will be wired in Phase 2
# ──────────────────────────────────────────────────────────
# from app.api.v1.router import api_router
# app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Health check endpoint — used by Docker and load balancers
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Returns 200 OK when the service is running.
    Load balancers and orchestrators (k8s) ping this to route traffic.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0",
    }