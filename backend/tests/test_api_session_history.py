from __future__ import annotations


def _create(client, lesson_id="basic.times_tables", size=3, params=None):
    body = {"lesson_id": lesson_id, "size": size, "params": params or {}}
    resp = client.post("/api/v1/sessions", json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _answer(client, session_id, problem_id, user_answer, elapsed_ms=500):
    return client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={
            "problem_id": problem_id,
            "user_answer": user_answer,
            "elapsed_ms": elapsed_ms,
        },
    )


def test_list_sessions_empty(client):
    resp = client.get("/api/v1/sessions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_sessions_newest_first(client):
    a = _create(client, size=2)
    b = _create(client, size=3)
    c = _create(client, size=4)

    resp = client.get("/api/v1/sessions")
    assert resp.status_code == 200
    items = resp.json()
    ids = [item["session_id"] for item in items]
    assert ids == [c["session_id"], b["session_id"], a["session_id"]]
    assert items[0]["total_problems"] == 4
    assert items[0]["status"] == "created"


def test_list_sessions_filter_by_lesson(client):
    _create(client, lesson_id="basic.times_tables", size=2)
    _create(client, lesson_id="basic.addition_tables", size=3)
    _create(client, lesson_id="basic.times_tables", size=4)

    resp = client.get(
        "/api/v1/sessions", params={"lesson_id": "basic.times_tables"}
    )
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    assert all(item["lesson_id"] == "basic.times_tables" for item in items)


def test_list_sessions_filter_by_status(client, db_session):
    from backend.app.db.models import PracticeSession

    a = _create(client, size=1)
    b = _create(client, size=1)

    # complete b
    client.post(f"/api/v1/sessions/{b['session_id']}/complete")

    resp = client.get("/api/v1/sessions", params={"status": "completed"})
    assert resp.status_code == 200
    ids = [item["session_id"] for item in resp.json()]
    assert ids == [b["session_id"]]

    resp = client.get("/api/v1/sessions", params={"status": "created"})
    assert resp.status_code == 200
    ids = [item["session_id"] for item in resp.json()]
    assert ids == [a["session_id"]]


def test_list_sessions_pagination(client):
    ids = [_create(client, size=1)["session_id"] for _ in range(5)]
    ids_desc = list(reversed(ids))

    resp = client.get("/api/v1/sessions", params={"limit": 2, "offset": 0})
    page1 = [item["session_id"] for item in resp.json()]
    assert page1 == ids_desc[:2]

    resp = client.get("/api/v1/sessions", params={"limit": 2, "offset": 2})
    page2 = [item["session_id"] for item in resp.json()]
    assert page2 == ids_desc[2:4]


def test_list_sessions_rejects_bad_status(client):
    resp = client.get("/api/v1/sessions", params={"status": "nope"})
    assert resp.status_code == 422


def test_get_session_detail_unknown_404(client):
    resp = client.get("/api/v1/sessions/9999")
    assert resp.status_code == 404


def test_get_session_detail_hides_answer_before_completion(client, db_session):
    body = _create(client, size=2)
    sid = body["session_id"]

    # created: no answer
    resp = client.get(f"/api/v1/sessions/{sid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "created"
    # params are normalized (defaults filled in), not echoed raw
    assert set(data["params"].keys()) == {"single_digits", "exclude_tens_and_elevens"}
    for p in data["problems"]:
        assert p["answer"] is None
        assert p["attempts"] == []
    assert data["summary"]["total_problems"] == 2
    assert data["summary"]["correct_problems"] == 0

    # still hidden while in_progress
    from backend.app.db.models import PracticeSession

    session = db_session.get(PracticeSession, sid)
    p0 = session.problems[0]
    _answer(client, sid, p0.id, p0.answer + 1, elapsed_ms=400)

    resp = client.get(f"/api/v1/sessions/{sid}")
    data = resp.json()
    assert data["status"] == "in_progress"
    for p in data["problems"]:
        assert p["answer"] is None
    # attempt visible on that problem
    prob0 = next(p for p in data["problems"] if p["id"] == p0.id)
    assert len(prob0["attempts"]) == 1
    assert prob0["attempts"][0]["is_correct"] is False


def test_get_session_detail_reveals_answer_after_complete(client, db_session):
    from backend.app.db.models import PracticeSession

    body = _create(client, size=1)
    sid = body["session_id"]
    session = db_session.get(PracticeSession, sid)
    p = session.problems[0]
    _answer(client, sid, p.id, p.answer)
    client.post(f"/api/v1/sessions/{sid}/complete")

    resp = client.get(f"/api/v1/sessions/{sid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["problems"][0]["answer"] == p.answer
    assert data["summary"]["correct_problems"] == 1
    assert data["summary"]["score"] == 1.0


def test_retry_missed_creates_session_with_only_missed_problems(client, db_session):
    from backend.app.db.models import PracticeSession

    body = _create(client, size=3)
    sid = body["session_id"]
    session = db_session.get(PracticeSession, sid)

    # first right, second wrong, third wrong
    _answer(client, sid, session.problems[0].id, session.problems[0].answer)
    _answer(client, sid, session.problems[1].id, session.problems[1].answer + 1)
    _answer(client, sid, session.problems[2].id, session.problems[2].answer + 2)
    client.post(f"/api/v1/sessions/{sid}/complete")

    missed_prompts = {session.problems[1].prompt, session.problems[2].prompt}

    resp = client.post(f"/api/v1/sessions/{sid}/retry-missed")
    assert resp.status_code == 201, resp.text
    new = resp.json()
    assert new["status"] == "created"
    assert new["lesson_id"] == session.lesson_id
    assert len(new["problems"]) == 2
    assert [p["ordinal"] for p in new["problems"]] == [1, 2]
    assert {p["prompt"] for p in new["problems"]} == missed_prompts
    assert new["session_id"] != sid


def test_retry_missed_rejected_when_no_misses(client, db_session):
    from backend.app.db.models import PracticeSession

    body = _create(client, size=1)
    sid = body["session_id"]
    session = db_session.get(PracticeSession, sid)
    _answer(client, sid, session.problems[0].id, session.problems[0].answer)
    client.post(f"/api/v1/sessions/{sid}/complete")

    resp = client.post(f"/api/v1/sessions/{sid}/retry-missed")
    assert resp.status_code == 400
    assert "no missed" in resp.text.lower()


def test_retry_missed_rejected_when_source_not_completed(client, db_session):
    body = _create(client, size=1)
    sid = body["session_id"]

    resp = client.post(f"/api/v1/sessions/{sid}/retry-missed")
    assert resp.status_code == 400
    assert "complete" in resp.text.lower()


def test_retry_missed_unknown_session_404(client):
    resp = client.post("/api/v1/sessions/9999/retry-missed")
    assert resp.status_code == 404


def test_retry_missed_preserves_params(client, db_session):
    from backend.app.db.models import PracticeSession

    body = _create(
        client, size=1, params={"single_digits": True, "exclude_tens_and_elevens": True}
    )
    sid = body["session_id"]
    session = db_session.get(PracticeSession, sid)
    _answer(client, sid, session.problems[0].id, session.problems[0].answer + 1)
    client.post(f"/api/v1/sessions/{sid}/complete")

    resp = client.post(f"/api/v1/sessions/{sid}/retry-missed")
    assert resp.status_code == 201
    new_id = resp.json()["session_id"]

    detail = client.get(f"/api/v1/sessions/{new_id}").json()
    assert detail["params"] == {
        "single_digits": True,
        "exclude_tens_and_elevens": True,
    }
