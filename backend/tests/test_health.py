from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_capabilities_listed():
    r = client.get("/capabilities")
    assert r.status_code == 200
    caps = r.json()["capabilities"]
    assert isinstance(caps, list)
    assert "example-capability" in caps
