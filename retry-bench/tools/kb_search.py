from __future__ import annotations

import re
from typing import Any

from faults.errors import failure, success
from tools.world import World


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 2}


def kb_search(world: World, query: str | None = None, **_: Any) -> dict[str, Any]:
    if not query or not str(query).strip():
        return failure("validation", False, "missing field: query")
    q = _tokens(str(query))
    scored = []
    for art in world.kb_articles:
        hay = _tokens(art["title"] + " " + art["body"] + " " + " ".join(art.get("tags", [])))
        score = len(q & hay)
        if score:
            scored.append((score, art))
    scored.sort(key=lambda x: (-x[0], x[1]["id"]))
    top = [
        {"id": a["id"], "title": a["title"], "body": a["body"], "score": s}
        for s, a in scored[:3]
    ]
    return success({"results": top, "count": len(top)})
