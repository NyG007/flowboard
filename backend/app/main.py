from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


from app.models.user import User          # noqa
from app.models.board import Board        # noqa
from app.models.column import BoardColumn # noqa
from app.models.task import Task          # noqa

from app.api.v1.endpoints.auth    import router as auth_router
from app.api.v1.endpoints.boards  import router as boards_router
from app.api.v1.endpoints.columns import router as columns_router
from app.api.v1.endpoints.tasks   import router as tasks_router

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

@app.on_event("startup")
async def startup():
    await create_tables()

@app.get("/health")
async def health():
    return {"status": "healthy"}

app.include_router(auth_router,    prefix="/api/v1")
app.include_router(boards_router,  prefix="/api/v1")
app.include_router(columns_router, prefix="/api/v1")
app.include_router(tasks_router,   prefix="/api/v1")