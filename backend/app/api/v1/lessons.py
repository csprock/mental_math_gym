from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.schemas.lesson import LessonDTO, LessonParamDTO
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
