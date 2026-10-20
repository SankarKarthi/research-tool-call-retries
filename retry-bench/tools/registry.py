from __future__ import annotations

from functools import partial
from typing import Any, Callable

from tools.escalate import escalate_to_human
from tools.issue_refund import issue_refund
from tools.kb_search import kb_search
from tools.order_lookup import order_lookup
from tools.web_search import web_search
from tools.world import World

SIDE_EFFECT_TOOLS = {"issue_refund", "escalate_to_human"}

SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "kb_search",
            "description": "Search Harbor & Co. help-center articles. Use for policy questions (returns, shipping, warranty, billing).",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "order_lookup",
            "description": "Look up an order by id (for example ORD-1042). Returns status, amount, refundable flag, and dates.",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "issue_refund",
            "description": "Issue a refund for an order. Only works if the order is refundable. Always look the order up first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "amount": {"type": "number"},
                },
                "required": ["order_id", "amount"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the public web for facts not in the help center (recalls, carrier delays, promotions, news).",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Open a human-support ticket. Use for angry customers, legal threats, or issues you cannot resolve with tools.",
            "parameters": {
                "type": "object",
                "properties": {"reason": {"type": "string"}},
                "required": ["reason"],
            },
        },
    },
]


def bind_tools(world: World, task_id: str) -> dict[str, Callable[..., dict[str, Any]]]:
    return {
        "kb_search": partial(kb_search, world),
        "order_lookup": partial(order_lookup, world),
        "issue_refund": partial(issue_refund, world, task_id=task_id),
        "web_search": partial(web_search, world),
        "escalate_to_human": partial(escalate_to_human, world, task_id=task_id),
    }
