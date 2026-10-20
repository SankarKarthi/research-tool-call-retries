from __future__ import annotations

from typing import Any


def evaluate(task: dict[str, Any], world, final_text: str, status: str) -> dict[str, Any]:
    expected = task.get("expected", {})
    reasons: list[str] = []

    if status == "timeout":
        return _fail("timeout", reasons)
    if status == "max_steps":
        return _fail("max_steps", reasons)

    called = set(world.tools_called)
    for name in expected.get("must_call", []):
        if name not in called:
            reasons.append(f"missing tool {name}")
    for name in expected.get("must_not_call", []):
        if name in called:
            reasons.append(f"forbidden tool {name}")

    fs = expected.get("final_state", {})
    if "refund_issued" in fs:
        order_id = fs.get("order_id")
        refunds = [r for r in world.refunds if not order_id or r["order_id"] == order_id]
        if fs["refund_issued"]:
            if not refunds:
                reasons.append("expected a refund")
            elif fs.get("amount") is not None and abs(float(refunds[0]["amount"]) - float(fs["amount"])) > 0.01:
                reasons.append("refund amount mismatch")
        elif refunds:
            reasons.append("refund was not allowed")

    if "escalated" in fs:
        if bool(world.tickets) != bool(fs["escalated"]):
            reasons.append("escalation mismatch")

    max_dup = expected.get("max_duplicate_actions", 0)
    if world.duplicate_actions > max_dup:
        return _fail("duplicate_action", reasons + ["duplicate side effect"])

    text = (final_text or "").lower()
    for kw in expected.get("answer_contains", []):
        if kw.lower() not in text:
            reasons.append(f"missing phrase {kw!r}")
    any_kws = expected.get("answer_contains_any", [])
    if any_kws and not any(kw.lower() in text for kw in any_kws):
        reasons.append(f"missing any of {any_kws}")

    if reasons:
        if any("forbidden" in r or "refund was not allowed" in r for r in reasons):
            return _fail("wrong_action", reasons)
        if any(r.startswith("missing tool") or r.startswith("expected") or r.startswith("escalation") for r in reasons):
            return _fail("wrong_action", reasons)
        if any(r.startswith("missing phrase") or r.startswith("missing any") for r in reasons):
            return _fail("wrong_answer", reasons)
        return _fail("wrong_action", reasons)

    return {"success": True, "failure_reason": None, "detail": []}


def _fail(reason: str, details: list[str]) -> dict[str, Any]:
    return {"success": False, "failure_reason": reason, "detail": details}
