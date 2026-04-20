from __future__ import annotations

from pydantic import BaseModel

from backend.app.schemas.session import SessionListItem


class LessonStats(BaseModel):
    """Rolled-up stats for a single lesson across all completed sessions."""

    lesson_id: str
    completed_sessions: int
    total_problems: int
    total_correct: int
    average_score: float
    average_seconds_per_problem: float
    recent_sessions: list[SessionListItem] = []
