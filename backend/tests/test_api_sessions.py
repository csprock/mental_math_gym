from __future__ import annotations

import pytest


def _create_session(client, lesson_id="basic.times_tables", size=5, params=None):
    body = {"lesson_id": lesson_id, "size": size, "params": params or {}}
    resp = client.post("/api/v1/sessions", json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_session_returns_problems_without_answers(client):
    body = _create_session(client, size=3)
    assert body["lesson_id"] == "basic.times_tables"
    assert body["status"] == "created"
    assert len(body["problems"]) == 3
    ordinals = [p["ordinal"] for p in body["problems"]]
    assert ordinals == [1, 2, 3]
    for p in body["problems"]:
        assert set(p.keys()) == {"id", "ordinal", "prompt"}


def test_create_session_unknown_lesson_404(client):
    resp = client.post(
        "/api/v1/sessions", json={"lesson_id": "nope", "size": 3, "params": {}}
    )
    assert resp.status_code == 404


def test_create_session_rejects_unknown_param(client):
    resp = client.post(
        "/api/v1/sessions",
        json={"lesson_id": "basic.times_tables", "size": 3, "params": {"bogus": 1}},
    )
    assert resp.status_code == 400
    assert "bogus" in resp.text.lower()


def test_create_session_rejects_wrong_param_type(client):
    resp = client.post(
        "/api/v1/sessions",
        json={
            "lesson_id": "basic.times_tables",
            "size": 3,
            "params": {"single_digits": "yes"},
        },
    )
    assert resp.status_code == 400


def test_create_session_size_must_be_positive(client):
    resp = client.post(
        "/api/v1/sessions", json={"lesson_id": "basic.times_tables", "size": 0}
    )
    assert resp.status_code == 422  # pydantic validation


def test_submit_correct_answer_and_status_transition(client, db_session):
    from backend.app.db.models import PracticeSession

    body = _create_session(client, size=2)
    session_id = body["session_id"]

    # Fetch the real answer from the DB for a deterministic test.
    session = db_session.get(PracticeSession, session_id)
    p0 = session.problems[0]

    resp = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"problem_id": p0.id, "user_answer": p0.answer, "elapsed_ms": 1000},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["correct"] is True
    assert data["attempt_number"] == 1
    assert data["correct_answer"] == p0.answer

    db_session.expire_all()
    session = db_session.get(PracticeSession, session_id)
    assert session.status.value == "in_progress"
    assert session.started_at is not None


def test_submit_wrong_answer_and_retry_increments_attempt_number(client, db_session):
    from backend.app.db.models import PracticeSession

    body = _create_session(client, size=1)
    session_id = body["session_id"]
    session = db_session.get(PracticeSession, session_id)
    p = session.problems[0]

    r1 = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"problem_id": p.id, "user_answer": p.answer + 1, "elapsed_ms": 500},
    )
    assert r1.status_code == 200
    assert r1.json()["correct"] is False
    assert r1.json()["attempt_number"] == 1

    r2 = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"problem_id": p.id, "user_answer": p.answer, "elapsed_ms": 300},
    )
    assert r2.status_code == 200
    assert r2.json()["correct"] is True
    assert r2.json()["attempt_number"] == 2


def test_submit_answer_unknown_session_404(client):
    resp = client.post(
        "/api/v1/sessions/9999/answers",
        json={"problem_id": 1, "user_answer": 1.0, "elapsed_ms": 100},
    )
    assert resp.status_code == 404


def test_submit_answer_wrong_session_for_problem_404(client, db_session):
    from backend.app.db.models import PracticeSession

    body_a = _create_session(client, size=1)
    body_b = _create_session(client, size=1)
    session_b_id = body_b["session_id"]

    session_a = db_session.get(PracticeSession, body_a["session_id"])
    p_a = session_a.problems[0]

    resp = client.post(
        f"/api/v1/sessions/{session_b_id}/answers",
        json={"problem_id": p_a.id, "user_answer": 1.0, "elapsed_ms": 100},
    )
    assert resp.status_code == 404


def test_complete_session_computes_summary(client, db_session):
    from backend.app.db.models import PracticeSession

    body = _create_session(client, size=3)
    session_id = body["session_id"]
    session = db_session.get(PracticeSession, session_id)

    # first two correct, third wrong
    for p in session.problems[:2]:
        client.post(
            f"/api/v1/sessions/{session_id}/answers",
            json={"problem_id": p.id, "user_answer": p.answer, "elapsed_ms": 1000},
        )
    third = session.problems[2]
    client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"problem_id": third.id, "user_answer": third.answer + 1, "elapsed_ms": 2000},
    )

    resp = client.post(f"/api/v1/sessions/{session_id}/complete")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["total_problems"] == 3
    assert data["correct_problems"] == 2
    assert data["score"] == pytest.approx(2 / 3)
    assert data["seconds_per_problem"] == pytest.approx(4.0 / 3)
    assert data["missed_problem_ids"] == [third.id]


def test_complete_is_idempotent(client, db_session):
    body = _create_session(client, size=1)
    session_id = body["session_id"]

    r1 = client.post(f"/api/v1/sessions/{session_id}/complete")
    r2 = client.post(f"/api/v1/sessions/{session_id}/complete")

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json() == r2.json()


def test_submit_answer_after_complete_rejected(client, db_session):
    from backend.app.db.models import PracticeSession

    body = _create_session(client, size=1)
    session_id = body["session_id"]
    client.post(f"/api/v1/sessions/{session_id}/complete")

    session = db_session.get(PracticeSession, session_id)
    p = session.problems[0]

    resp = client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"problem_id": p.id, "user_answer": p.answer, "elapsed_ms": 100},
    )
    assert resp.status_code == 400


def test_retry_attempts_count_toward_seconds_per_problem(client, db_session):
    from backend.app.db.models import PracticeSession

    body = _create_session(client, size=1)
    session_id = body["session_id"]
    session = db_session.get(PracticeSession, session_id)
    p = session.problems[0]

    client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"problem_id": p.id, "user_answer": p.answer + 1, "elapsed_ms": 1000},
    )
    client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"problem_id": p.id, "user_answer": p.answer, "elapsed_ms": 500},
    )

    resp = client.post(f"/api/v1/sessions/{session_id}/complete")
    assert resp.status_code == 200
    data = resp.json()
    assert data["correct_problems"] == 1  # eventually got it
    assert data["seconds_per_problem"] == pytest.approx(1.5)  # both attempts counted
