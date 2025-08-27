import types
from fastapi.testclient import TestClient


def test_health_and_info(monkeypatch):
    # Patch startup initializers to no-op
    import app.main as main

    async def _noop():
        return None

    monkeypatch.setattr(main, "init_db", _noop, raising=True)
    monkeypatch.setattr(main, "init_redis", _noop, raising=True)

    client = TestClient(main.app)

    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "healthy"

    r2 = client.get("/api/v1/info")
    assert r2.status_code == 200
    j = r2.json()
    assert j.get("name") == "Agentik B2B API"
