from __future__ import annotations

import hashlib
from typing import Any

from faults.errors import failure, success
from tools.world import World


def escalate_to_human(
    world: World,
    reason: str | None = None,
    task_id: str = "",
    **_: Any,
) -> dict[str, Any]:
    if not reason or not str(reason).strip():
        return failure("validation", False, "missing field: reason")
    key = hashlib.sha256(f"{task_id}|escalate_to_human|{reason.strip().lower()}".encode()).hexdigest()[:24]
    if key in world._idempotent:
        return world.remember(key, world._idempotent[key])
    ticket_id = f"TKT-{len(world.tickets) + 1:04d}"
    rec = {"ticket_id": ticket_id, "reason": reason, "status": "open"}
    world.tickets.append(rec)
    result = success(rec)
    world.remember(key, result)
    return result
