from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Pega a DATABASE_URL do .env injetado pelo docker-compose
DATABASE_URL = os.getenv("DATABASE_URL")

# Se não tiver DATABASE_URL, monta a partir das variáveis individuais
if not DATABASE_URL:
    user = os.getenv("POSTGRES_USER", "flowboard_user")
    password = os.getenv("POSTGRES_PASSWORD", "flowboard_pass")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "flowboard_db")
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
