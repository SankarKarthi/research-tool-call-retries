from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from faults.errors import ToolError, failure, success
from retry.classifier import classify


def _idempotency_key(task_id: str, tool: str, args: dict[str, Any]) -> str:
    raw = f"{task_id}|{tool}|{sorted(args.items())}".encode()
    return hashlib.sha256(raw).hexdigest()[:24]


@dataclass
class RetryContext:
    run_id: str
    config: str
    task_id: str
    seed: int
    tool_name: str
    logger: Any
    wrap_tool: Callable[[Callable[..., dict[str, Any]]], Callable[..., dict[str, Any]]]
    sleep_fn: Callable[[float], None] = time.sleep
    extra: dict[str, Any] = field(default_factory=dict)


class RetryPolicy:
    name = "base"

    def execute(self, tool_fn: Callable[..., dict[str, Any]], args: dict[str, Any], ctx: RetryContext) -> dict[str, Any]:
        raise NotImplementedError


class NoRetry(RetryPolicy):
    name = "A_no_retry"

    def execute(self, tool_fn: Callable[..., dict[str, Any]], args: dict[str, Any], ctx: RetryContext) -> dict[str, Any]:
        wrapped = ctx.wrap_tool(tool_fn)
        t0 = time.perf_counter()
        try:
            result = wrapped(**args)
            _log_tool(ctx, args, result, attempt=1, duration_ms=_ms(t0), retried=False)
            return result
        except ToolError as err:
            result = err.to_result()
            _log_tool(ctx, args, result, attempt=1, duration_ms=_ms(t0), retried=False)
            return result


class NaiveRetry(RetryPolicy):
    name = "B_naive"

    def __init__(self, max_attempts: int = 3, wait_s: float = 1.0):
        self.max_attempts = max_attempts
        self.wait_s = wait_s

    def execute(self, tool_fn: Callable[..., dict[str, Any]], args: dict[str, Any], ctx: RetryContext) -> dict[str, Any]:
        wrapped = ctx.wrap_tool(tool_fn)
        last: dict[str, Any] | None = None
        wasted = 0
        for attempt in range(1, self.max_attempts + 1):
            t0 = time.perf_counter()
            try:
                result = wrapped(**args)
                _log_tool(ctx, args, result, attempt=attempt, duration_ms=_ms(t0), retried=attempt > 1)
                return result
            except ToolError as err:
                last = err.to_result()
                _log_tool(ctx, args, last, attempt=attempt, duration_ms=_ms(t0), retried=attempt > 1)
                if attempt < self.max_attempts:
                    ctx.logger.add_retry()
                    wasted += 1
                    ctx.logger.event(
                        "retry",
                        tool=ctx.tool_name,
                        attempt=attempt + 1,
                        error_category=err.category,
                        policy="naive",
                    )
                    ctx.sleep_fn(self.wait_s)
        ctx.logger.add_wasted(wasted)
        return last or failure("permission", False, "unknown tool failure")


class SmartRetry(RetryPolicy):
    name = "C_smart"

    def __init__(
        self,
        max_attempts: int = 3,
        base_s: float = 0.5,
        jitter: bool = True,
        budget_s: float = 8.0,
    ):
        self.max_attempts = max_attempts
        self.base_s = base_s
        self.jitter = jitter
        self.budget_s = budget_s

    def execute(self, tool_fn: Callable[..., dict[str, Any]], args: dict[str, Any], ctx: RetryContext) -> dict[str, Any]:
        wrapped = ctx.wrap_tool(tool_fn)
        started = time.perf_counter()
        last: dict[str, Any] | None = None
        wasted = 0
        merged: dict[str, Any] = {}

        for attempt in range(1, self.max_attempts + 1):
            if time.perf_counter() - started > self.budget_s:
                ctx.logger.add_wasted(wasted)
                return last or failure("transient", True, "retry budget exceeded")
            t0 = time.perf_counter()
            try:
                result = wrapped(**args)
                if merged and result.get("ok"):
                    result = _merge_partial(merged, result)
                _log_tool(ctx, args, result, attempt=attempt, duration_ms=_ms(t0), retried=attempt > 1)
                return result
            except ToolError as err:
                cat, retryable, message, data = classify(err)
                last = err.to_result()
                _log_tool(ctx, args, last, attempt=attempt, duration_ms=_ms(t0), retried=attempt > 1)

                if cat == "partial" and data:
                    merged = _merge_partial(merged, {"ok": True, "data": data})
                    # Retry only remaining failed items if the tool understands `retry_items`.
                    if data.get("failed_items"):
                        args = {**args, "retry_items": data["failed_items"]}
                    retryable = True

                if cat in ("validation", "permission", "not_found"):
                    ctx.logger.add_wasted(wasted)
                    return last

                if not retryable or attempt >= self.max_attempts:
                    ctx.logger.add_wasted(wasted)
                    return last

                wasted += 1
                ctx.logger.add_retry()
                delay = self.base_s * (2 ** (attempt - 1))
                if self.jitter:
                    delay *= 0.5 + 0.5 * (hash(f"{ctx.task_id}{attempt}") % 1000) / 1000.0
                delay = min(delay, max(0.0, self.budget_s - (time.perf_counter() - started)))
                ctx.logger.event(
                    "retry",
                    tool=ctx.tool_name,
                    attempt=attempt + 1,
                    error_category=cat,
                    policy="smart",
                    delay_s=round(delay, 3),
                )
                ctx.sleep_fn(delay)

        ctx.logger.add_wasted(wasted)
        return last or failure("transient", True, "retries exhausted")


def policy_for(config: str, cfg: dict[str, Any]) -> RetryPolicy:
    config = config.upper()
    if config == "A":
        return NoRetry()
    if config == "B":
        naive = cfg.get("retry", {}).get("naive", {})
        return NaiveRetry(max_attempts=int(naive.get("max_attempts", 3)), wait_s=float(naive.get("wait_s", 1)))
    if config == "C":
        smart = cfg.get("retry", {}).get("smart", {}).get("transient", {})
        return SmartRetry(
            max_attempts=int(smart.get("max_attempts", 3)),
            base_s=float(smart.get("base_s", 0.5)),
            jitter=bool(smart.get("jitter", True)),
            budget_s=float(smart.get("budget_s", 8)),
        )
    raise ValueError(f"unknown config {config}")


def _ms(t0: float) -> int:
    return int((time.perf_counter() - t0) * 1000)


def _log_tool(ctx: RetryContext, args: dict[str, Any], result: dict[str, Any], attempt: int, duration_ms: int, retried: bool) -> None:
    err = None if result.get("ok") else (result.get("error") or {})
    ctx.logger.event(
        "tool_call",
        tool=ctx.tool_name,
        attempt=attempt,
        retried=retried,
        ok=bool(result.get("ok")),
        error_category=(err or {}).get("category"),
        duration_ms=duration_ms,
        args=args,
        idempotency_key=_idempotency_key(ctx.task_id, ctx.tool_name, args),
    )


def _merge_partial(previous: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    prev_data = previous.get("data") or {}
    new_data = incoming.get("data") or {}
    items = list(prev_data.get("items") or []) + list(new_data.get("items") or [])
    return success({**prev_data, **new_data, "items": items})
