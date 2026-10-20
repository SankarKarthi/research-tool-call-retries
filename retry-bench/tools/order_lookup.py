from __future__ import annotations

from typing import Any

from faults.errors import failure, success
from tools.world import World


def order_lookup(world: World, order_id: str | None = None, **_: Any) -> dict[str, Any]:
    if not order_id or not str(order_id).strip():
        return failure("validation", False, "missing field: order_id")
    oid = str(order_id).strip().upper()
    if not oid.startswith("ORD-"):
        oid = f"ORD-{oid.lstrip('#')}"
    order = world.orders.get(oid)
    if not order:
        return success({"found": False, "order": None})
    customer = world.customers.get(order["customer_id"], {})
    return success({"found": True, "order": {**order, "customer_name": customer.get("name")}})
