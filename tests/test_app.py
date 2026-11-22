import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)
os.environ.pop("MOCK_LLM", None)

from fastapi.testclient import TestClient  # noqa: E402

from app import proof, rules  # noqa: E402
from app.main import SEEN_TRX, app  # noqa: E402

client = TestClient(app)


# ---------------------------------------------------------------- rules
def test_pin_request_is_high():
    assert rules.analyze("Apnar bKash PIN ta bolun, ami ferot pathiye dicchi")["risk"] == "high"


def test_bangla_pin_request_is_high():
    assert rules.analyze("আপনার পিন নম্বরটা বলুন, আমি টাকা ফেরত দিচ্ছি")["risk"] == "high"


def test_genuine_otp_sms_is_low():
    t = "Your bKash verification code is 482913. Do not share it with anyone."
    assert rules.analyze(t)["risk"] == "low"


def test_received_money_is_low():
    t = "You have received Tk 500.00 from 01712345678. Fee Tk 0.00. Balance Tk 1,250.00. TrxID 8N7A6D5EF3 at 21/11/2026 10:30"
    assert rules.analyze(t)["risk"] == "low"


def test_wrong_number_refund_is_high():
    assert rules.analyze("Vul kore apnar number e 5000 taka chole gese, ferot din please")["risk"] == "high"


def test_kyc_threat_bangla_is_high():
    t = "আপনার বিকাশ অ্যাকাউন্টের কেওয়াইসি আপডেট না করলে আজই অ্যাকাউন্ট বন্ধ হয়ে যাবে। এখনই এই নম্বরে কল করুন"
    assert rules.analyze(t)["risk"] == "high"


def test_remote_access_is_high():
    assert rules.analyze("Please install AnyDesk so I can help you")["risk"] == "high"


# ---------------------------------------------------------------- proof
NOW = datetime(2026, 11, 23, 12, 0)


def fresh():
    return {}


def test_proof_consistent():
    r = proof.check(
        {"amount": 3500, "trx_id": "8N7A6D5EF3", "recipient": "01712345678", "datetime": "2026-11-23 11:20"},
        {"amount": 3500, "recipient": "01712345678", "chat_time": "2026-11-23T11:30", "order_ref": "a"},
        NOW, fresh())
    assert r["verdict"] == "consistent"


def test_proof_amount_mismatch_is_suspicious():
    r = proof.check(
        {"amount": 3000, "trx_id": "8N7A6D5EF3", "recipient": "01712345678", "datetime": "2026-11-23 11:20"},
        {"amount": 3500, "recipient": "01712345678", "chat_time": "2026-11-23T11:30", "order_ref": "a"},
        NOW, fresh())
    assert r["verdict"] == "suspicious"
    assert any(c["id"] == "amount" and c["status"] == "fail" for c in r["checks"])


def test_proof_two_fails_is_likely_fake():
    r = proof.check(
        {"amount": 3000, "trx_id": "8N7A6D5EF3", "recipient": "01712345678", "datetime": "2026-11-23 13:00"},
        {"amount": 3500, "recipient": "01712345678", "chat_time": "2026-11-23T11:30", "order_ref": "a"},
        NOW, fresh())
    assert r["verdict"] == "likely_fake"


def test_proof_trx_reuse_flagged():
    seen = {}
    fields = {"amount": 3500, "trx_id": "8N7A6D5EF3", "recipient": "01712345678", "datetime": "2026-11-23 11:20"}
    proof.check(fields, {"amount": 3500, "recipient": "01712345678", "order_ref": "order-1"}, NOW, seen)
    r = proof.check(fields, {"amount": 3500, "recipient": "01712345678", "order_ref": "order-2"}, NOW, seen)
    assert any(c["id"] == "trx_reuse" for c in r["checks"])


def test_proof_never_says_safe():
    r = proof.check({"amount": 1, "trx_id": "8N7A6D5EF3", "datetime": "2026-11-23 11:20"}, {"amount": 1}, NOW, {})
    assert r["verdict"] in ("consistent", "suspicious", "likely_fake")
    assert "own" in r["reminder_en"]


# ------------------------------------------------------------------ API
def test_status_rules_mode():
    assert client.get("/api/status").json()["ai"] == "rules"


def test_pretx_endpoint():
    r = client.post("/api/pretx", json={"text": "Apnar PIN ta bolun", "lang": "en"})
    assert r.status_code == 200 and r.json()["risk"] == "high"


def test_pretx_rejects_empty():
    assert client.post("/api/pretx", json={"text": " ", "lang": "en"}).status_code == 400


def test_proof_manual_fields():
    SEEN_TRX.clear()
    manual = {"amount": "3,000", "trx_id": "8N7A6D5EF3", "datetime": "2026-11-01T11:20"}
    r = client.post("/api/proof", data={"expected_amount": "3500", "manual": json.dumps(manual)})
    assert r.status_code == 200
    body = r.json()
    assert body["needs_manual"] is False and body["verdict"] == "suspicious"


def test_proof_needs_input():
    assert client.post("/api/proof", data={"expected_amount": "3500"}).json()["needs_manual"] is True


def test_trainer_scenarios_served():
    data = client.get("/api/trainer/scenarios").json()
    assert len(data) == 3 and all(len(s["steps"]) == 3 for s in data)


def test_trainer_chat_needs_key():
    assert client.post("/api/trainer/chat", json={"scenario": "refund", "history": [], "lang": "en"}).status_code == 503


# ------------------------------------------------------- robustness
def test_pretx_very_long_and_odd_input():
    for t in ["a" * 50000, "😀" * 500, "০১২৩ pin ওটিপি " * 200, "<script>alert(1)</script>", "\x00\x01 bolun"]:
        r = client.post("/api/pretx", json={"text": t, "lang": "bn"})
        assert r.status_code in (200, 400)


def test_pretx_bad_json_shape():
    assert client.post("/api/pretx", json={"nope": 1}).status_code == 422
    assert client.post("/api/pretx", content=b"not json", headers={"content-type": "application/json"}).status_code == 422


def test_proof_rejects_big_and_wrong_type():
    big = ("x.png", b"0" * (4 * 1024 * 1024 + 1), "image/png")
    assert client.post("/api/proof", files={"image": big}).status_code == 413
    assert client.post("/api/proof", files={"image": ("x.txt", b"hi", "text/plain")}).status_code == 415


def test_proof_garbage_manual_json():
    r = client.post("/api/proof", data={"manual": "{not json", "expected_amount": "abc"})
    assert r.status_code == 200 and r.json()["needs_manual"] is True


def test_rate_limit(monkeypatch):
    import app.main as m
    m._hits.clear(); monkeypatch.setattr(m, "RATE_LIMIT", 3)
    codes = [client.post("/api/pretx", json={"text": "hello there", "lang": "en"}).status_code for _ in range(5)]
    assert codes[:3] == [200, 200, 200] and codes[3] == 429
    m._hits.clear()


# ------------------------------------------------------- gemini wiring (no network)
def test_gemini_request_shape(monkeypatch):
    import httpx
    from app import llm
    sent = {}

    class R:
        status_code = 200
        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": "thinking", "thought": True}, {"text": '{"risk": "high"}'}]}}]}

    def fake_post(url, json, timeout, headers):
        sent.update(url=url, body=json, headers=headers)
        return R()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("MOCK_LLM", raising=False)
    monkeypatch.setattr(httpx, "post", fake_post)
    out = llm.complete("extract", "sys", "read it", image=(b"img", "image/png"))
    assert out == '{"risk": "high"}'
    assert "gemini-3.5-flash-lite:generateContent" in sent["url"]
    assert sent["headers"]["x-goog-api-key"] == "test-key"
    assert sent["body"]["contents"][0]["parts"][0]["inline_data"]["mime_type"] == "image/png"
    assert sent["body"]["generationConfig"]["responseMimeType"] == "application/json"
    assert client.get("/api/status").json() == {"ai": "live", "provider": "gemini", "model": "gemini-3.5-flash-lite"}


def test_gemini_error_falls_back_to_rules(monkeypatch):
    import httpx

    class R:
        status_code = 429
        text = "quota"
        def json(self):
            return {"error": {"message": "quota exceeded"}}

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "post", lambda *a, **k: R())
    d = client.post("/api/pretx", json={"text": "Apnar PIN ta bolun", "lang": "en"}).json()
    assert d["risk"] == "high" and d["source"] == "rules" and "429" in d["ai_error"]
