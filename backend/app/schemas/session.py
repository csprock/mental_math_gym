from __future__ import annotations

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
