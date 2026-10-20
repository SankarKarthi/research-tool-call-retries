from __future__ import annotations

import hashlib
from typing import Any

from faults.errors import failure, success
from tools.world import World


def issue_refund(
    world: World,
    order_id: str | None = None,
    amount: float | None = None,
    task_id: str = "",
    **_: Any,
) -> dict[str, Any]:
    if not order_id:
        return failure("validation", False, "missing field: order_id")
    if amount is None:
        return failure("validation", False, "missing field: amount")
    try:
        amt = float(amount)
    except (TypeError, ValueError):
        return failure("validation", False, "amount must be a number")
    if amt <= 0:
        return failure("validation", False, "amount must be positive")

    oid = str(order_id).strip().upper()
    if not oid.startswith("ORD-"):
        oid = f"ORD-{oid.lstrip('#')}"
    key = hashlib.sha256(f"{task_id}|issue_refund|{oid}|{amt:.2f}".encode()).hexdigest()[:24]
    if key in world._idempotent:
        replay = world.remember(key, world._idempotent[key])
        return replay

    order = world.orders.get(oid)
    if not order:
        return failure("not_found", False, f"order {oid} does not exist")
    if not order.get("refundable"):
        reason = "already refunded" if order.get("status") == "refunded" else "refund not allowed for this order"
        return failure("permission", False, reason)
    if amt - 1e-6 > float(order["amount"]):
        return failure("validation", False, "refund amount exceeds order total")

    order["status"] = "refunded"
    order["refundable"] = False
    rec = {"refund_id": f"RF-{oid[-4:]}", "order_id": oid, "amount": round(amt, 2), "status": "issued"}
    world.refunds.append(rec)
    result = success(rec)
    world.remember(key, result)
    return result
