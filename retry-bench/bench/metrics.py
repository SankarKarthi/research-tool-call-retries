from __future__ import annotations

import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


def cost_usd(input_tokens: int, output_tokens: int, prices: dict[str, float]) -> float:
    return (input_tokens / 1_000_000) * float(prices["input"]) + (output_tokens / 1_000_000) * float(prices["output"])


def percentile(xs: list[float], p: float) -> float:
    if not xs:
        return 0.0
    ys = sorted(xs)
    k = (len(ys) - 1) * p
    f = int(k)
    c = min(f + 1, len(ys) - 1)
    if f == c:
        return ys[f]
    return ys[f] + (ys[c] - ys[f]) * (k - f)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_config: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_config[row["config"]].append(row)
    out = {}
    for config, group in sorted(by_config.items()):
        walls = [r["wall_time_s"] for r in group]
        out[config] = {
            "n": len(group),
            "success_rate": mean([1.0 if r["success"] else 0.0 for r in group]),
            "cost_per_task_groq": mean([r["cost_usd"] for r in group]),
            "cost_total_groq": sum(r["cost_usd"] for r in group),
            "cost_per_task_claude_eq": mean([r["cost_usd_claude_eq"] for r in group]),
            "latency_p50_s": percentile(walls, 0.50),
            "latency_p95_s": percentile(walls, 0.95),
            "avg_tool_calls": mean([r["tool_calls"] for r in group]),
            "avg_llm_calls": mean([r["llm_calls"] for r in group]),
            "retries_total": sum(r["retries_total"] for r in group),
            "retries_wasted": sum(r["retries_wasted"] for r in group),
            "duplicate_actions": sum(r["duplicate_actions"] for r in group),
            "failure_reasons": _count([r.get("failure_reason") for r in group if not r["success"]]),
        }
    return out


def mean(xs: list[float]) -> float:
    return float(statistics.fmean(xs)) if xs else 0.0


def _count(xs: list[str | None]) -> dict[str, int]:
    c: dict[str, int] = defaultdict(int)
    for x in xs:
        c[str(x)] += 1
    return dict(c)


def write_outputs(rows: list[dict[str, Any]], summary: dict[str, Any], results_dir: Path, tag: str) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / f"{tag}_tasks.csv"
    json_path = results_dir / f"{tag}_summary.json"
    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"wrote {csv_path}")
    print(f"wrote {json_path}")
    print(json.dumps(summary, indent=2))
