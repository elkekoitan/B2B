from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app


def auth_headers():
    return {"Authorization": "Bearer mock-admin-token"}


def test_rfq_list_pagination_with_filters():
    client = TestClient(app)

    # Clean up previous RFQs to ensure a clean slate for counting
    all_rfqs_res = client.get("/rfqs?size=100", headers=auth_headers())
    if all_rfqs_res.status_code == 200:
        for rfq in all_rfqs_res.json().get("data", {}).get("data", []):
            # This assumes a delete endpoint exists and works, which is not ideal for this test.
            # A better approach would be to use a test database that is reset for each run.
            # Since I cannot guarantee a delete endpoint, I will proceed, but this is a known fragility.
            # The bug is in the GET endpoint, so this part is just for setup.
            # The DELETE endpoint is implemented in rfq.py, but it does a soft delete.
            # This is fine for this test.
            client.delete(f"/rfqs/{rfq['id']}", headers=auth_headers())


    future = (datetime.utcnow() + timedelta(days=5)).isoformat()
    # Create 3 RFQs for 'electronics'
    for i in range(3):
        rfq = {
            "title": f"Electronics RFQ {i}",
            "category": "electronics",
            "quantity": 10,
            "unit": "pieces",
            "deadline": future,
            "delivery_location": "Dubai",
        }
        r = client.post("/rfqs", json=rfq, headers=auth_headers())
        assert r.status_code == 200

    # Create 2 RFQs for 'chemicals'
    for i in range(2):
        rfq = {
            "title": f"Chemicals RFQ {i}",
            "category": "chemicals",
            "quantity": 50,
            "unit": "kg",
            "deadline": future,
            "delivery_location": "USA",
        }
        r = client.post("/rfqs", json=rfq, headers=auth_headers())
        assert r.status_code == 200

    # List RFQs with category filter
    res = client.get("/rfqs?category=electronics", headers=auth_headers())
    assert res.status_code == 200
    data = res.json()

    # The bug is that 'total' will be 5, but it should be 3.
    # The returned data list will have 3 items, but the total count will be wrong.
    assert data["success"] is True
    assert len(data["data"]["data"]) == 3
    assert data["data"]["total"] == 3
    assert all(item["category"] == "electronics" for item in data["data"]["data"])
