from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Literal, Type

from mathgen.common.problems import ProblemSetBaseClass

logger = logging.getLogger(__name__)

ParamType = Literal["bool", "int"]


@dataclass(frozen=True)
class LessonParam:
    name: str
    type: ParamType
    default: Any
    description: str = ""


@dataclass(frozen=True)
class LessonMetadata:
    id: str
    title: str
    description: str = ""
    unit: str | None = None
    params: tuple[LessonParam, ...] = field(default_factory=tuple)


class LessonRegistry:
    def __init__(self) -> None:
        self._lessons: dict[str, tuple[LessonMetadata, Type[ProblemSetBaseClass]]] = {}

    def register(
        self, metadata: LessonMetadata, cls: Type[ProblemSetBaseClass]
    ) -> None:
        if metadata.id in self._lessons:
            existing_cls = self._lessons[metadata.id][1]
            raise ValueError(
                f"Lesson id {metadata.id!r} already registered to "
                f"{existing_cls.__module__}.{existing_cls.__name__}; "
                f"cannot register {cls.__module__}.{cls.__name__}"
            )
        self._lessons[metadata.id] = (metadata, cls)
        logger.debug("registered lesson %s -> %s", metadata.id, cls.__name__)

    def get(self, lesson_id: str) -> tuple[LessonMetadata, Type[ProblemSetBaseClass]]:
        if lesson_id not in self._lessons:
            raise KeyError(f"Unknown lesson id: {lesson_id!r}")
        return self._lessons[lesson_id]

    def all(self) -> list[LessonMetadata]:
        return [meta for meta, _ in self._lessons.values()]

    def ids(self) -> list[str]:
        return list(self._lessons.keys())

    def clear(self) -> None:
        """Primarily for tests."""
        self._lessons.clear()


_registry = LessonRegistry()


def get_registry() -> LessonRegistry:
    return _registry


def register_lesson(
    id: str,
    title: str,
    description: str = "",
    unit: str | None = None,
    params: tuple[LessonParam, ...] = (),
) -> Callable[[Type[ProblemSetBaseClass]], Type[ProblemSetBaseClass]]:
    def decorator(cls: Type[ProblemSetBaseClass]) -> Type[ProblemSetBaseClass]:
        metadata = LessonMetadata(
            id=id, title=title, description=description, unit=unit, params=params
        )
        _registry.register(metadata, cls)
        cls._lesson_metadata = metadata  # type: ignore[attr-defined]
        return cls

    return decorator
