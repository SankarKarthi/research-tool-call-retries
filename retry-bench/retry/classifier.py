from __future__ import annotations

from typing import Any

from faults.errors import ToolError


RETRYABLE_BY_DEFAULT = {
    "transient": True,
    "validation": False,
    "permission": False,
    "not_found": False,
    "partial": True,
}


def classify(error: Any) -> tuple[str, bool, str, dict[str, Any] | None]:
    """Map an exception or error payload to (category, retryable, message, data)."""
    if isinstance(error, ToolError):
        return error.category, error.retryable, error.message, error.data
    if isinstance(error, dict):
        inner = error.get("error", error)
        if isinstance(inner, dict) and inner.get("category"):
            cat = str(inner["category"])
            retryable = bool(inner.get("retryable", RETRYABLE_BY_DEFAULT.get(cat, False)))
            return cat, retryable, str(inner.get("message", "tool error")), inner.get("data")
    # Unknown errors: do not retry.
    return "permission", False, str(error), None
