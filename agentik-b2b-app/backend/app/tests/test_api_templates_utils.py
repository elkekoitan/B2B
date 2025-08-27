from fastapi.testclient import TestClient


def _setup_client(monkeypatch):
    import app.main as main

    async def _noop():
        return None

    # Disable external init
    monkeypatch.setattr(main, "init_db", _noop, raising=True)
    monkeypatch.setattr(main, "init_redis", _noop, raising=True)

    # Override auth dependency to a permissive user
    from app.core.auth import get_current_user_profile

    def fake_user():
        return {"id": "u", "company_id": "c", "role": "admin"}

    main.app.dependency_overrides[get_current_user_profile] = fake_user
    return TestClient(main.app)


def test_rfq_templates_list_and_get(monkeypatch):
    client = _setup_client(monkeypatch)
    r = client.get("/api/v1/rfqs/templates")
    assert r.status_code == 200
    data = r.json().get("data") or r.json()
    assert isinstance(data, list)
    r2 = client.get("/api/v1/rfqs/templates/chemicals")
    assert r2.status_code == 200
    body = r2.json()
    assert body.get("category") == "chemicals"
    assert isinstance(body.get("fields"), list)


def test_utils_currency(monkeypatch):
    client = _setup_client(monkeypatch)
    r = client.get("/api/v1/utils/currency/rates")
    assert r.status_code == 200
    data = r.json().get("data")
    assert "USD" in data
    r2 = client.get("/api/v1/utils/currency/convert", params={"amount": 100, "from_currency": "USD", "to_currency": "EUR"})
    assert r2.status_code == 200
    assert r2.json().get("data", {}).get("amount")

