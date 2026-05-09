# ============================================================
# FlowBoard — Models Registry
# IMPORTANTE: Todos os models DEVEM ser importados aqui.
# O Alembic usa este arquivo para detectar mudanças no schema.
# ============================================================

from app.models.user import User
from app.models.board import Board, Column, BoardMember, BoardRole
from app.models.task import Task, TaskPriority
from app.models.calendar_event import CalendarEvent
from app.models.activity_log import ActivityLog

__all__ = [
    "User",
    "Board",
    "Column",
    "BoardMember",
    "BoardRole",
    "Task",
    "TaskPriority",
    "CalendarEvent",
    "ActivityLog",
]