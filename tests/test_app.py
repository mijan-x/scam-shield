import pytest
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


GOOD = {"amount": 3500, "recipient": "01712345678", "datetime": "2026-11-23 11:20"}
EXP = {"amount": 3500, "recipient": "01712345678", "chat_time": "2026-11-23T11:30", "order_ref": "a"}


def test_wrong_trx_format_makes_whole_payment_likely_fake():
    # everything else matches, only the transaction ID is impossible
    for bad in ("ABC12", "8N7A-6D5EF3", "1234567890", "AAAAAAAAAA", "8N7A6D5EF3X99ZZ"):
        r = proof.check({**GOOD, "trx_id": bad}, EXP, NOW, fresh())
        assert r["verdict"] == "likely_fake", bad
        assert any(c["id"] == "trx_format" and c["status"] == "fail" for c in r["checks"]), bad


def test_bkash_trx_must_be_10_characters():
    r = proof.check({**GOOD, "trx_id": "8N7A6D5EF", "provider": "bkash"}, EXP, NOW, fresh())
    assert r["verdict"] == "likely_fake"
    r = proof.check({**GOOD, "trx_id": "8N7A6D5EF3", "provider": "bkash"}, EXP, NOW, fresh())
    assert r["verdict"] == "consistent"


def test_bank_reference_can_be_longer():
    r = proof.check({**GOOD, "trx_id": "FT2632814029X7Q1", "provider": "bank"}, EXP, NOW, fresh())
    assert r["verdict"] == "consistent"


def test_trx_label_and_spaces_are_ignored():
    r = proof.check({**GOOD, "trx_id": "TrxID: 8N7A 6D5E F3"}, EXP, NOW, fresh())
    assert r["verdict"] == "consistent"


def test_trx_differs_from_sellers_own_message_is_likely_fake():
    r = proof.check({**GOOD, "trx_id": "8N7A6D5EF3"}, {**EXP, "trx_id": "9K2L4M6N8P"}, NOW, fresh())
    assert r["verdict"] == "likely_fake"
    assert any(c["id"] == "trx_match" and c["status"] == "fail" for c in r["checks"])
    r = proof.check({**GOOD, "trx_id": "8N7A6D5EF3"}, {**EXP, "trx_id": "8n7a6d5ef3"}, NOW, fresh())
    assert r["verdict"] == "consistent"
    assert any(c["id"] == "trx_match" and c["status"] == "ok" for c in r["checks"])


def test_reused_trx_is_likely_fake():
    seen = {}
    f = {**GOOD, "trx_id": "8N7A6D5EF3"}
    proof.check(f, {**EXP, "order_ref": "order-1"}, NOW, seen)
    r = proof.check(f, {**EXP, "order_ref": "order-2"}, NOW, seen)
    assert r["verdict"] == "likely_fake"


def test_api_own_trx_field():
    SEEN_TRX.clear()
    manual = json.dumps({"amount": "3500", "trx_id": "8N7A6D5EF3", "datetime": "2026-11-01T11:20"})
    r = client.post("/api/proof", data={"manual": manual, "expected_amount": "3500", "expected_trx": "7Q2W4E6R8T"}).json()
    assert r["verdict"] == "likely_fake"


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
    from app.scenarios import PERSONA
    assert len(data) >= 3
    for sc in data:
        for k in ("id", "title_en", "title_bn", "intro_en", "intro_bn", "safe_en", "safe_bn", "red_flags_en", "red_flags_bn"):
            assert sc.get(k), f"{sc.get('id')}: missing {k}"
        assert sc["id"] in PERSONA, f"{sc['id']}: add a PERSONA entry for free chat"
        assert len(sc["steps"]) >= 2
        for st in sc["steps"]:
            assert st["scammer_en"] and st["scammer_bn"] and len(st["choices"]) >= 2
            assert {c["score"] for c in st["choices"]} <= {0, 1, 2} and max(c["score"] for c in st["choices"]) == 2
            for c in st["choices"]:
                assert c["en"] and c["bn"] and c["fb_en"] and c["fb_bn"]


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
    assert client.get("/api/status").json() == {"ai": "live", "provider": "gemini", "model": "gemini-3.5-flash-lite", "voice": True}


def test_gemini_error_falls_back_to_rules(monkeypatch):
    import httpx

    class R:
        status_code = 429
        text = "quota"
        def json(self):
            return {"error": {"message": "quota exceeded"}}

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(httpx, "post", lambda *a, **k: R())
    import app.llm as _l
    monkeypatch.setattr(_l.time, "sleep", lambda s: None)
    d = client.post("/api/pretx", json={"text": "Apnar PIN ta bolun", "lang": "en"}).json()
    assert d["risk"] == "high" and d["source"] == "rules" and "429" in d["ai_error"]


def test_head_requests_supported():
    assert client.head("/api/status").status_code == 200
    assert client.head("/api/trainer/scenarios").status_code == 200
    assert client.head("/").status_code == 200


# ------------------------------------------------------- explainability & entities
def test_highlights_map_to_original_text():
    t = "Apnar  bKash   PIN ta BOLUN\nnow"
    r = rules.analyze(t)
    words = {t[h["start"]:h["end"]].lower() for h in r["highlights"]}
    assert "pin" in words and "bolun" in words


def test_bangla_digits_and_highlight_positions():
    t = "আপনার উপবৃত্তির টাকা পেতে ওটিপি কোডটি বলুন"
    r = rules.analyze(t)
    assert r["risk"] == "high"
    assert any(t[h["start"]:h["end"]] == "ওটিপি" for h in r["highlights"])


def test_lookalike_link_flagged_official_not():
    bad = rules.analyze("Verify now: http://bkash-secure-login.top/verify")
    assert bad["risk"] == "high" and bad["entities"][0]["verdict"] == "danger"
    good = rules.analyze("Download the app from https://www.bkash.com/app")
    assert good["risk"] == "low" and good["entities"][0]["verdict"] == "official"


def test_personal_number_with_care_is_flagged():
    r = rules.analyze("Nagad customer care: call 01812345678 to fix your account")
    assert r["risk"] in ("medium", "high")
    assert any(e["kind"] == "phone" and e["verdict"] == "caution" for e in r["entities"])


def test_hotline_recognised():
    r = rules.analyze("Problem hole 16247 e call korun")
    assert any(e["text"] == "16247" and e["verdict"] == "official" for e in r["entities"])


# ------------------------------------------------------- image forensics
def _png(text_chunk=None, size=(400, 800), color=(255, 255, 255)):
    import io
    from PIL import Image, PngImagePlugin
    info = PngImagePlugin.PngInfo()
    if text_chunk:
        info.add_text("Software", text_chunk)
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG", pnginfo=info)
    return buf.getvalue()


def test_editor_metadata_detected():
    from app import forensics
    assert forensics.inspect(_png("Adobe Photoshop 25.0"))["editor"].lower() == "photoshop"
    assert forensics.inspect(_png())["editor"] is None


def test_proof_flags_editor_and_reused_image():
    SEEN_TRX.clear()
    import app.main as m
    m.SEEN_IMG.clear()
    manual = json.dumps({"amount": "3500", "trx_id": "8N7A6D5EF3", "datetime": "2026-11-01T11:20"})
    img = _png("PicsArt")
    r1 = client.post("/api/proof", data={"expected_amount": "3500", "order_ref": "a", "manual": manual},
                     files={"image": ("s.png", img, "image/png")}).json()
    assert any(c["id"] == "meta_editor" and c["status"] == "fail" for c in r1["checks"])
    manual2 = json.dumps({"amount": "3500", "trx_id": "9K2L4M6N8P", "datetime": "2026-11-01T11:20"})
    r2 = client.post("/api/proof", data={"expected_amount": "3500", "order_ref": "b", "manual": manual2},
                     files={"image": ("s.png", img, "image/png")}).json()
    assert any(c["id"] == "image_reuse" for c in r2["checks"]) and r2["verdict"] == "likely_fake"
    assert 0 <= r2["score"] <= 100


def test_unreadable_image_rejected():
    assert client.post("/api/proof", files={"image": ("x.png", b"not an image", "image/png")}).status_code == 415


# ------------------------------------------------------- transparency endpoints
def test_meta_and_metrics():
    meta = client.get("/api/meta").json()
    assert len(meta["patterns"]) >= 14 and meta["hotlines"][0]["number"] == "16247"
    mt = client.get("/api/metrics").json()
    assert mt["holdout"]["scam"] > 0 and 0 <= mt["holdout"]["recall"] <= 1
    assert client.get("/api/health").json() == {"ok": True}


# ------------------------------------------------------- voice
def _wav(seconds=0.5):
    import io, struct, wave
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(struct.pack("<h", 0) * int(16000 * seconds))
    return buf.getvalue()


def test_voice_needs_gemini_in_rules_mode():
    r = client.post("/api/voice", files={"audio": ("v.wav", _wav(), "audio/wav")})
    assert r.status_code == 503
    assert client.get("/api/status").json()["voice"] is False


def test_voice_mock_transcribes(monkeypatch):
    monkeypatch.setenv("MOCK_LLM", "1")
    r = client.post("/api/voice", files={"audio": ("v.wav", _wav(), "audio/wav")}, data={"lang": "bn"})
    assert r.status_code == 200 and "PIN" in r.json()["transcript"]


def test_voice_rejects_bad_input(monkeypatch):
    monkeypatch.setenv("MOCK_LLM", "1")
    assert client.post("/api/voice", files={"audio": ("v.txt", b"hello", "text/plain")}).status_code == 415
    assert client.post("/api/voice", files={"audio": ("v.wav", b"", "audio/wav")}).status_code == 400
    big = ("v.wav", b"0" * (4 * 1024 * 1024 + 1), "audio/wav")
    assert client.post("/api/voice", files={"audio": big}).status_code == 413


def test_voice_sends_audio_to_gemini(monkeypatch):
    import httpx
    sent = {}

    class R:
        status_code = 200
        def json(self):
            return {"candidates": [{"content": {"parts": [{"text": "  আপনার পিন বলুন \n"}]}}]}

    def fake_post(url, json, timeout, headers):
        sent["body"] = json
        return R()

    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.delenv("MOCK_LLM", raising=False)
    monkeypatch.setattr(httpx, "post", fake_post)
    r = client.post("/api/voice", files={"audio": ("v.wav", _wav(), "audio/wav")}).json()
    assert r["transcript"] == "আপনার পিন বলুন"
    part = sent["body"]["contents"][0]["parts"][0]["inline_data"]
    assert part["mime_type"] == "audio/wav" and "responseMimeType" not in sent["body"]["generationConfig"]


# ------------------------------------------------------- AI busy: retry, fallback model, friendly message
class _Resp:
    def __init__(self, code, text='{"risk": "high"}'):
        self.status_code, self._text = code, text
    def json(self):
        if self.status_code == 200:
            return {"candidates": [{"content": {"parts": [{"text": self._text}]}}]}
        return {"error": {"message": "This model is currently experiencing high demand."}}


def _gemini_env(monkeypatch, codes):
    import httpx
    from app import llm
    calls = []

    def fake_post(url, json, timeout, headers):
        calls.append(url.split("/models/")[1].split(":")[0])
        return _Resp(codes[len(calls) - 1] if len(calls) <= len(codes) else codes[-1])

    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.delenv("MOCK_LLM", raising=False)
    monkeypatch.delenv("GEMINI_FALLBACK_MODEL", raising=False)
    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    llm._CACHE.clear()
    return calls


def test_busy_then_ok_retries_same_model(monkeypatch):
    from app import llm
    calls = _gemini_env(monkeypatch, [503, 200])
    assert llm.complete("pretx", "s", "u") == '{"risk": "high"}'
    assert calls == ["gemini-3.5-flash-lite", "gemini-3.5-flash-lite"]


def test_busy_three_times_uses_fallback_model(monkeypatch):
    from app import llm
    calls = _gemini_env(monkeypatch, [503, 503, 503, 200])
    assert llm.complete("pretx", "s", "u") == '{"risk": "high"}'
    assert calls == ["gemini-3.5-flash-lite"] * 3 + ["gemini-3.8-flash"]


def test_all_busy_gives_friendly_proof_message(monkeypatch):
    calls = _gemini_env(monkeypatch, [503])
    r = client.post("/api/proof", data={"expected_amount": "1000"},
                    files={"image": ("s.png", _png("PicsArt"), "image/png")}).json()
    assert r["needs_manual"] is True and "busy" in r["error"] and r["error_bn"]
    assert r["image"]["editor"] == "PicsArt" and len(calls) == 6  # 3 tries on each of 2 models


def test_bad_request_is_not_retried(monkeypatch):
    from app import llm
    calls = _gemini_env(monkeypatch, [400])
    with pytest.raises(RuntimeError):
        llm.complete("pretx", "s", "u")
    assert len(calls) == 1


# ------------------------------------------------------- screenshot only (no expected details)
_SS = {"amount": 1500, "trx_id": "8N7A6D5EF3", "datetime": "2026-11-23 10:15", "screen_status": "success",
       "status_bar_visible": True, "status_bar_time": "10:16", "edit_suspicion": "low", "is_payment_screenshot": True}
_TALL = {"format": "PNG", "width": 720, "height": 1600, "editor": None, "hash": 7}


def _ss(**over):
    x = {**_SS, **{k: v for k, v in over.items() if k != "meta"}}
    return proof.check(x, {}, NOW, {}, meta=over.get("meta", _TALL), seen_img=[])


def test_screenshot_only_genuine_is_not_flagged():
    r = _ss()
    assert r["verdict"] == "consistent" and r["compared"] is False
    assert not [c for c in r["checks"] if c["status"] in ("warn", "fail")]


def test_screenshot_only_clock_before_payment():
    r = _ss(status_bar_time="10:05")
    assert any(c["id"] == "clock" and c["status"] == "fail" for c in r["checks"]) and r["verdict"] != "consistent"


def test_screenshot_only_pending_cropped_old():
    assert _ss(screen_status="failed")["verdict"] == "suspicious"
    assert _ss(datetime="2026-11-18 10:15", status_bar_time=None)["verdict"] == "suspicious"
    # no status bar / not tall = normal for receipts shared from the app: noted, not flagged
    assert _ss(status_bar_visible=False, status_bar_time=None)["verdict"] == "consistent"
    assert _ss(meta={**_TALL, "height": 800}, status_bar_time=None)["verdict"] == "consistent"


def test_missing_expectation_is_info_not_warning_when_compared_elsewhere():
    r = proof.check(_SS, {"recipient": "01712345678"}, NOW, {}, meta=_TALL, seen_img=[])
    amount = next(c for c in r["checks"] if c["id"] == "amount")
    assert amount["status"] == "info" and r["compared"] is True


def test_screenshot_only_without_ai_still_reports_image_checks():
    import app.main as m
    m.SEEN_IMG.clear()
    r = client.post("/api/proof", files={"image": ("s.png", _png("PicsArt", size=(800, 700)), "image/png")}).json()
    ids = {c["id"]: c["status"] for c in r["checks"]}
    assert r["needs_manual"] is True and ids["meta_editor"] == "fail" and ids["meta_crop"] == "info"


def test_screenshot_only_api_with_mock_ai(monkeypatch):
    monkeypatch.setenv("MOCK_LLM", "1")
    import app.main as m
    m.SEEN_IMG.clear(); SEEN_TRX.clear()
    r = client.post("/api/proof", files={"image": ("s.png", _png(), "image/png")}).json()
    assert r["needs_manual"] is False and r["compared"] is False
    assert any(c["id"] == "no_expected" for c in r["checks"])


def test_genuine_receipt_with_ai_doubts_is_not_fake():
    """Regression: all facts matched, AI disliked the logo/profile picture, no status bar -> must not be fake."""
    x = {**_SS, "amount": 2050, "recipient": "01712345678", "status_bar_visible": False, "status_bar_time": None,
         "edit_suspicion": "high",
         "visual_flags": ["unusual profile picture and name format for bKash", "bKash logo looks slightly altered"]}
    exp = {"amount": 2050, "recipient": "01712345678", "chat_time": "2026-11-23T10:20", "order_ref": "o"}
    r = proof.check(x, exp, NOW, {}, meta=_TALL, seen_img=[])
    assert r["verdict"] == "consistent" and r["score"] < 30
    visual = next(c for c in r["checks"] if c["id"] == "visual")
    assert visual["status"] == "warn" and "not proof" in visual["en"]


def test_ai_doubt_plus_hard_fact_failure_still_caught():
    x = {**_SS, "amount": 2000, "recipient": "01712345678", "edit_suspicion": "high", "visual_flags": ["amount digits in a different font"]}
    exp = {"amount": 2050, "recipient": "01712345678", "chat_time": "2026-11-23T10:20", "order_ref": "o"}
    assert proof.check(x, exp, NOW, {}, meta=_TALL, seen_img=[])["verdict"] == "likely_fake"


def test_ai_doubt_alone_without_details_is_suspicious_not_fake():
    r = _ss(edit_suspicion="high", visual_flags=["amount digits misaligned"])
    assert r["verdict"] == "suspicious"


# ------------------------------------------------------- real-world timing, masked numbers, amounts
_NOW3 = datetime(2026, 11, 23, 15, 0)
_B3 = {"amount": 1000, "trx_id": "8N7A6D5EF3", "recipient": "01712345678", "datetime": "2026-11-23 14:10",
       "screen_status": "success", "status_bar_visible": True, "status_bar_time": None, "edit_suspicion": "low",
       "is_payment_screenshot": True}
_E3 = {"amount": 1000, "recipient": "01712345678", "chat_time": "2026-11-23T14:00", "order_ref": "o"}


def _r3(x=None, e=None):
    r = proof.check({**_B3, **(x or {})}, {**_E3, **(e or {})}, _NOW3, {},
                    meta={"format": "PNG", "width": 720, "height": 1600, "editor": None, "hash": 3}, seen_img=[])
    return r, {c["id"]: c["status"] for c in r["checks"]}


@pytest.mark.parametrize("x,e,verdict,check,status", [
    ({}, {}, "consistent", "time", "ok"),                                                       # paid 10 min after
    ({"datetime": "2026-11-23 14:55"}, {}, "consistent", "time", "ok"),                         # 55 min after
    ({"datetime": "2026-11-23 13:05"}, {}, "consistent", "time", "ok"),                         # 55 min before
    ({"datetime": "2026-11-23 14:00"}, {"chat_time": "2026-11-23T11:00"}, "consistent", "time", "warn"),  # 3 h after
    ({}, {"chat_time": "2026-11-23T04:00"}, "suspicious", "time", "fail"),                      # 10 h after claim
    ({"datetime": "2026-11-23 02:10"}, {}, "consistent", "time", "info"),                       # AM/PM slip
    ({"datetime": "2026-11-23 08:00"}, {}, "consistent", "time", "info"),                       # paid this morning
    ({"datetime": None}, {}, "consistent", "time", "info"),                                     # no time on receipt
    ({"status_bar_time": "2:15"}, {}, "consistent", "clock", "ok"),                             # 12-hour clock
    ({"status_bar_time": "13:50"}, {}, "suspicious", "clock", "fail"),                          # clock before payment
    ({"recipient": "017XXXXX678"}, {}, "consistent", "recipient", "ok"),                        # masked, matches
    ({"recipient": "017XXXXX999"}, {}, "suspicious", "recipient", "fail"),                      # masked, wrong
    ({"recipient": "Rahim Store"}, {}, "consistent", "recipient", "info"),                      # merchant name
    ({"recipient": "+8801712345678"}, {}, "consistent", "recipient", "ok"),
    ({"amount": 1020}, {}, "consistent", "amount", "warn"),                                     # paid a bit more
    ({"amount": 900}, {}, "suspicious", "amount", "fail"),                                      # paid less
])
def test_real_world_cases(x, e, verdict, check, status):
    r, ids = _r3(x, e)
    assert ids[check] == status and r["verdict"] == verdict


# ------------------------------------------------------- sender / receiver directions
@pytest.mark.parametrize("x,e,check,status", [
    ({"recipient": "01712345678", "sender": "01911111111"}, {"sender": "01911111111"}, "sender", "ok"),
    ({"recipient": "01712345678", "sender": "01922222222"}, {"sender": "01911111111"}, "sender", "warn"),   # family account
    ({"recipient": "01712345678", "sender": None}, {"sender": "01911111111"}, "sender", "info"),          # not shown
    ({"recipient": "01911111111", "sender": "01712345678"}, {}, "recipient", "warn"),                     # seller shown as sender
    ({"recipient": "01899999999", "sender": None}, {}, "recipient", "fail"),                              # went elsewhere
    ({"recipient": "019XXXXX111", "sender": "017XXXXX678"}, {}, "recipient", "warn"),                     # masked, swapped
])
def test_sender_receiver_directions(x, e, check, status):
    r, ids = _r3(x, e)
    assert ids[check] == status


def test_wrong_receiver_message_names_the_number():
    r, _ = _r3({"recipient": "01899999999"})
    c = next(c for c in r["checks"] if c["id"] == "recipient")
    assert "01899999999" in c["en"] and "not your number" in c["en"]


def test_api_accepts_buyer_number():
    SEEN_TRX.clear()
    manual = json.dumps({"amount": "1000", "trx_id": "7Q2W4E6R8T", "recipient": "01712345678",
                         "sender": "01911111111", "datetime": "2026-11-01T10:00"})
    r = client.post("/api/proof", data={"expected_amount": "1000", "expected_recipient": "01712345678",
                                        "expected_sender": "01911111111", "manual": manual}).json()
    ids = {c["id"]: c["status"] for c in r["checks"]}
    assert ids["recipient"] == "ok" and ids["sender"] == "ok"


def test_fully_swapped_numbers_give_one_clear_warning():
    r, ids = _r3({"recipient": "01911111111", "sender": "01712345678"}, {"sender": "01911111111"})
    assert ids["recipient"] == "warn" and "sender" not in ids
    assert "wrong way round" in next(c["en"] for c in r["checks"] if c["id"] == "recipient")


# ------------------------------------------------------- new patterns (authority, tasks, betting, advance, codes)
@pytest.mark.parametrize("text,pid", [
    ("Robi theke bolchi, apnar SIM bondho hoye jabe, mobile e asha code ta bolen", "otp_pin_request"),
    ("থানা থেকে বলছি, আপনার নামে মামলা হয়েছে। এখনই টাকা বিকাশ করুন।", "authority_threat"),
    ("Earn Tk 2,000 daily by liking YouTube videos. Registration fee Tk 300.", "task_scam"),
    ("Aviator game e 200 taka dile 5000 taka jitben", "betting_gambling"),
    ("Flat er advance 10,000 taka bKash korun", "advance_payment"),
])
def test_new_patterns_fire(text, pid):
    assert pid in [p["id"] for p in rules.analyze(text)["patterns"]]


@pytest.mark.parametrize("text", [
    "Grab a coffee and decide later, it is a simple case of fine tuning.",
    "The alphabet song video is on YouTube.",
    "Book a time slot for your account opening at the branch.",
    "Your SIM will be replaced free at any Grameenphone Centre. Never share your PIN with anyone.",
    "Enter the school code at the counter to pay fees.",
])
def test_new_patterns_no_false_alarm(text):
    assert rules.analyze(text)["risk"] == "low", rules.analyze(text)["patterns"]


def test_bangla_digit_numbers_are_compared_correctly():
    r, ids = _r3({"recipient": "01712345678", "sender": "01911111111"},
                 {"recipient": "০১৭১২৩৪৫৬৭৮", "sender": "০১৯১১১১১১১১"})
    assert ids["recipient"] == "ok" and ids["sender"] == "ok"


# ------------------------------------------------------- screen check (photo of a call or message)
from app import screen as scr


def test_number_kinds():
    assert scr.number_kind("16247") == "official"
    assert scr.number_kind("01812345678") == "personal"
    assert scr.number_kind("+880 1812-345678") == "personal"
    assert scr.number_kind("০১৮১২৩৪৫৬৭৮") == "personal"
    assert scr.number_kind("+44 7700 900123") == "foreign"
    assert scr.number_kind("") == "none"


def test_brand_name_on_personal_number_is_high():
    f = scr.flags("call", "01812345678", "bKash Customer Care", "")
    assert f and f[0]["id"] == "brand_from_personal" and f[0]["weight"] >= 65


def test_official_sender_name_is_not_flagged():
    # real bKash SMS come from the sender name "bKash", with no number
    assert scr.flags("sms", None, "bKash", "You have received Tk 500.00 from 01712345678. TrxID 8N7A6D5EF3") == []
    assert scr.flags("call", "16247", "bKash", "") == []


def test_brand_sms_from_personal_number_and_foreign_and_spam():
    assert [x["id"] for x in scr.flags("sms", "01912345678", None, "Your Nagad account will be closed")] == ["brand_sms_from_personal"]
    assert [x["id"] for x in scr.flags("call", "+234 801 234 5678", None, "")] == ["number_foreign"]
    assert [x["id"] for x in scr.flags("call", "01712345678", "Suspected spam", "")] == ["phone_spam_label"]


def _screen_ai(monkeypatch, reply):
    from app import llm
    import app.main as m
    m._hits.clear()  # many screen calls in a row: keep clear of the per-IP rate limit
    monkeypatch.setenv("MOCK_LLM", "1")
    monkeypatch.setattr(llm, "complete", lambda *a, **k: json.dumps(reply) if isinstance(reply, dict) else (_ for _ in ()).throw(reply))


def test_api_screen_sms_scam(monkeypatch):
    monkeypatch.setenv("MOCK_LLM", "1")
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["risk"] == "high" and r["screen"]["kind"] == "sms" and r["screen"]["number_kind"] == "personal"
    assert "PIN" in r["text"] and any(p["id"] == "brand_from_personal" for p in r["patterns"])


def test_api_screen_call_only_is_not_high(monkeypatch):
    _screen_ai(monkeypatch, {"is_phone_screen": True, "kind": "call", "number": "01712345678", "name": None,
                             "text": "", "risk": "low"})
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["risk"] == "low" and r["screen"]["kind"] == "call"
    assert any("hang up" in x["en"] for x in r["reasons"])


def test_api_screen_ai_cannot_lower_risk(monkeypatch):
    _screen_ai(monkeypatch, {"is_phone_screen": True, "kind": "call", "number": "01712345678", "name": "Nagad Agent",
                             "text": "", "risk": "low"})
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["risk"] == "high"


def test_api_screen_not_a_phone_and_busy(monkeypatch):
    from app import llm
    _screen_ai(monkeypatch, {"is_phone_screen": False})
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["needs_text"] is True and r["error_bn"]
    _screen_ai(monkeypatch, llm.AIBusy("503"))
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["needs_text"] is True and "busy" in r["error"]


def test_api_screen_rejects_non_images(monkeypatch):
    monkeypatch.setenv("MOCK_LLM", "1")
    assert client.post("/api/screen", files={"image": ("a.txt", b"hello", "text/plain")}).status_code == 415


def test_outgoing_call_is_labelled_and_judged_as_outgoing(monkeypatch):
    _screen_ai(monkeypatch, {"is_phone_screen": True, "kind": "call", "direction": "outgoing",
                             "number": "16247", "name": "bKash", "text": "", "risk": "low"})
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["screen"]["direction"] == "outgoing" and r["text"].startswith("Outgoing call to")
    assert r["risk"] == "low" and any("calling an official hotline" in x["en"] for x in r["reasons"])


def test_outgoing_call_to_fake_care_number_is_high(monkeypatch):
    _screen_ai(monkeypatch, {"is_phone_screen": True, "kind": "call", "direction": "outgoing",
                             "number": "01812345678", "name": "bKash Customer Care", "text": "", "risk": "low"})
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["risk"] == "high" and any(p["id"] == "calling_fake_care" for p in r["patterns"])


def test_unknown_direction_is_not_called_incoming(monkeypatch):
    _screen_ai(monkeypatch, {"is_phone_screen": True, "kind": "call", "direction": "sideways",
                             "number": "01712345678", "name": None, "text": ""})
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["screen"]["direction"] == "unknown" and "Incoming" not in r["text"]


def test_spam_label_ignored_on_outgoing_call():
    assert scr.flags("call", "01712345678", "Suspected spam", "", "outgoing") == []


# ------------------------------------------------------- number patterns
@pytest.mark.parametrize("num,kind", [
    ("+8801812345678", "personal"), ("01712345678", "personal"), ("০১৭১২৩৪৫৬৭৮", "personal"),
    ("+880181234567", "suspicious"), ("+88018123456789", "suspicious"), ("01212345678", "suspicious"),
    ("16247", "official"), ("+880 2-55663001", "official"), ("999", "official"), ("01500121125", "official"),
    ("09610016247", "ip"), ("0961001624", "suspicious"), ("+2348012345678", "foreign"), ("0044 7700 900123", "foreign"),
    ("26969", "short"), ("Private number", "hidden"), ("02-9550128", "landline"), ("+880 2 55667788", "landline"),
])
def test_number_patterns(num, kind):
    assert scr.classify(num)["kind"] == kind


def test_official_number_shows_company_name():
    assert scr.classify("16167")["label_en"] == "Nagad helpline"
    assert "Nigeria" in scr.classify("+234 801 234 5678")["label_en"]


def test_unknown_bd_number_call_is_low_even_if_ai_says_medium(monkeypatch):
    _screen_ai(monkeypatch, {"is_phone_screen": True, "kind": "call", "direction": "incoming",
                             "number": "+8801712345678", "name": None, "text": "", "risk": "medium",
                             "reasons_en": ["Unknown caller"]})
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["risk"] == "low" and r["screen"]["number_kind"] == "personal"


@pytest.mark.parametrize("num,risk", [("+880181234567", "high"), ("+2348012345678", "medium"),
                                      ("01712345678", "low"), ("16247", "low")])
def test_call_screen_risk_by_number(monkeypatch, num, risk):
    _screen_ai(monkeypatch, {"is_phone_screen": True, "kind": "call", "direction": "incoming",
                             "number": num, "name": None, "text": "", "risk": "low"})
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["risk"] == risk, r


def test_caller_id_spam_label_is_high(monkeypatch):
    _screen_ai(monkeypatch, {"is_phone_screen": True, "kind": "call", "direction": "incoming",
                             "number": "01712345678", "name": None, "text": "Spam - 2,345 reports", "risk": "low"})
    r = client.post("/api/screen", files={"image": ("s.jpg", _png("x"), "image/jpeg")}).json()
    assert r["risk"] == "high"


@pytest.mark.parametrize("num,risk", [("+880181234567", "high"), ("+92 300 1234567", "medium"), ("01812345678", "low")])
def test_message_check_on_just_a_number(monkeypatch, num, risk):
    import app.main as m
    m._hits.clear()
    monkeypatch.setenv("MOCK_LLM", "1")
    r = client.post("/api/pretx", json={"text": num}).json()
    assert r["risk"] == risk and r["screen"]["kind"] == "number"


# ------------------------------------------------------- honesty: what a verdict rests on
from app import honesty as hon


def test_new_scam_with_no_known_pattern_is_not_called_safe(monkeypatch):
    import app.main as m
    m._hits.clear()
    monkeypatch.delenv("MOCK_LLM", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    r = client.post("/api/pretx", json={"text": "Hi, I am your cousin's friend, can you help me with something important today?"}).json()
    assert r["risk"] == "low"  # detection unchanged
    h = r["honesty"]
    assert h["level"] == "unknown_rules_only" and "did not run" in h["en"]
    assert len(h["checklist"]) == 5 and h["tail"]["bn"]


def test_ai_only_warning_is_labelled_as_opinion():
    h = hon.for_message(0, "low", "high", True)
    assert h["level"] == "ai_only" and "not as proof" in h["en"]


def test_ai_found_nothing_still_not_safe():
    h = hon.for_message(0, "low", "low", True)
    assert h["level"] == "unknown" and "does not mean safe" in h["title_en"]


def test_known_pattern_basis():
    assert hon.for_message(2, "high", "high", True)["level"] == "known_pattern"


def test_genuine_payment_that_looks_edited_is_explained_not_accused():
    res = {"verdict": "suspicious", "compared": True, "checks": [
        {"id": "amount", "status": "ok"}, {"id": "recipient", "status": "ok"},
        {"id": "visual", "status": "warn"}, {"id": "meta_editor", "status": "warn"}]}
    h = hon.for_proof(res)
    assert h["level"] == "looks_only" and "genuine" in h["en"] and h["verify_en"]


def test_proof_levels():
    assert hon.for_proof({"verdict": "likely_fake", "checks": [{"id": "amount", "status": "fail"}]})["level"] == "facts_contradict"
    assert hon.for_proof({"verdict": "consistent", "compared": True, "checks": []})["level"] == "no_red_flags"
    assert hon.for_proof({"verdict": "consistent", "compared": False, "checks": []})["level"] == "self_only"
    assert hon.for_proof({"verdict": "suspicious", "checks": [{"id": "time", "status": "warn"}]})["level"] == "details_unclear"


def test_api_proof_has_honesty_and_same_verdict():
    SEEN_TRX.clear()
    manual = json.dumps({"amount": "3500", "trx_id": "8N7A6D5EF3", "recipient": "01712345678"})
    r = client.post("/api/proof", data={"manual": manual, "expected_amount": "3500",
                                        "expected_recipient": "01712345678"}).json()
    assert r["verdict"] in ("consistent", "suspicious") and r["honesty"]["verify_bn"]


# ------------------------------------------------------- typography and reference receipt
def _ext(**over):
    base = {"amount": 3500, "trx_id": "8N7A6D5EF3", "recipient": "01712345678", "datetime": "2026-11-23 11:20",
            "screen_status": "success", "is_payment_screenshot": True}
    base.update(over)
    return base


EXP_T = {"amount": 3500, "recipient": "01712345678", "chat_time": "2026-11-23T11:30", "order_ref": "t"}


def test_bold_amount_is_flagged_with_a_box():
    tc = [{"field": "amount", "issue": "bolder", "confidence": "high", "detail": "x", "box": [400, 300, 460, 700]}]
    r = proof.check(_ext(text_checks=tc), EXP_T, NOW, {})
    t = [c for c in r["checks"] if c["id"] == "typography"]
    assert t and t[0]["status"] == "warn" and "bolder" in t[0]["en"]
    assert r["edit_boxes"][0]["box"] == [400.0, 300.0, 460.0, 700.0] and r["verdict"] == "suspicious"


def test_reference_comparison_makes_a_clear_difference_a_fail():
    tc = [{"field": "amount", "issue": "smaller", "confidence": "high", "box": [400, 300, 460, 700]}]
    r = proof.check(_ext(text_checks=tc, reference_used=True, reference_same_app=True), EXP_T, NOW, {})
    t = [c for c in r["checks"] if c["id"] == "typography"][0]
    assert t["status"] == "fail" and "reference" in t["en"] and r["reference_used"] is True


def test_reference_from_another_app_is_ignored():
    tc = [{"field": "amount", "issue": "smaller", "confidence": "high"}]
    r = proof.check(_ext(text_checks=tc, reference_used=True, reference_same_app=False), EXP_T, NOW, {})
    assert [c for c in r["checks"] if c["id"] == "typography"][0]["status"] == "warn"


def test_low_confidence_and_bad_items_are_dropped():
    tc = [{"field": "amount", "issue": "bolder", "confidence": "low"}, {"field": "logo", "issue": "bolder", "confidence": "high"},
          "junk", {"field": "amount", "issue": "glitter", "confidence": "high"}]
    r = proof.check(_ext(text_checks=tc), EXP_T, NOW, {})
    assert not [c for c in r["checks"] if c["id"] == "typography"] and r["edit_boxes"] == []
    assert r["verdict"] == "consistent"


def test_typography_only_counts_as_looks_for_honesty():
    tc = [{"field": "amount", "issue": "bolder", "confidence": "high"}]
    r = proof.check(_ext(text_checks=tc), EXP_T, NOW, {})
    assert hon.for_proof(r)["level"] == "looks_only"


def test_api_sends_reference_with_the_screenshot(monkeypatch):
    from app import llm
    import app.main as m
    m._hits.clear(); SEEN_TRX.clear()
    seen = {}

    def fake(task, system, user, image=None, **k):
        seen["n"] = len(image) if isinstance(image, list) else 1
        seen["user"] = user
        return json.dumps(_ext(reference_used=True, reference_same_app=True, text_checks=[]))
    monkeypatch.setenv("MOCK_LLM", "1")
    monkeypatch.setattr(llm, "complete", fake)
    r = client.post("/api/proof", data={"expected_amount": "3500", "expected_recipient": "01712345678"},
                    files={"image": ("s.png", _png("x"), "image/png"), "reference": ("r.jpg", _png("y"), "image/jpeg")}).json()
    assert seen["n"] == 2 and "Image 1" in seen["user"] and r["reference_used"] is True
