"""Gemini busy handling: retries, next model, time budget, cache. No network: httpx.post is faked."""
import httpx
import pytest

from app import llm


class Resp:
    def __init__(self, code, body=None, headers=None):
        self.status_code, self._body, self.headers = code, body or {}, headers or {}
        self.text = str(self._body)

    def json(self):
        return self._body


OK = Resp(200, {"candidates": [{"content": {"parts": [{"text": "hello"}]}}]})


@pytest.fixture
def gemini(monkeypatch):
    monkeypatch.delenv("MOCK_LLM", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "test")
    monkeypatch.setenv("GEMINI_MODEL", "m1")
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "m2, m3")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    llm._CACHE.clear()
    calls = []

    def run(answers):
        it = iter(answers)

        def post(url, **kw):
            calls.append(url.split("/models/")[1].split(":")[0])
            a = next(it)
            if isinstance(a, Exception):
                raise a
            return a
        monkeypatch.setattr(httpx, "post", post)
        return calls
    return run


def test_busy_then_ok_on_same_model(gemini):
    calls = gemini([Resp(503), Resp(503), OK])
    assert llm.complete("x", "s", "u1") == "hello"
    assert calls == ["m1", "m1", "m1"]


def test_moves_to_next_models(gemini):
    calls = gemini([Resp(503)] * 3 + [Resp(429, {"error": {"message": "quota per day"}})] + [OK])
    assert llm.complete("x", "s", "u2") == "hello"
    assert calls == ["m1", "m1", "m1", "m2", "m3"]


def test_all_busy_raises_aibusy(gemini):
    gemini([Resp(503)] * 9)
    with pytest.raises(llm.AIBusy):
        llm.complete("x", "s", "u3")


def test_timeout_tries_next_model(gemini):
    calls = gemini([httpx.ReadTimeout("slow"), OK])
    assert llm.complete("x", "s", "u4") == "hello"
    assert calls == ["m1", "m2"]


def test_busy_then_missing_model_is_still_busy(gemini, monkeypatch):
    monkeypatch.setenv("GEMINI_FALLBACK_MODEL", "nope")
    gemini([Resp(503)] * 3 + [Resp(404, {"error": {"message": "not found"}})])
    with pytest.raises(llm.AIBusy):
        llm.complete("x", "s", "u5")


def test_same_request_answered_from_cache(gemini):
    calls = gemini([OK])
    assert llm.complete("x", "s", "same", ("img".encode(), "image/png")) == "hello"
    assert llm.complete("x", "s", "same", ("img".encode(), "image/png")) == "hello"
    assert calls == ["m1"]  # second call never reached Gemini


def test_time_budget_stops_retrying(gemini, monkeypatch):
    monkeypatch.setenv("AI_TIME_BUDGET", "2")
    calls = gemini([Resp(503)] * 9)
    with pytest.raises(llm.AIBusy):
        llm.complete("x", "s", "u6")
    assert calls == []  # budget too small to even start


def test_claude_backup_when_gemini_busy(gemini, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")
    monkeypatch.setattr(llm, "_claude", lambda *a: "from claude")
    gemini([Resp(503)] * 9)
    assert llm.complete("x", "s", "u7") == "from claude"
