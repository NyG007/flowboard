import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title          = Column(String, nullable=False)
    description    = Column(Text, nullable=True)
    position       = Column(Integer, default=0)
    priority       = Column(String, default="no_priority")
    labels         = Column(JSON, default=list)
    cover_color    = Column(String, nullable=True)
    estimate_hours = Column(Integer, nullable=True)
    is_completed   = Column(Boolean, default=False)
    is_archived    = Column(Boolean, default=False)
    due_date       = Column(DateTime, nullable=True)
    column_id      = Column(String, ForeignKey("columns.id", ondelete="CASCADE"), nullable=False)
    creator_id     = Column(String, ForeignKey("users.id"), nullable=True)
    assignee_id    = Column(String, ForeignKey("users.id"), nullable=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)