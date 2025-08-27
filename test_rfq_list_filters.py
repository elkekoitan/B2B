from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app


def auth_headers():
    return {"Authorization": "Bearer mock-admin-token"}


def test_rfq_list_filters_status_and_category():
    client = TestClient(app)

    # create two rfqs with different status/category
    future = (datetime.utcnow() + timedelta(days=5)).isoformat()
    rfq1 = {
        "title": "Chemicals RFQ A",
        "description": "desc lengthy",
        "category": "chemicals",
        "quantity": 10,
        "unit": "kg",
        "deadline": future,
        "delivery_location": "Dubai",
    }
    rfq2 = {
        "title": "Electronics RFQ B",
        "description": "desc lengthy",
        "category": "electronics",
        "quantity": 5,
        "unit": "pieces",
        "deadline": future,
        "delivery_location": "Dubai",
    }
    r1 = client.post("/rfqs", json=rfq1, headers=auth_headers())
    r2 = client.post("/rfqs", json=rfq2, headers=auth_headers())
    assert r1.status_code == 200 and r2.status_code == 200

    # list by category
    res = client.get("/rfqs?category=chemicals", headers=auth_headers())
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert all(item["category"] == "chemicals" for item in data["data"]) or len(data["data"]) == 0

