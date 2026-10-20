from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env(ROOT / ".env")

from agent.llm_client import LLMClient
from agent.loop import run_task
from bench.evaluator import evaluate
from bench.logger import EventLogger
from bench.metrics import cost_usd, summarize, write_outputs
from faults.injector import FaultInjector
from retry.policies import policy_for
from tools.world import World

RESULTS = ROOT / "results"


def load_config() -> dict[str, Any]:
    with open(ROOT / "config.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_tasks() -> list[dict[str, Any]]:
    with open(ROOT / "bench" / "tasks.json", encoding="utf-8") as f:
        return json.load(f)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run tool-call retry benchmarks")
    p.add_argument("--configs", default="A", help="Comma-separated configs: A,B,C (A=no retry)")
    p.add_argument("--seeds", default=None, help="Comma-separated seeds (default from config.yaml)")
    p.add_argument("--tasks", default="all", help="all, a prefix like T01, or comma-separated ids")
    p.add_argument("--no-fault", action="store_true", help="Disable fault injection (ceiling run)")
    p.add_argument("--limit", type=int, default=0, help="Optional cap on number of tasks")
    p.add_argument("--tag", default=None, help="Results file tag")
    return p.parse_args()


def select_tasks(all_tasks: list[dict[str, Any]], spec: str, limit: int) -> list[dict[str, Any]]:
    if spec == "all":
        chosen = all_tasks
    elif "," in spec:
        ids = {s.strip() for s in spec.split(",")}
        chosen = [t for t in all_tasks if t["id"] in ids]
    else:
        chosen = [t for t in all_tasks if t["id"].startswith(spec)]
    if limit:
        chosen = chosen[:limit]
    return chosen


def injected_by_type(injector: FaultInjector) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in injector.injected:
        counts[item["category"]] = counts.get(item["category"], 0) + 1
    return counts


def main() -> None:
    args = parse_args()
    cfg = load_config()
    tasks = select_tasks(load_tasks(), args.tasks, args.limit)
    configs = [c.strip().upper() for c in args.configs.split(",") if c.strip()]
    seeds = [int(s) for s in args.seeds.split(",")] if args.seeds else list(cfg["seeds"])
    base = World.load()
    run_id = uuid.uuid4().hex[:10]
    tag = args.tag or f"{''.join(configs)}_{'nofault' if args.no_fault else 'faults'}_{run_id}"
    log_path = RESULTS / f"{tag}.jsonl"

    llm = LLMClient(
        model=cfg["model"],
        temperature=float(cfg["temperature"]),
        max_tokens=int(cfg["max_tokens"]),
        max_provider_retries=int(cfg.get("provider_max_retries", 5)),
        retry_base_s=float(cfg.get("provider_retry_base_s", 1.0)),
    )
    groq_prices = cfg["price_per_million_tokens"]["groq"]
    claude_prices = cfg["price_per_million_tokens"]["claude_equivalent"]
    delay = float(cfg.get("inter_call_delay_s", 0.15))
    rows = []

    print(f"run_id={run_id} configs={configs} seeds={seeds} tasks={len(tasks)} faults={not args.no_fault}")
    # Interleave configs per task so provider load does not favor one config.
    for seed in seeds:
        for task in tasks:
            for config in configs:
                world = base.clone()
                injector = FaultInjector(
                    seed=seed,
                    rates=cfg["fault_rates"],
                    enabled=not args.no_fault,
                    transient_latency=cfg.get("transient_latency_s"),
                )
                logger = EventLogger(
                    log_path,
                    {"run_id": run_id, "config": config, "task_id": task["id"], "seed": seed},
                )
                policy = policy_for(config, cfg)
                llm.logger = logger
                logger.event("task_start")
                outcome = run_task(task, policy, seed, cfg, world, llm, logger, injector, run_id, config)
                judged = evaluate(task, world, outcome["final_text"], outcome["status"])
                in_tok = sum(e.get("input_tokens", 0) for e in logger.llm_calls())
                out_tok = sum(e.get("output_tokens", 0) for e in logger.llm_calls())
                row = {
                    "run_id": run_id,
                    "config": config,
                    "task_id": task["id"],
                    "task_type": task.get("type"),
                    "seed": seed,
                    "success": judged["success"],
                    "failure_reason": judged["failure_reason"],
                    "detail": "; ".join(judged["detail"]),
                    "status": outcome["status"],
                    "input_tokens": in_tok,
                    "output_tokens": out_tok,
                    "cost_usd": round(cost_usd(in_tok, out_tok, groq_prices), 6),
                    "cost_usd_claude_eq": round(cost_usd(in_tok, out_tok, claude_prices), 6),
                    "wall_time_s": round(outcome["wall_time_s"], 4),
                    "llm_calls": len(logger.llm_calls()),
                    "tool_calls": len(logger.tool_calls()),
                    "retries_total": logger.retries_total,
                    "retries_wasted": logger.wasted_retries,
                    "duplicate_actions": world.duplicate_actions,
                    "injected_faults": json.dumps(injected_by_type(injector)),
                    "answer": (outcome["final_text"] or "")[:400],
                }
                logger.event("task_end", **{k: v for k, v in row.items() if k != "answer"})
                rows.append(row)
                mark = "OK" if row["success"] else f"FAIL:{row['failure_reason']}"
                print(f"  {config} seed={seed} {task['id']} {mark} {row['wall_time_s']:.1f}s ${row['cost_usd']:.4f}")
                time.sleep(delay)

    write_outputs(rows, summarize(rows), RESULTS, tag)


if __name__ == "__main__":
    main()
