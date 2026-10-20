from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class EventLogger:
    def __init__(self, path: Path, meta: dict[str, Any]):
        self.path = path
        self.meta = meta
        self.events: list[dict[str, Any]] = []
        self.wasted_retries = 0
        self.retries_total = 0
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def event(self, event: str, **fields: Any) -> None:
        row = {
            **self.meta,
            "event": event,
            "ts": time.time(),
            **{k: v for k, v in fields.items() if v is not None},
        }
        self.events.append(row)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")

    def add_wasted(self, n: int) -> None:
        self.wasted_retries += n

    def add_retry(self) -> None:
        self.retries_total += 1

    def tool_calls(self) -> list[dict[str, Any]]:
        return [e for e in self.events if e["event"] == "tool_call"]

    def llm_calls(self) -> list[dict[str, Any]]:
        return [e for e in self.events if e["event"] == "llm_call"]
