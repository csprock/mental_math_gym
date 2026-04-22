from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class LessonParamDTO(BaseModel):
    name: str
    type: str
    default: Any
    description: str = ""


class LessonDTO(BaseModel):
    id: str
    title: str
    description: str = ""
    unit: str | None = None
    params: list[LessonParamDTO] = []
