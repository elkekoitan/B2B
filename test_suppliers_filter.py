from fastapi.testclient import TestClient

from app.main import app


def auth_headers():
    return {"Authorization": "Bearer mock-admin-token"}


def test_suppliers_filter_category_and_verified():
    client = TestClient(app)

    # list suppliers (mock db may be empty). This is primarily a sanity check for filters.
    res = client.get("/suppliers?category=chemicals&verified_only=true&per_page=10", headers=auth_headers())
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    # Data may be empty in mock, but should be a list
    assert isinstance(body.get("data", []), list)

