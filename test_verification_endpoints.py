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


class _Insert:
    def __init__(self, name: str, db: dict, data: dict):
        self.name = name
        self.db = db
        self.data = data

    def execute(self):
        rows = self.db.setdefault(self.name, [])
        row = {**self.data}
        if "id" not in row:
            row["id"] = str(uuid.uuid4())
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


class _SupabaseStub:
    def __init__(self):
        self.db = {"verification_requests": []}

    def table(self, name: str):
        return _Table(name, self.db)


def test_verification_request_list_approve(monkeypatch):
    client = TestClient(app)
    import app.main as main_mod
    stub = _SupabaseStub()
    monkeypatch.setattr(main_mod, "supabase", stub, raising=True)

    # Request verification
    body = {
        "documents": [
            {"file_name": "cert.pdf", "file_path": "/tmp/cert.pdf", "file_type": "verification"}
        ],
        "notes": "Please verify",
    }
    r_req = client.post("/verification/request", json=body, headers=auth_headers())
    assert r_req.status_code == 200
    company_id = r_req.json()["data"]["request"]["company_id"]

    # List requests
    r_list = client.get("/verification/requests?page=1&size=10", headers=auth_headers())
    assert r_list.status_code == 200
    items = r_list.json()["data"]["items"]
    assert len(items) == 1
    assert items[0]["data"]["company_id"] == company_id

    # Approve
    r_app = client.post("/verification/approve", json={"company_id": company_id}, headers=auth_headers())
    assert r_app.status_code == 200

    # Now pending list should be empty
    r_list2 = client.get("/verification/requests?page=1&size=10", headers=auth_headers())
    assert r_list2.status_code == 200
    assert len(r_list2.json()["data"]["items"]) == 0

