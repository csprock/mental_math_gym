from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.app.db.models import Attempt, PracticeSession, Problem, SessionStatus


@dataclass(frozen=True)
class LessonStatsData:
    lesson_id: str
    completed_sessions: int
    total_problems: int
    total_correct: int
    average_score: float
    average_seconds_per_problem: float
    recent_sessions: list[PracticeSession]


def lesson_stats(
    db: Session, lesson_id: str, recent_limit: int = 10
) -> LessonStatsData:
    """Aggregate stats across all COMPLETED sessions for a lesson.

    Averages are macro-averages over sessions (each session weighted equally),
    matching the per-session numbers users see after completing a run.
    """
    completed_stmt = (
        select(
            func.count(PracticeSession.id),
            func.coalesce(func.avg(PracticeSession.score), 0.0),
            func.coalesce(func.avg(PracticeSession.seconds_per_problem), 0.0),
        )
        .where(PracticeSession.lesson_id == lesson_id)
        .where(PracticeSession.status == SessionStatus.COMPLETED)
    )
    completed_count, avg_score, avg_spp = db.execute(completed_stmt).one()

    total_problems = (
        db.scalar(
            select(func.count(Problem.id))
            .join(PracticeSession, Problem.session_id == PracticeSession.id)
            .where(PracticeSession.lesson_id == lesson_id)
            .where(PracticeSession.status == SessionStatus.COMPLETED)
        )
        or 0
    )

    # A problem counts as "correct" only if the FIRST attempt was correct,
    # matching per-session scoring (see _problem_was_correct). Filtering on
    # attempt_number == 1 yields at most one row per problem so a plain count
    # works without GROUP BY.
    total_correct = (
        db.scalar(
            select(func.count(Problem.id))
            .join(PracticeSession, Problem.session_id == PracticeSession.id)
            .join(Attempt, Attempt.problem_id == Problem.id)
            .where(PracticeSession.lesson_id == lesson_id)
            .where(PracticeSession.status == SessionStatus.COMPLETED)
            .where(Attempt.attempt_number == 1)
            .where(Attempt.is_correct.is_(True))
        )
        or 0
    )

    recent_stmt = (
        select(PracticeSession)
        .options(selectinload(PracticeSession.problems))
        .where(PracticeSession.lesson_id == lesson_id)
        .where(PracticeSession.status == SessionStatus.COMPLETED)
        .order_by(
            PracticeSession.completed_at.desc().nulls_last(),
            PracticeSession.id.desc(),
        )
        .limit(recent_limit)
    )
    recent_sessions = list(db.scalars(recent_stmt))

    return LessonStatsData(
        lesson_id=lesson_id,
        completed_sessions=int(completed_count or 0),
        total_problems=int(total_problems),
        total_correct=int(total_correct),
        average_score=float(avg_score or 0.0),
        average_seconds_per_problem=float(avg_spp or 0.0),
        recent_sessions=recent_sessions,
    )
