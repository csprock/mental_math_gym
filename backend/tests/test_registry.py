from __future__ import annotations

import pytest

from mathgen.common.problems import ProblemSetBaseClass
from mathgen.common.registry import LessonRegistry, LessonMetadata, register_lesson, get_registry


def test_registry_discovers_all_lessons():
    import mathgen.lessons  # noqa: F401

    registry = get_registry()
    ids = set(registry.ids())

    # basic
    assert {
        "basic.times_tables",
        "basic.addition_tables",
        "basic.subtraction_tables",
    } <= ids

    # representative mmmg lessons across units
    assert {"mmmg.lesson1", "mmmg.lesson8", "mmmg.lesson22", "mmmg.lesson27"} <= ids

    # empty Lesson3 should NOT be registered
    assert "mmmg.lesson3" not in ids


def test_registry_metadata_shape():
    import mathgen.lessons  # noqa: F401

    registry = get_registry()
    meta, cls = registry.get("basic.times_tables")

    assert isinstance(meta, LessonMetadata)
    assert meta.title == "Times Tables"
    assert meta.unit == "Basic"
    assert {p.name for p in meta.params} == {"single_digits", "exclude_tens_and_elevens"}
    assert issubclass(cls, ProblemSetBaseClass)


def test_duplicate_registration_raises():
    reg = LessonRegistry()

    @register_lesson(id="dup.test", title="A")
    class _A(ProblemSetBaseClass):
        def new_problem(self):
            raise NotImplementedError

    # The global registry got one; now try to register the same id twice on a fresh registry.
    meta = LessonMetadata(id="dup.test", title="B")
    reg.register(meta, _A)
    with pytest.raises(ValueError, match="already registered"):
        reg.register(meta, _A)


def test_metadata_attached_to_class():
    import mathgen.lessons  # noqa: F401
    from mathgen.lessons.basic import TimesTables

    assert TimesTables._lesson_metadata.id == "basic.times_tables"
