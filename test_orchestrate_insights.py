from fastapi.testclient import TestClient

from app.main import app


def auth_headers():
    # Uses mock-admin-token in development mode (see app/auth.py)
    return {"Authorization": "Bearer mock-admin-token"}


def test_orchestrate_queues_snapshot():
    client = TestClient(app)
    r = client.get("/orchestrate/queues", headers=auth_headers())
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    data = body.get("data") or {}
    assert "main" in data
    assert isinstance(data.get("main"), int)
    assert "agents" in data
    assert isinstance(data.get("agents"), dict)


def test_orchestrate_heartbeat_shape():
    client = TestClient(app)
    r = client.get("/orchestrate/heartbeat", headers=auth_headers())
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    data = body.get("data") or {}
    # available may be False if orchestrator isn't running; just assert shape
    assert "available" in data
    assert "heartbeat" in data

