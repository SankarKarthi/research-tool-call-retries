from types import SimpleNamespace

from bench.evaluator import evaluate


def test_kb_success():
    world = SimpleNamespace(tools_called=["kb_search"], refunds=[], tickets=[], duplicate_actions=0)
    task = {"expected": {"must_call": ["kb_search"], "answer_contains": ["30 days"]}}
    out = evaluate(task, world, "Our return window is 30 days.", "completed")
    assert out["success"]


def test_duplicate_is_failure():
    world = SimpleNamespace(tools_called=["issue_refund"], refunds=[{"order_id": "ORD-1042", "amount": 49.99}], tickets=[], duplicate_actions=1)
    task = {"expected": {"final_state": {"refund_issued": True, "order_id": "ORD-1042", "amount": 49.99}, "max_duplicate_actions": 0}}
    out = evaluate(task, world, "Refunded.", "completed")
    assert out["success"] is False
    assert out["failure_reason"] == "duplicate_action"
