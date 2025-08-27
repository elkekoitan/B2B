import uuid
from fastapi.testclient import TestClient

from app.main import app


def auth_headers():
    return {"Authorization": "Bearer mock-admin-token"}


class _MockResponse:
    def __init__(self, data=None, count=None):
        self.data = data
        self.count = count


class _Table:
    def __init__(self, name: str, db: dict):
        self.name = name
        self.db = db
        self._filters = []
        self._order = None
        self._desc = False
        self._count_mode = False

    def select(self, fields: str = "*", count: str | None = None):
        self._count_mode = count == "exact"
        return self

    def eq(self, field: str, value):
        self._filters.append(("eq", field, value))
        return self

    def order(self, field: str, desc: bool = False):
        self._order = field
        self._desc = desc
        return self

    def execute(self):
        rows = list(self.db.get(self.name, []))
        for ftype, field, value in self._filters:
            if ftype == "eq":
                rows = [r for r in rows if r.get(field) == value]
        if self._order:
            rows = sorted(rows, key=lambda r: r.get(self._order) or "", reverse=self._desc)
        return _MockResponse(rows, count=len(rows) if self._count_mode else None)

    def insert(self, data: dict):
        return _Insert(self.name, self.db, data)

    def update(self, data: dict):
        return _Update(self.name, self.db, data)

    def delete(self):
        return _Delete(self.name, self.db)


class _Insert:
    def __init__(self, name: str, db: dict, data: dict):
        self.name = name
        self.db = db
        self.data = data

    def execute(self):
        rows = self.db.setdefault(self.name, [])
        row = {**self.data}
        row.setdefault("id", str(uuid.uuid4()))
        rows.append(row)
        return _MockResponse([row])


class _Update:
    def __init__(self, name: str, db: dict, data: dict):
        self.name = name
        self.db = db
        self.data = data
        self._filters = []

    def eq(self, field: str, value):
        self._filters.append((field, value))
        return self

    def execute(self):
        rows = self.db.setdefault(self.name, [])
        updated = []
        for r in rows:
            if all(r.get(f) == v for f, v in self._filters):
                r.update(self.data)
                updated.append(dict(r))
        return _MockResponse(updated)


class _Delete:
    def __init__(self, name: str, db: dict):
        self.name = name
        self.db = db
        self._filters = []

    def eq(self, field: str, value):
        self._filters.append((field, value))
        return self

    def execute(self):
        rows = self.db.setdefault(self.name, [])
        keep = []
        for r in rows:
            if all(r.get(f) == v for f, v in self._filters):
                continue
            keep.append(r)
        self.db[self.name] = keep
        return _MockResponse([])


class _SupabaseStub:
    def __init__(self):
        self.db = {"supplier_products": []}

    def table(self, name: str):
        return _Table(name, self.db)


def test_catalog_crud_and_filters(monkeypatch):
    client = TestClient(app)

    # Patch supabase in app.main with a stub
    stub = _SupabaseStub()
    import app.main as main_mod

    monkeypatch.setattr(main_mod, "supabase", stub, raising=True)

    # Create item
    payload = {
        "product_name": "Item A",
        "category": "chem",
        "price": 10,
        "currency": "USD",
    }
    r_create = client.post("/catalog", json=payload, headers=auth_headers())
    assert r_create.status_code == 200, r_create.text
    item_id = r_create.json()["data"]["item"]["id"]

    # List mine
    r_list = client.get("/catalog/mine", headers=auth_headers())
    assert r_list.status_code == 200
    body = r_list.json()
    assert body["success"] is True
    assert body["total"] == 1
    assert body["data"][0]["product_name"] == "Item A"

    # Update
    r_upd = client.put(f"/catalog/{item_id}", json={"price": 12, "currency": "EUR"}, headers=auth_headers())
    assert r_upd.status_code == 200

    # Filters
    r_filter_cat = client.get("/catalog/mine?category=chem", headers=auth_headers())
    assert r_filter_cat.status_code == 200
    assert r_filter_cat.json()["total"] == 1

    r_filter_cur = client.get("/catalog/mine?currency=USD", headers=auth_headers())
    assert r_filter_cur.status_code == 200
    # After update, currency became EUR, so USD filter should be 0
    assert r_filter_cur.json()["total"] == 0

    # Search
    r_search = client.get("/catalog/mine?search=item", headers=auth_headers())
    assert r_search.status_code == 200
    assert r_search.json()["total"] == 1

    # Pagination: add more items
    for i in range(2):
        client.post(
            "/catalog",
            json={"product_name": f"Item {i+1}", "category": "chem"},
            headers=auth_headers(),
        )
    r_page1 = client.get("/catalog/mine?page=1&size=2", headers=auth_headers())
    r_page2 = client.get("/catalog/mine?page=2&size=2", headers=auth_headers())
    assert r_page1.status_code == 200 and r_page2.status_code == 200
    assert r_page1.json()["total"] == 3
    assert len(r_page1.json()["data"]) == 2
    assert len(r_page2.json()["data"]) == 1

    # Delete
    r_del = client.delete(f"/catalog/{item_id}", headers=auth_headers())
    assert r_del.status_code == 200
    r_list2 = client.get("/catalog/mine", headers=auth_headers())
    assert r_list2.json()["total"] == 2

