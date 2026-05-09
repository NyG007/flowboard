import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from app.database import Base

class BoardColumn(Base):
    __tablename__ = "columns"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title      = Column(String, nullable=False)
    color      = Column(String, default="#94a3b8")
    position   = Column(Integer, default=0)
    wip_limit  = Column(Integer, nullable=True)
    board_id   = Column(String, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)