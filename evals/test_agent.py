"""Evals for the demo-agent boilerplate.

Run:
    backend/.venv/bin/python -m pytest evals/ -v

- test_behaviour_* run in stub mode (no API key needed).
- test_live_chat is skipped unless GEMINI_API_KEY (or LLM_API_KEY) is set in the
  environment — it actually calls the configured provider and asserts a real reply.
"""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config import settings

client = TestClient(app)


def test_behaviour_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_behaviour_chat_returns_reply():
    r = client.post("/api/chat", json={"messages": [{"role": "user", "content": "ping"}]})
    assert r.status_code == 200
    body = r.json()
    assert "reply" in body
    assert body["run_id"] is not None


def test_behaviour_chat_persists_run():
    r = client.post("/api/chat", json={"messages": [{"role": "user", "content": "remember this"}]})
    run_id = r.json()["run_id"]
    rr = client.get(f"/api/runs/{run_id}")
    assert rr.status_code == 200
    assert rr.json()["status"] in {"succeeded", "error"}


def test_behaviour_goal_loop_completes():
    r = client.post(
        "/goals",
        json={"goal_text": "demo", "steps": [{"description": "step one"}, {"description": "step two"}]},
    )
    goal_id = r.json()["goal_id"]
    rr = client.post(f"/goals/{goal_id}/run")
    assert rr.status_code == 200
    body = rr.json()
    assert body["status"] == "succeeded"
    assert body["step_index"] == 2


@pytest.mark.skipif(
    not (os.getenv("GEMINI_API_KEY") or settings.resolved_api_key),
    reason="no API key set; skipping live provider call",
)
def test_live_chat():
    r = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Say hello in 3 words."}]})
    assert r.status_code == 200
    reply = r.json()["reply"]
    assert reply and not reply.startswith("[stub]")
