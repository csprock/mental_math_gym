from __future__ import annotations


def test_list_lessons_returns_registered(client):
    resp = client.get("/api/v1/lessons")
    assert resp.status_code == 200
    data = resp.json()
    ids = {entry["id"] for entry in data}
    assert "basic.times_tables" in ids
    assert "mmmg.lesson1" in ids


def test_get_lesson_detail(client):
    resp = client.get("/api/v1/lessons/basic.times_tables")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "basic.times_tables"
    assert body["title"] == "Times Tables"
    param_names = {p["name"] for p in body["params"]}
    assert param_names == {"single_digits", "exclude_tens_and_elevens"}


def test_get_unknown_lesson_returns_404(client):
    resp = client.get("/api/v1/lessons/does.not.exist")
    assert resp.status_code == 404
