from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.db.models import Attempt, PracticeSession, Problem, SessionStatus


def test_create_session_with_problems_and_attempts(db_session):
    session = PracticeSession(
        lesson_id="basic.times_tables",
        params_json={"single_digits": True},
        status=SessionStatus.CREATED,
    )
    session.problems = [
        Problem(ordinal=1, prompt="3 x 4 = ", answer=12.0, inputs_json=[3, 4]),
        Problem(ordinal=2, prompt="5 x 6 = ", answer=30.0, inputs_json=[5, 6]),
    ]
    db_session.add(session)
    db_session.commit()

    reloaded = db_session.get(PracticeSession, session.id)
    assert reloaded is not None
    assert reloaded.lesson_id == "basic.times_tables"
    assert len(reloaded.problems) == 2
    assert [p.ordinal for p in reloaded.problems] == [1, 2]

    problem = reloaded.problems[0]
    problem.attempts = [
        Attempt(
            attempt_number=1, user_answer=11.0, is_correct=False, elapsed_ms=2500
        ),
        Attempt(
            attempt_number=2, user_answer=12.0, is_correct=True, elapsed_ms=1800
        ),
    ]
    db_session.commit()

    reloaded = db_session.get(Problem, problem.id)
    assert len(reloaded.attempts) == 2
    assert reloaded.attempts[0].attempt_number == 1
    assert reloaded.attempts[1].is_correct is True


def test_unique_ordinal_per_session(db_session):
    session = PracticeSession(lesson_id="basic.times_tables", params_json={})
    session.problems = [
        Problem(ordinal=1, prompt="a", answer=1.0, inputs_json=[]),
        Problem(ordinal=1, prompt="b", answer=2.0, inputs_json=[]),
    ]
    db_session.add(session)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_unique_attempt_number_per_problem(db_session):
    session = PracticeSession(lesson_id="basic.times_tables", params_json={})
    problem = Problem(ordinal=1, prompt="a", answer=1.0, inputs_json=[])
    session.problems = [problem]
    db_session.add(session)
    db_session.commit()

    problem.attempts = [
        Attempt(attempt_number=1, user_answer=1.0, is_correct=True, elapsed_ms=100),
        Attempt(attempt_number=1, user_answer=2.0, is_correct=False, elapsed_ms=100),
    ]
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_session_delete_cascades(db_session):
    session = PracticeSession(lesson_id="basic.times_tables", params_json={})
    problem = Problem(ordinal=1, prompt="a", answer=1.0, inputs_json=[])
    problem.attempts = [
        Attempt(attempt_number=1, user_answer=1.0, is_correct=True, elapsed_ms=100),
    ]
    session.problems = [problem]
    db_session.add(session)
    db_session.commit()

    session_id = session.id
    problem_id = problem.id

    db_session.delete(session)
    db_session.commit()

    assert db_session.get(PracticeSession, session_id) is None
    assert db_session.get(Problem, problem_id) is None
