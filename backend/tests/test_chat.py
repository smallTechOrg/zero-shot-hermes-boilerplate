from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_stub():
    r = client.post("/api/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code == 200
    body = r.json()
    assert "reply" in body
    assert "run_id" in body
    assert isinstance(body["run_id"], int)


def test_chat_creates_run():
    r = client.post("/api/chat", json={"messages": [{"role": "user", "content": "save me"}]})
    assert r.status_code == 200
    run_id = r.json().get("run_id")
    assert isinstance(run_id, int)


def test_runs_endpoints():
    r = client.get("/api/runs")
    assert r.status_code == 200
    body = r.json()
    assert "runs" in body
    assert isinstance(body["runs"], list)


def test_goal_loop():
    r = client.post(
        "/goals",
        json={"goal_text": "demo", "steps": [{"description": "step 1"}, {"description": "step 2"}]},
    )
    assert r.status_code == 200
    goal_id = r.json()["goal_id"]
    r2 = client.post(f"/goals/{goal_id}/run")
    assert r2.status_code == 200
    body = r2.json()
    assert body["status"] == "succeeded"
    assert body["step_index"] == 2
