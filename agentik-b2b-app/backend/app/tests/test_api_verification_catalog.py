from fastapi.testclient import TestClient


class MockResult:
    def __init__(self, data=None, count=None):
        self.data = data
        self.count = count


class MockQuery:
    def __init__(self, table_name: str, store: dict):
        self.table_name = table_name
        self.store = store
        self._filters = []
        self._order = None
        self._range = (0, 0)
        self._selected = []
        self._single = False

    # chainable ops
    def select(self, *args, **kwargs):
        self._selected = list(args)
        return self

    def eq(self, field, value):
        self._filters.append((field, value))
        return self

    def order(self, field, desc=False):
        self._order = (field, desc)
        return self

    def range(self, start, end):
        self._range = (start, end)
        return self

    def in_(self, field, values):
        return self

    def single(self):
        self._single = True
        return self

    def execute(self):
        items = self.store.get(self.table_name, [])
        if self.table_name == "notifications":
            # filter by type if present
            for f, v in self._filters:
                if f == "type":
                    items = [x for x in items if x.get("type") == v]
        # basic id filter support
        for f, v in self._filters:
            if f == "id":
                items = [x for x in items if str(x.get("id")) == str(v)]
        if self._order:
            field, desc = self._order
            items = sorted(items, key=lambda x: x.get(field), reverse=desc)
        start, end = self._range
        if end > start:
            items = items[start : end + 1]
        # simulate join suppliers(company_id)
        if self.table_name == "supplier_products" and items and any(
            isinstance(f, str) and f.startswith("suppliers(") for f in self._selected
        ):
            suppliers = {s["id"]: s for s in self.store.get("suppliers", [])}
            tmp = []
            for it in items:
                sup = suppliers.get(it.get("supplier_id"), {})
                it2 = dict(it)
                it2["suppliers"] = {"company_id": sup.get("company_id")}
                tmp.append(it2)
            items = tmp
        if self._single:
            return MockResult(data=items[0] if items else None, count=len(items))
        return MockResult(data=items, count=len(self.store.get(self.table_name, [])))


class MockDB:
    def __init__(self, store: dict):
        self.store = store

    def table(self, name: str):
        return MockQuery(name, self.store)


def _client_with_overrides(monkeypatch, store: dict):
    import app.main as main

    async def _noop():
        return None

    # Disable real init
    monkeypatch.setattr(main, "init_db", _noop, raising=True)
    monkeypatch.setattr(main, "init_redis", _noop, raising=True)

    # Override deps
    from app.core.auth import get_current_user_profile
    from app.core.database import get_db

    def fake_user():
        return {"id": "u", "company_id": "c", "role": "admin"}

    def fake_db():
        return MockDB(store)

    main.app.dependency_overrides[get_current_user_profile] = fake_user
    main.app.dependency_overrides[get_db] = fake_db
    return TestClient(main.app)


def test_verification_requests_listing(monkeypatch):
    store = {
        "notifications": [
            {"id": "n1", "type": "verification_request", "title": "Req", "message": "m", "created_at": "2025-01-01"}
        ]
    }
    client = _client_with_overrides(monkeypatch, store)
    r = client.get("/api/v1/verification/requests")
    assert r.status_code == 200
    body = r.json()
    assert body.get("success") is True
    assert len(body["data"]["items"]) == 1


def test_catalog_create(monkeypatch):
    # Simulate suppliers and supplier_products insert
    class CatalogMockQuery(MockQuery):
        def insert(self, data):
            items = self.store.setdefault(self.table_name, [])
            if isinstance(data, list):
                items.extend(data)
            else:
                items.append(data)
            return MockResult(data=[{"id": "p1"}])

        def update(self, data):
            target_id = None
            for f, v in self._filters:
                if f == "id":
                    target_id = str(v)
            updated = None
            if target_id:
                for it in self.store.get(self.table_name, []):
                    if str(it.get("id")) == target_id:
                        it.update(data)
                        updated = dict(it)
                        break
            return MockResult(data=[updated] if updated else [])

        def delete(self):
            target_id = None
            for f, v in self._filters:
                if f == "id":
                    target_id = str(v)
            if target_id:
                self.store[self.table_name] = [it for it in self.store.get(self.table_name, []) if str(it.get("id")) != target_id]
            return MockResult(data=[{"deleted": True}])

    class CatalogMockDB(MockDB):
        def table(self, name: str):
            q = CatalogMockQuery(name, self.store)
            return q

    import app.main as main

    async def _noop():
        return None

    monkeypatch.setattr(main, "init_db", _noop, raising=True)
    monkeypatch.setattr(main, "init_redis", _noop, raising=True)

    from app.core.auth import get_current_user_profile
    from app.core.database import get_db

    def fake_user():
        return {"id": "u", "company_id": "c", "role": "admin"}

    store = {
        "suppliers": [{"id": "s1", "company_id": "c"}],
        "supplier_products": [],
    }

    def fake_db():
        return CatalogMockDB(store)

    main.app.dependency_overrides[get_current_user_profile] = fake_user
    main.app.dependency_overrides[get_db] = fake_db
    client = TestClient(main.app)

    payload = {"product_name": "P", "category": "chem", "price": 10, "currency": "USD", "supplier_id": "s1"}
    r = client.post("/api/v1/catalog", json=payload)
    assert r.status_code == 200
    assert r.json().get("success") is True


def test_catalog_update_and_delete(monkeypatch):
    # Prepare store with a supplier and a product
    store = {
        "suppliers": [{"id": "s1", "company_id": "c"}],
        "supplier_products": [
            {"id": "p1", "supplier_id": "s1", "product_name": "Old", "category": "chem", "price": 10, "currency": "USD"}
        ],
    }

    import app.main as main

    async def _noop():
        return None

    monkeypatch.setattr(main, "init_db", _noop, raising=True)
    monkeypatch.setattr(main, "init_redis", _noop, raising=True)

    from app.core.auth import get_current_user_profile
    from app.core.database import get_db

    def fake_user():
        return {"id": "u", "company_id": "c", "role": "admin"}

    class CatalogMockDB(MockDB):
        def table(self, name: str):
            return CatalogMockQuery(name, store)

    def fake_db():
        return CatalogMockDB(store)

    main.app.dependency_overrides[get_current_user_profile] = fake_user
    main.app.dependency_overrides[get_db] = fake_db

    client = TestClient(main.app)

    # Update
    r_up = client.put("/api/v1/catalog/p1", json={"product_name": "New", "price": 12})
    assert r_up.status_code == 200
    body_up = r_up.json()
    assert body_up.get("success") is True
    assert body_up["data"]["product_name"] == "New"
    assert body_up["data"]["price"] == 12

    # Delete
    r_del = client.delete("/api/v1/catalog/p1")
    assert r_del.status_code == 200
    body_del = r_del.json()
    assert body_del.get("success") is True

    # Verify list is empty now
    r_list = client.get("/api/v1/catalog/mine")
    assert r_list.status_code == 200
    assert len(r_list.json()["data"]["data"]) == 0
