from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.db.models import Attempt, PracticeSession, Problem, SessionStatus
from mathgen.common.registry import LessonMetadata, get_registry


class ParamValidationError(ValueError):
    """Raised when a session is created with invalid params for a lesson."""


class UnknownLessonError(KeyError):
    """Raised when a lesson id does not exist in the registry."""


class UnknownSessionError(KeyError):
    """Raised when a session id does not exist."""


class UnknownProblemError(KeyError):
    """Raised when a problem does not belong to the referenced session."""


class SessionStateError(RuntimeError):
    """Raised when an operation is not valid for the session's current status."""


def validate_and_normalize_params(
    metadata: LessonMetadata, supplied: dict[str, Any]
) -> dict[str, Any]:
    """Reject unknown params, coerce types, fill defaults."""
    allowed = {p.name: p for p in metadata.params}
    unknown = set(supplied) - set(allowed)
    if unknown:
        raise ParamValidationError(
            f"Unknown params for lesson {metadata.id!r}: {sorted(unknown)}"
        )

    result: dict[str, Any] = {}
    for name, param in allowed.items():
        if name in supplied:
            value = supplied[name]
            if param.type == "bool":
                if not isinstance(value, bool):
                    raise ParamValidationError(
                        f"Param {name!r} must be bool, got {type(value).__name__}"
                    )
            elif param.type == "int":
                # bool is a subclass of int in Python; reject to avoid surprises
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ParamValidationError(
                        f"Param {name!r} must be int, got {type(value).__name__}"
                    )
            result[name] = value
        else:
            result[name] = param.default
    return result


def create_session(
    db: Session, lesson_id: str, size: int, params: dict[str, Any]
) -> PracticeSession:
    registry = get_registry()
    try:
        metadata, cls = registry.get(lesson_id)
    except KeyError as e:
        raise UnknownLessonError(lesson_id) from e

    normalized_params = validate_and_normalize_params(metadata, params)
    generator = cls(**normalized_params)

    session = PracticeSession(
        lesson_id=lesson_id,
        params_json=normalized_params,
        status=SessionStatus.CREATED,
    )
    for i in range(size):
        problem = generator.new_problem()
        session.problems.append(
            Problem(
                ordinal=i + 1,
                prompt=problem.prompt,
                answer=float(problem.answer),
                inputs_json=list(problem.inputs),
            )
        )

    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: int) -> PracticeSession:
    session = db.get(PracticeSession, session_id)
    if session is None:
        raise UnknownSessionError(session_id)
    return session


@dataclass(frozen=True)
class AnswerResult:
    attempt: Attempt
    correct_answer: float


def submit_answer(
    db: Session,
    session_id: int,
    problem_id: int,
    user_answer: float,
    elapsed_ms: int,
) -> AnswerResult:
    session = get_session(db, session_id)
    if session.status in (SessionStatus.COMPLETED, SessionStatus.ABANDONED):
        raise SessionStateError(
            f"Cannot submit answer to session {session_id} with status {session.status.value}"
        )

    problem = db.get(Problem, problem_id)
    if problem is None or problem.session_id != session_id:
        raise UnknownProblemError(problem_id)

    next_number = (
        db.scalar(
            select(func.coalesce(func.max(Attempt.attempt_number), 0)).where(
                Attempt.problem_id == problem_id
            )
        )
        or 0
    ) + 1

    is_correct = user_answer == problem.answer
    attempt = Attempt(
        problem_id=problem_id,
        attempt_number=next_number,
        user_answer=user_answer,
        is_correct=is_correct,
        elapsed_ms=elapsed_ms,
    )
    db.add(attempt)

    if session.status == SessionStatus.CREATED:
        session.status = SessionStatus.IN_PROGRESS
        session.started_at = dt.datetime.now(dt.timezone.utc)

    db.commit()
    db.refresh(attempt)
    return AnswerResult(attempt=attempt, correct_answer=problem.answer)


@dataclass(frozen=True)
class SessionSummaryData:
    session_id: int
    lesson_id: str
    status: SessionStatus
    total_problems: int
    correct_problems: int
    score: float
    seconds_per_problem: float
    missed_problem_ids: list[int]


def compute_summary(session: PracticeSession) -> SessionSummaryData:
    total = len(session.problems)
    correct_count = 0
    total_elapsed_ms = 0
    missed_ids: list[int] = []
    for problem in session.problems:
        was_correct = any(a.is_correct for a in problem.attempts)
        total_elapsed_ms += sum(a.elapsed_ms for a in problem.attempts)
        if was_correct:
            correct_count += 1
        else:
            missed_ids.append(problem.id)

    score = correct_count / total if total > 0 else 0.0
    seconds_per_problem = (
        (total_elapsed_ms / 1000.0) / total if total > 0 else 0.0
    )

    return SessionSummaryData(
        session_id=session.id,
        lesson_id=session.lesson_id,
        status=session.status,
        total_problems=total,
        correct_problems=correct_count,
        score=score,
        seconds_per_problem=seconds_per_problem,
        missed_problem_ids=missed_ids,
    )


def complete_session(db: Session, session_id: int) -> SessionSummaryData:
    """Idempotent: second call returns the same summary without changing state."""
    session = get_session(db, session_id)
    summary = compute_summary(session)

    if session.status != SessionStatus.COMPLETED:
        session.status = SessionStatus.COMPLETED
        session.completed_at = dt.datetime.now(dt.timezone.utc)
        session.score = summary.score
        session.seconds_per_problem = summary.seconds_per_problem
        db.commit()
        # summary.status was read pre-flip; update to reflect new state
        summary = SessionSummaryData(
            **{**summary.__dict__, "status": SessionStatus.COMPLETED}
        )

    return summary


def list_sessions(
    db: Session,
    lesson_id: str | None = None,
    status: SessionStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[PracticeSession]:
    """Return sessions newest-first, eager-loading problems for the count."""
    stmt = (
        select(PracticeSession)
        .options(selectinload(PracticeSession.problems))
        .order_by(PracticeSession.created_at.desc(), PracticeSession.id.desc())
        .limit(limit)
        .offset(offset)
    )
    if lesson_id is not None:
        stmt = stmt.where(PracticeSession.lesson_id == lesson_id)
    if status is not None:
        stmt = stmt.where(PracticeSession.status == status)
    return list(db.scalars(stmt))


def get_session_detail(db: Session, session_id: int) -> PracticeSession:
    """Fetch a session with problems and attempts eagerly loaded."""
    stmt = (
        select(PracticeSession)
        .options(selectinload(PracticeSession.problems).selectinload(Problem.attempts))
        .where(PracticeSession.id == session_id)
    )
    session = db.scalars(stmt).one_or_none()
    if session is None:
        raise UnknownSessionError(session_id)
    return session


def create_retry_session(db: Session, source_session_id: int) -> PracticeSession:
    """Create a new session seeded with the missed problems from a completed session."""
    source = get_session_detail(db, source_session_id)
    if source.status != SessionStatus.COMPLETED:
        raise SessionStateError(
            f"Cannot retry session {source_session_id} with status {source.status.value}; "
            "complete it first."
        )

    missed = [p for p in source.problems if not any(a.is_correct for a in p.attempts)]
    if not missed:
        raise SessionStateError(
            f"Session {source_session_id} has no missed problems to retry."
        )

    new_session = PracticeSession(
        lesson_id=source.lesson_id,
        params_json=dict(source.params_json or {}),
        status=SessionStatus.CREATED,
    )
    for i, src in enumerate(missed):
        new_session.problems.append(
            Problem(
                ordinal=i + 1,
                prompt=src.prompt,
                answer=src.answer,
                inputs_json=list(src.inputs_json or []),
            )
        )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session
