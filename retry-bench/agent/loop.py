from __future__ import annotations

import json
import time
from typing import Any, Callable

from agent.llm_client import LLMClient
from agent.prompts import SYSTEM_PROMPT
from bench.logger import EventLogger
from retry.policies import RetryContext, RetryPolicy
from tools.registry import SCHEMAS, bind_tools
from tools.world import World


def ctx_for_retry(task: dict[str, Any], seed: int, run_id: str, config: str, tool_name: str, logger: EventLogger, wrap: Callable) -> RetryContext:
    return RetryContext(
        run_id=run_id,
        config=config,
        task_id=task["id"],
        seed=seed,
        tool_name=tool_name,
        logger=logger,
        wrap_tool=wrap,
    )


def run_task(
    task: dict[str, Any],
    policy: RetryPolicy,
    seed: int,
    cfg: dict[str, Any],
    world: World,
    llm: LLMClient,
    logger: EventLogger,
    injector,
    run_id: str,
    config: str,
) -> dict[str, Any]:
    tools = bind_tools(world, task["id"])
    max_steps = int(cfg.get("max_steps", 8))
    timeout_s = float(cfg.get("task_timeout_s", 60))
    max_corrections = int(cfg.get("retry", {}).get("smart", {}).get("validation", {}).get("model_corrections", 2))
    corrections: dict[str, int] = {}
    started = time.perf_counter()
    status = "completed"
    final_text = ""

    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task["user_message"]},
    ]

    def wrap(tool_fn):
        return injector.wrap(tool_fn, task["id"], current_tool[0])

    current_tool = [""]

    for step in range(max_steps):
        if time.perf_counter() - started > timeout_s:
            status = "timeout"
            break
        resp = llm.call(messages, SCHEMAS)
        logger.event(
            "llm_call",
            step=step,
            input_tokens=resp.input_tokens,
            output_tokens=resp.output_tokens,
            wall_time_s=round(resp.wall_time_s, 4),
            provider_retries=resp.provider_retries,
            is_final=resp.is_final,
        )
        if resp.is_final:
            final_text = resp.text or ""
            messages.append({"role": "assistant", "content": final_text})
            break

        assistant_msg = resp.raw_message
        if assistant_msg.get("content") is None:
            assistant_msg["content"] = ""
        messages.append(assistant_msg)

        for tc in resp.tool_calls:
            if time.perf_counter() - started > timeout_s:
                status = "timeout"
                break
            name = tc.name
            args = dict(tc.arguments)
            world.tools_called.append(name)
            if name not in tools:
                result = {"ok": False, "error": {"category": "validation", "retryable": False, "message": f"unknown tool {name}"}}
            else:
                last_err = _last_error_category(logger, name)
                if last_err == "validation":
                    corrections[name] = corrections.get(name, 0) + 1
                    if config == "C" and corrections[name] > max_corrections:
                        result = {
                            "ok": False,
                            "error": {
                                "category": "validation",
                                "retryable": False,
                                "message": "too many argument corrections for this tool",
                            },
                        }
                        _append_tool_msg(messages, tc.id, name, result)
                        continue
                current_tool[0] = name
                ctx = ctx_for_retry(task, seed, run_id, config, name, logger, wrap)
                result = policy.execute(tools[name], args, ctx)
            _append_tool_msg(messages, tc.id, name, result)
        else:
            reflect_note = (
                "Reflect silently: did the latest tool result move you toward solving the task? "
                "If yes and you can answer, give the customer the final answer. If a tool failed, follow the error-category rules."
            )
            messages.append({"role": "user", "content": reflect_note})
            continue
        break
    else:
        status = "max_steps"
        final_text = final_text or "I could not complete this request in the allowed number of steps."

    wall = time.perf_counter() - started
    return {
        "status": status,
        "final_text": final_text,
        "wall_time_s": wall,
        "world": world,
        "messages": messages,
    }


def _append_tool_msg(messages: list[dict[str, Any]], tool_call_id: str, name: str, result: dict[str, Any]) -> None:
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": name,
            "content": json.dumps(result),
        }
    )


def _last_error_category(logger: EventLogger, tool: str) -> str | None:
    for event in reversed(logger.tool_calls()):
        if event.get("tool") == tool:
            return event.get("error_category")
    return None
