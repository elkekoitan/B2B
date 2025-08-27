from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app


def auth_headers():
    # Uses mock-admin-token in development mode (see app/auth.py)
    return {"Authorization": "Bearer mock-admin-token"}


def test_orchestrate_queued_status():
    client = TestClient(app)

    # 1) Create a minimal valid RFQ
    deadline = (datetime.utcnow() + timedelta(days=5)).isoformat()
    rfq_payload = {
        "title": "Test RFQ",
        "description": "Test description long enough",
        "category": "chemicals",
        "quantity": 10,
        "unit": "kg",
        "budget_min": 100.0,
        "budget_max": 200.0,
        "deadline": deadline,
        "delivery_location": "Dubai",
        "requirements": "N/A",
        "priority": "medium",
    }

    r_create = client.post("/rfqs", json=rfq_payload, headers=auth_headers())
    assert r_create.status_code == 200, r_create.text
    rfq_id = r_create.json()["data"]["rfq"]["id"]

    # 2) Trigger orchestration for this RFQ
    job_payload = {"job_type": "rfq_process", "rfq_id": rfq_id, "payload": {}}
    r_orch = client.post("/orchestrate", json=job_payload, headers=auth_headers())
    assert r_orch.status_code == 200, r_orch.text
    job_id = r_orch.json()["data"]["job_id"]

    # 3) Check orchestration status
    r_status = client.get(f"/orchestrate/status/{job_id}", headers=auth_headers())
    assert r_status.status_code == 200, r_status.text
    body = r_status.json()
    assert body["success"] is True
    assert body["data"]["job"]["status"] == "queued"

