from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(name: str) -> Any:
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


@dataclass
class World:
    customers: dict[str, dict[str, Any]]
    orders: dict[str, dict[str, Any]]
    kb_articles: list[dict[str, Any]]
    web_results: list[dict[str, Any]]
    refunds: list[dict[str, Any]] = field(default_factory=list)
    tickets: list[dict[str, Any]] = field(default_factory=list)
    tools_called: list[str] = field(default_factory=list)
    duplicate_actions: int = 0
    _idempotent: dict[str, dict[str, Any]] = field(default_factory=dict)

    @classmethod
    def load(cls) -> "World":
        customers = {c["id"]: c for c in _load("customers.json")}
        orders = {o["id"]: o for o in _load("orders.json")}
        return cls(
            customers=customers,
            orders=orders,
            kb_articles=_load("kb_articles.json"),
            web_results=_load("web_results.json"),
        )

    def clone(self) -> "World":
        return copy.deepcopy(self)

    def remember(self, key: str, result: dict[str, Any]) -> dict[str, Any]:
        if key in self._idempotent:
            self.duplicate_actions += 1
            return self._idempotent[key]
        self._idempotent[key] = result
        return result
