from __future__ import annotations

import datetime as dt
from typing import Any

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    lesson_id: str
    size: int = Field(..., gt=0, le=500)
    params: dict[str, Any] = Field(default_factory=dict)


class ProblemDTO(BaseModel):
    """A problem as delivered to the client — answer intentionally omitted."""

    id: int
    ordinal: int
    prompt: str


class SessionCreateResponse(BaseModel):
    session_id: int
    lesson_id: str
    status: str
    problems: list[ProblemDTO]


class AnswerRequest(BaseModel):
    problem_id: int
    user_answer: float
    elapsed_ms: int = Field(..., ge=0)


class AnswerResponse(BaseModel):
    correct: bool
    correct_answer: float
    attempt_number: int


class SessionSummary(BaseModel):
    session_id: int
    lesson_id: str
    status: str
    total_problems: int
    correct_problems: int
    score: float
    seconds_per_problem: float
    missed_problem_ids: list[int]


class SessionListItem(BaseModel):
    """Lightweight session view used by the history list."""

    session_id: int
    lesson_id: str
    status: str
    created_at: dt.datetime
    completed_at: dt.datetime | None = None
    total_problems: int
    score: float | None = None
    seconds_per_problem: float | None = None


class AttemptDTO(BaseModel):
    id: int
    attempt_number: int
    user_answer: float
    is_correct: bool
    elapsed_ms: int
    created_at: dt.datetime


class ProblemDetailDTO(BaseModel):
    """Problem view for detail/review — answer only shown for finished sessions."""

    id: int
    ordinal: int
    prompt: str
    answer: float | None = None
    attempts: list[AttemptDTO] = []


class SessionDetail(BaseModel):
    session_id: int
    lesson_id: str
    status: str
    params: dict[str, Any]
    created_at: dt.datetime
    started_at: dt.datetime | None = None
    completed_at: dt.datetime | None = None
    problems: list[ProblemDetailDTO]
    summary: SessionSummary
