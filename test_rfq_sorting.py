from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app


def auth_headers():
    return {"Authorization": "Bearer mock-admin-token"}


def test_rfq_sorting_created_at():
    client = TestClient(app)
    future = (datetime.utcnow() + timedelta(days=10)).isoformat()

    # create two rfqs sequentially
    rfqA = {
        "title": "Sort Test A",
        "description": "AAAAA description long",
        "category": "chemicals",
        "quantity": 1,
        "unit": "kg",
        "deadline": future,
        "delivery_location": "Dubai",
    }
    rfqB = {
        "title": "Sort Test B",
        "description": "BBBBB description long",
        "category": "chemicals",
        "quantity": 1,
        "unit": "kg",
        "deadline": future,
        "delivery_location": "Dubai",
    }
    r1 = client.post("/rfqs", json=rfqA, headers=auth_headers())
    r2 = client.post("/rfqs", json=rfqB, headers=auth_headers())
    assert r1.status_code == 200 and r2.status_code == 200

    # desc: B should come before A when titles are identical category
    res_desc = client.get("/rfqs?sort_by=created_at&sort_dir=desc&category=chemicals&per_page=5", headers=auth_headers())
    assert res_desc.status_code == 200
    data_desc = res_desc.json()["data"]
    ids_desc = [item["id"] for item in data_desc]

    # asc: A should come before B
    res_asc = client.get("/rfqs?sort_by=created_at&sort_dir=asc&category=chemicals&per_page=5", headers=auth_headers())
    assert res_asc.status_code == 200
    data_asc = res_asc.json()["data"]
    ids_asc = [item["id"] for item in data_asc]

    # sanity: orders should be reverse of each other for same filter
    assert ids_desc[:2] == list(reversed(ids_asc[:2]))

