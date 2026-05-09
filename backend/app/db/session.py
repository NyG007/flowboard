# ============================================================
# FlowBoard — Database Session Factory
# Async SQLAlchemy engine e session management.
# ============================================================

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from app.core.config import settings

# ──────────────────────────────────────────────────────────
# Engine — conexão com o PostgreSQL
# pool_pre_ping: testa conexão antes de usar (evita "connection closed" errors)
# pool_size: número de conexões mantidas abertas (padrão 5)
# max_overflow: conexões extras em picos de tráfego
# echo: loga SQL em desenvolvimento (NUNCA em produção — expõe dados)
# ──────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,  # Loga queries SQL apenas em desenvolvimento
)

# Session factory — nunca crie sessões manualmente, use esta factory
# expire_on_commit=False: objetos permanecem acessíveis após commit
# (crítico em APIs async onde a sessão fecha antes da resposta)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency injection para rotas FastAPI.
    
    Uso:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    
    O 'async with' garante que a sessão é sempre fechada,
    mesmo em caso de exceção — evita connection leaks.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()