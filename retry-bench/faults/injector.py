from __future__ import annotations

import hashlib
import time
from typing import Any, Callable

from faults.errors import ToolError


def stable_unit(seed: int, task_id: str, tool: str, call_idx: int, salt: str = "") -> float:
    raw = f"{seed}|{task_id}|{tool}|{call_idx}|{salt}".encode()
    n = int(hashlib.sha256(raw).hexdigest()[:16], 16)
    return n / float(16**16)


class FaultInjector:
    """Deterministic wrapper: same (seed, task, tool, call_idx) always fails the same way."""

    def __init__(
        self,
        seed: int,
        rates: dict[str, float],
        enabled: bool = True,
        sleep_fn: Callable[[float], None] | None = None,
        transient_latency: dict[str, float] | None = None,
    ):
        self.seed = seed
        self.rates = rates
        self.enabled = enabled
        self.sleep_fn = sleep_fn or time.sleep
        self.transient_latency = transient_latency or {"min": 1.0, "max": 2.0}
        self._call_idx: dict[tuple[str, str], int] = {}
        self.injected: list[dict[str, Any]] = []

    def next_index(self, task_id: str, tool: str) -> int:
        key = (task_id, tool)
        idx = self._call_idx.get(key, 0)
        self._call_idx[key] = idx + 1
        return idx

    def maybe_fail(self, task_id: str, tool: str, call_idx: int) -> ToolError | None:
        if not self.enabled:
            return None
        r = stable_unit(self.seed, task_id, tool, call_idx)
        t = self.rates.get("transient", 0.0)
        v = self.rates.get("validation", 0.0)
        p = self.rates.get("permission", 0.0)
        if r < t:
            delay = self.transient_latency["min"] + stable_unit(
                self.seed, task_id, tool, call_idx, "lat"
            ) * (self.transient_latency["max"] - self.transient_latency["min"])
            self.sleep_fn(delay)
            err = ToolError("transient", True, "503 service unavailable")
        elif r < t + v:
            err = ToolError("validation", False, "missing field: order_id")
        elif r < t + v + p:
            err = ToolError("permission", False, "403 forbidden")
        else:
            return None
        self.injected.append(
            {
                "task_id": task_id,
                "tool": tool,
                "call_idx": call_idx,
                "category": err.category,
            }
        )
        return err

    def wrap(self, tool_fn: Callable[..., dict[str, Any]], task_id: str, tool: str) -> Callable[..., dict[str, Any]]:
        def wrapped(**kwargs: Any) -> dict[str, Any]:
            call_idx = self.next_index(task_id, tool)
            err = self.maybe_fail(task_id, tool, call_idx)
            if err is not None:
                raise err
            return tool_fn(**kwargs)

        return wrapped
