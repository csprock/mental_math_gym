from __future__ import annotations

import pytest


def _create(client, lesson_id="basic.times_tables", size=3, params=None):
    body = {"lesson_id": lesson_id, "size": size, "params": params or {}}
    resp = client.post("/api/v1/sessions", json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _play(client, db_session, session_id, outcomes, elapsed_ms=1000):
    """Submit answers for a session. `outcomes` is a list of bools (correct?)."""
    from backend.app.db.models import PracticeSession

    session = db_session.get(PracticeSession, session_id)
    for problem, correct in zip(session.problems, outcomes):
        ans = problem.answer if correct else problem.answer + 1
        client.post(
            f"/api/v1/sessions/{session_id}/answers",
            json={"problem_id": problem.id, "user_answer": ans, "elapsed_ms": elapsed_ms},
        )


def test_lesson_stats_unknown_lesson_404(client):
    resp = client.get("/api/v1/lessons/does.not.exist/stats")
    assert resp.status_code == 404


def test_lesson_stats_empty_when_no_sessions(client):
    resp = client.get("/api/v1/lessons/basic.times_tables/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["lesson_id"] == "basic.times_tables"
    assert data["completed_sessions"] == 0
    assert data["total_problems"] == 0
    assert data["total_correct"] == 0
    assert data["average_score"] == 0.0
    assert data["average_seconds_per_problem"] == 0.0
    assert data["recent_sessions"] == []


def test_lesson_stats_excludes_non_completed_sessions(client, db_session):
    # One session created but not completed
    _create(client, size=3)

    # Complete one: all correct
    body = _create(client, size=2)
    _play(client, db_session, body["session_id"], [True, True], elapsed_ms=500)
    client.post(f"/api/v1/sessions/{body['session_id']}/complete")

    resp = client.get("/api/v1/lessons/basic.times_tables/stats")
    data = resp.json()
    assert data["completed_sessions"] == 1
    assert data["total_problems"] == 2
    assert data["total_correct"] == 2
    assert data["average_score"] == pytest.approx(1.0)


def test_lesson_stats_macro_averages(client, db_session):
    # Session 1: 2/2 correct, 0.5s avg (1000ms total / 2 problems)
    s1 = _create(client, size=2)
    _play(client, db_session, s1["session_id"], [True, True], elapsed_ms=500)
    client.post(f"/api/v1/sessions/{s1['session_id']}/complete")

    # Session 2: 1/2 correct, 2.0s avg (2000ms each -> total 4000ms / 2)
    s2 = _create(client, size=2)
    _play(client, db_session, s2["session_id"], [True, False], elapsed_ms=2000)
    client.post(f"/api/v1/sessions/{s2['session_id']}/complete")

    resp = client.get("/api/v1/lessons/basic.times_tables/stats")
    data = resp.json()
    assert data["completed_sessions"] == 2
    assert data["total_problems"] == 4
    assert data["total_correct"] == 3
    # macro avg of 1.0 and 0.5
    assert data["average_score"] == pytest.approx(0.75)
    # macro avg of 0.5s and 2.0s
    assert data["average_seconds_per_problem"] == pytest.approx(1.25)


def test_lesson_stats_ignores_other_lessons(client, db_session):
    s1 = _create(client, lesson_id="basic.times_tables", size=1)
    _play(client, db_session, s1["session_id"], [True])
    client.post(f"/api/v1/sessions/{s1['session_id']}/complete")

    s2 = _create(client, lesson_id="basic.addition_tables", size=2)
    _play(client, db_session, s2["session_id"], [False, False])
    client.post(f"/api/v1/sessions/{s2['session_id']}/complete")

    resp = client.get("/api/v1/lessons/basic.times_tables/stats")
    data = resp.json()
    assert data["completed_sessions"] == 1
    assert data["total_problems"] == 1
    assert data["total_correct"] == 1


def test_lesson_stats_recent_sessions_newest_first(client, db_session):
    completed_ids = []
    for _ in range(3):
        s = _create(client, size=1)
        _play(client, db_session, s["session_id"], [True])
        client.post(f"/api/v1/sessions/{s['session_id']}/complete")
        completed_ids.append(s["session_id"])

    resp = client.get("/api/v1/lessons/basic.times_tables/stats")
    data = resp.json()
    recent_ids = [item["session_id"] for item in data["recent_sessions"]]
    assert recent_ids == list(reversed(completed_ids))


def test_lesson_stats_counts_problem_correct_even_after_retry(client, db_session):
    """A problem with a wrong then a right attempt should count once in total_correct."""
    from backend.app.db.models import PracticeSession

    s = _create(client, size=1)
    sid = s["session_id"]
    session = db_session.get(PracticeSession, sid)
    p = session.problems[0]
    client.post(
        f"/api/v1/sessions/{sid}/answers",
        json={"problem_id": p.id, "user_answer": p.answer + 1, "elapsed_ms": 500},
    )
    client.post(
        f"/api/v1/sessions/{sid}/answers",
        json={"problem_id": p.id, "user_answer": p.answer, "elapsed_ms": 500},
    )
    client.post(f"/api/v1/sessions/{sid}/complete")

    resp = client.get("/api/v1/lessons/basic.times_tables/stats")
    data = resp.json()
    assert data["total_problems"] == 1
    assert data["total_correct"] == 1
