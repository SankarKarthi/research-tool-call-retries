from faults.errors import ToolError
from retry.policies import NaiveRetry, NoRetry, RetryContext, SmartRetry


class DummyLogger:
    def __init__(self):
        self.events = []
        self.wasted_retries = 0
        self.retries_total = 0

    def event(self, *a, **k):
        self.events.append((a, k))

    def add_wasted(self, n):
        self.wasted_retries += n

    def add_retry(self):
        self.retries_total += 1


def ctx(wrap):
    return RetryContext("r", "A", "T1", 1, "kb_search", DummyLogger(), wrap)


def test_no_retry_returns_error():
    calls = {"n": 0}

    def tool():
        calls["n"] += 1
        raise ToolError("transient", True, "503")

    def wrap(fn):
        return fn

    out = NoRetry().execute(tool, {}, ctx(wrap))
    assert out["ok"] is False
    assert out["error"]["category"] == "transient"
    assert calls["n"] == 1


def test_naive_retries_validation():
    calls = {"n": 0}

    def tool():
        calls["n"] += 1
        raise ToolError("validation", False, "bad args")

    out = NaiveRetry(max_attempts=3, wait_s=0).execute(tool, {}, ctx(lambda f: f))
    assert calls["n"] == 3
    assert out["error"]["category"] == "validation"


def test_smart_does_not_retry_permission():
    calls = {"n": 0}

    def tool():
        calls["n"] += 1
        raise ToolError("permission", False, "403")

    out = SmartRetry(max_attempts=3, base_s=0, jitter=False).execute(tool, {}, ctx(lambda f: f))
    assert calls["n"] == 1
    assert out["error"]["category"] == "permission"


def test_smart_retries_transient_until_success():
    calls = {"n": 0}

    def tool():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ToolError("transient", True, "503")
        return {"ok": True, "data": {"ok": True}}

    out = SmartRetry(max_attempts=3, base_s=0, jitter=False).execute(tool, {}, ctx(lambda f: f))
    assert out["ok"] is True
    assert calls["n"] == 3
