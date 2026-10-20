from tools.issue_refund import issue_refund
from tools.kb_search import kb_search
from tools.order_lookup import order_lookup
from tools.world import World


def world():
    return World.load()


def test_kb_search_return_window():
    out = kb_search(world(), query="return window")
    assert out["ok"]
    bodies = " ".join(r["body"] for r in out["data"]["results"])
    assert "30 days" in bodies


def test_order_lookup_and_refund():
    w = world()
    looked = order_lookup(w, order_id="ORD-1042")
    assert looked["data"]["found"]
    refunded = issue_refund(w, order_id="ORD-1042", amount=49.99, task_id="T019")
    assert refunded["ok"]
    again = issue_refund(w, order_id="ORD-1042", amount=49.99, task_id="T019")
    assert again["ok"]
    assert w.duplicate_actions == 1
    assert len(w.refunds) == 1


def test_blocked_refund():
    w = world()
    out = issue_refund(w, order_id="ORD-1020", amount=55.0, task_id="T027")
    assert out["ok"] is False
    assert out["error"]["category"] == "permission"
