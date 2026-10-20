from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CATEGORIES = ("transient", "validation", "permission", "not_found", "partial")


@dataclass
class ToolError(Exception):
    category: str
    retryable: bool
    message: str
    data: dict[str, Any] | None = None

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "category": self.category,
            "retryable": self.retryable,
            "message": self.message,
        }
        if self.data:
            payload["data"] = self.data
        return payload

    def to_result(self) -> dict[str, Any]:
        return {"ok": False, "error": self.to_payload()}


def success(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data}


def failure(category: str, retryable: bool, message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    return ToolError(category, retryable, message, data).to_result()
