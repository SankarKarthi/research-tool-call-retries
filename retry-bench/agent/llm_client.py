from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from openai import APIStatusError, OpenAI, RateLimitError


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    text: str | None
    tool_calls: list[ToolCall]
    input_tokens: int
    output_tokens: int
    wall_time_s: float
    provider_retries: int = 0
    raw_message: dict[str, Any] = field(default_factory=dict)

    @property
    def is_final(self) -> bool:
        return not self.tool_calls


class LLMClient:
    def __init__(
        self,
        model: str,
        temperature: float = 0,
        max_tokens: int = 800,
        api_key: str | None = None,
        max_provider_retries: int = 5,
        retry_base_s: float = 1.0,
        sleep_fn: Callable[[float], None] | None = None,
        logger: Any | None = None,
    ):
        key = api_key or os.environ.get("GROQ_API_KEY")
        if not key:
            raise RuntimeError("GROQ_API_KEY is not set")
        self.client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_provider_retries = max_provider_retries
        self.retry_base_s = retry_base_s
        self.sleep_fn = sleep_fn or time.sleep
        self.logger = logger

    def call(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMResponse:
        last_err: Exception | None = None
        provider_retries = 0
        for attempt in range(1, self.max_provider_retries + 1):
            t0 = time.perf_counter()
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                )
                wall = time.perf_counter() - t0
                choice = resp.choices[0].message
                usage = resp.usage
                tool_calls = []
                raw_tool_calls = []
                for tc in choice.tool_calls or []:
                    args = tc.function.arguments or "{}"
                    try:
                        parsed = json.loads(args)
                    except json.JSONDecodeError:
                        parsed = {"_raw": args}
                    tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=parsed))
                    raw_tool_calls.append(
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": args},
                        }
                    )
                raw_message = {"role": "assistant", "content": choice.content or ""}
                if raw_tool_calls:
                    raw_message["tool_calls"] = raw_tool_calls
                return LLMResponse(
                    text=choice.content,
                    tool_calls=tool_calls,
                    input_tokens=int(getattr(usage, "prompt_tokens", 0) or 0),
                    output_tokens=int(getattr(usage, "completion_tokens", 0) or 0),
                    wall_time_s=wall,
                    provider_retries=provider_retries,
                    raw_message=raw_message,
                )
            except (RateLimitError, APIStatusError) as err:
                last_err = err
                status = getattr(err, "status_code", None)
                if status not in (429, 500, 502, 503) and not isinstance(err, RateLimitError):
                    raise
                provider_retries += 1
                if self.logger:
                    self.logger.event(
                        "provider_retry",
                        attempt=attempt,
                        status=status,
                        error=str(err)[:200],
                    )
                if attempt >= self.max_provider_retries:
                    break
                self.sleep_fn(self.retry_base_s * (2 ** (attempt - 1)))
        raise RuntimeError(f"Groq call failed after provider retries: {last_err}")
