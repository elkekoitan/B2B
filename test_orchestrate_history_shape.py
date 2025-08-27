from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app


def auth_headers():
    # Uses mock-admin-token in development mode (see app/auth.py)
    return {"Authorization": "Bearer mock-admin-token"}


def test_orchestrate_history_shape():
    client = TestClient(app)

    # Create a minimal valid RFQ (best-effort; history does not depend on it)
    deadline = (datetime.utcnow() + timedelta(days=3)).isoformat()
    rfq_payload = {
        "title": "History Shape RFQ",
        "description": "desc long enough",
        "category": "chemicals",
        "quantity": 1,
        "unit": "kg",
        "deadline": deadline,
        "delivery_location": "Dubai",
    }
    client.post("/rfqs", json=rfq_payload, headers=auth_headers())

    # Call history endpoint and assert shape
    r = client.get("/orchestrate/history?limit=5", headers=auth_headers())
    assert r.status_code == 200, r.text
    body = r.json()
    assert body.get("success") is True
    data = body.get("data") or {}
    assert "jobs" in data
    assert isinstance(data.get("jobs"), list)

