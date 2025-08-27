from app.core.permissions import has_permission
from app.services.currency import convert
from app.services import rfq_templates


def test_permissions_matrix():
    assert has_permission("admin", "anything")
    assert has_permission("buyer", "rfq:create")
    assert not has_permission("supplier", "rfq:delete")


def test_currency_convert_roundtrip():
    amount = convert(100, "USD", "EUR")
    assert amount > 0
    back = convert(amount, "EUR", "USD")
    assert 90 <= back <= 110  # allow coarse tolerance due to default rates


def test_rfq_templates_list_and_get():
    lst = rfq_templates.list_templates()
    assert any(x["category"] == "chemicals" for x in lst)
    tpl = rfq_templates.get_template("chemicals")
    assert tpl["category"] == "chemicals"
    assert any(f["required"] for f in tpl["fields"])  # at least one required field

