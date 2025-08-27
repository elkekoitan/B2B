from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app


def auth_headers():
    return {"Authorization": "Bearer mock-admin-token"}


def test_recent_and_cancel_flow():
    client = TestClient(app)

    # create RFQ
    deadline = (datetime.utcnow() + timedelta(days=3)).isoformat()
    rfq = {
        "title": "Job Cancel Test",
        "description": "desc long enough for validation",
        "category": "chemicals",
        "quantity": 5,
        "unit": "kg",
        "deadline": deadline,
        "delivery_location": "Dubai",
    }
    r = client.post("/rfqs", json=rfq, headers=auth_headers())
    assert r.status_code == 200
    rfq_id = r.json()["data"]["rfq"]["id"]

    # start job
    body = {"job_type": "rfq_process", "rfq_id": rfq_id}
    r2 = client.post("/orchestrate", json=body, headers=auth_headers())
    assert r2.status_code == 200
    job_id = r2.json()["data"]["job_id"]

    # recent with filter
    r3 = client.get("/orchestrate/recent?limit=10&job_type=rfq_process", headers=auth_headers())
    assert r3.status_code == 200
    jobs = r3.json()["data"]["jobs"]
    assert any((j.get("job_id") or j.get("id")) == job_id for j in jobs)

    # cancel
    r4 = client.delete(f"/orchestrate/{job_id}", headers=auth_headers())
    assert r4.status_code == 200

    # status should be failed/cancelled
    r5 = client.get(f"/orchestrate/status/{job_id}", headers=auth_headers())
    assert r5.status_code == 200
    job = r5.json()["data"]["job"]
    assert job["status"] in ("failed", "cancelled")
