from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.deps import get_db
from backend.app.schemas.lesson import LessonDTO, LessonParamDTO
from backend.app.schemas.session import SessionListItem
from backend.app.schemas.stats import LessonStats
from backend.app.services import stats_service
from mathgen.common.registry import LessonMetadata, get_registry

router = APIRouter(prefix="/lessons", tags=["lessons"])


def _to_dto(metadata: LessonMetadata) -> LessonDTO:
    return LessonDTO(
        id=metadata.id,
        title=metadata.title,
        description=metadata.description,
        unit=metadata.unit,
        params=[
            LessonParamDTO(
                name=p.name,
                type=p.type,
                default=p.default,
                description=p.description,
            )
            for p in metadata.params
        ],
    )


@router.get("", response_model=list[LessonDTO])
def list_lessons() -> list[LessonDTO]:
    return [_to_dto(m) for m in get_registry().all()]


@router.get("/{lesson_id}", response_model=LessonDTO)
def get_lesson(lesson_id: str) -> LessonDTO:
    try:
        metadata, _cls = get_registry().get(lesson_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown lesson: {lesson_id!r}")
    return _to_dto(metadata)


@router.get("/{lesson_id}/stats", response_model=LessonStats)
def get_lesson_stats(
    lesson_id: str, db: Session = Depends(get_db)
) -> LessonStats:
    try:
        get_registry().get(lesson_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Unknown lesson: {lesson_id!r}")

    data = stats_service.lesson_stats(db, lesson_id)
    return LessonStats(
        lesson_id=data.lesson_id,
        completed_sessions=data.completed_sessions,
        total_problems=data.total_problems,
        total_correct=data.total_correct,
        average_score=data.average_score,
        average_seconds_per_problem=data.average_seconds_per_problem,
        recent_sessions=[
            SessionListItem(
                session_id=s.id,
                lesson_id=s.lesson_id,
                status=s.status.value,
                created_at=s.created_at,
                completed_at=s.completed_at,
                total_problems=len(s.problems),
                score=s.score,
                seconds_per_problem=s.seconds_per_problem,
            )
            for s in data.recent_sessions
        ],
    )
