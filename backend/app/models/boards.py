import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from app.database import Base

class Board(Base):
    __tablename__ = "boards"

    id          = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title       = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    color       = Column(String, default="#6366f1")
    icon        = Column(String, nullable=True)
    is_archived = Column(Boolean, default=False)
    is_public   = Column(Boolean, default=False)
    owner_id    = Column(String, ForeignKey("users.id"), nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)