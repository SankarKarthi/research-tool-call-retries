from __future__ import annotations

import re
from typing import Any

from faults.errors import failure, success
from tools.world import World


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def web_search(world: World, query: str | None = None, **_: Any) -> dict[str, Any]:
    if not query or not str(query).strip():
        return failure("validation", False, "missing field: query")
    q = _tokens(str(query))
    scored = []
    for row in world.web_results:
        hay = _tokens(row["query"] + " " + row["title"] + " " + row["snippet"])
        score = len(q & hay)
        scored.append((score, row))
    scored.sort(key=lambda x: (-x[0], x[1]["title"]))
    top = [{"title": r["title"], "snippet": r["snippet"], "url": r["url"]} for _, r in scored[:3]]
    return success({"results": top})
