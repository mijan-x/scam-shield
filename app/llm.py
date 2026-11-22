"""Thin LLM client. One function, so you can swap the provider in one place.

Set GEMINI_API_KEY (Google AI Studio, has a free tier) or ANTHROPIC_API_KEY to
enable AI features. If both are set, Gemini is used. Without either the app still works in
"rules mode": rules-based message check, manual fields for the Payment Proof Check
and the scripted Scam Trainer. Set MOCK_LLM=1 to develop without any key.
"""
import json
import os
import re
from typing import Optional, Tuple

MODEL = os.getenv("SHIELD_MODEL", "claude-sonnet-5-5")
GEMINI_MODEL_DEFAULT = "gemini-3.5-flash-lite"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
JSON_TASKS = {"pretx", "extract", "trainer_grade"}


def provider() -> Optional[str]:
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    return None


def model_name() -> Optional[str]:
    p = provider()
    if p == "gemini":
        return os.getenv("GEMINI_MODEL") or GEMINI_MODEL_DEFAULT
    return MODEL if p == "anthropic" else None


def available() -> bool:
    return provider() is not None or os.getenv("MOCK_LLM") == "1"


def mode() -> str:
    if os.getenv("MOCK_LLM") == "1":
        return "mock"
    return "live" if provider() else "rules"


def extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model reply (tolerates code fences)."""
    if not text:
        raise ValueError("empty reply")
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object in reply")
    return json.loads(text[start : end + 1])


def _mock(task: str, user: str) -> str:
    if task == "pretx":
        return json.dumps({
            "risk": "high" if re.search(r"pin|otp|পিন|ওটিপি", user.lower()) else "low",
            "pattern_ids": ["otp_pin_request"] if re.search(r"pin|otp|পিন|ওটিপি", user.lower()) else [],
            "reasons_en": ["(mock) The message asks for a secret code."],
            "reasons_bn": ["(মক) বার্তায় গোপন কোড চাওয়া হয়েছে।"],
            "advice_en": "(mock) Do not share it.",
            "advice_bn": "(মক) এটি কাউকে দেবেন না।",
        })
    if task == "extract":
        return json.dumps({
            "is_payment_screenshot": True, "provider": "bkash", "amount": 5000,
            "trx_id": "8N7A6D5EF3", "sender": "01700000000", "recipient": "01800000000",
            "datetime": "2026-11-23 10:15", "visual_flags": ["(mock) spacing around the amount looks uneven"],
            "edit_suspicion": "medium", "notes": "mock extraction",
        })
    if task == "trainer_chat":
        return "(mock scammer) Please hurry, I need the money back now!"
    if task == "trainer_grade":
        return json.dumps({
            "caught": ["(mock) you checked your own account"],
            "missed": ["(mock) you almost shared a code"],
            "tip_en": "(mock) Never share a PIN or OTP.",
            "tip_bn": "(মক) পিন বা ওটিপি কখনো দেবেন না।",
            "score": 70,
        })
    return "{}"


def complete(task: str, system: str, user: str, image: Optional[Tuple[bytes, str]] = None,
             max_tokens: int = 1200) -> str:
    """Return the model's text reply. `image` is (bytes, media_type)."""
    if os.getenv("MOCK_LLM") == "1":
        return _mock(task, user)
    p = provider()
    if p is None:
        raise RuntimeError("No GEMINI_API_KEY or ANTHROPIC_API_KEY set")
    if p == "gemini":
        return _gemini(task, system, user, image, max_tokens)
    import base64
    import anthropic

    client = anthropic.Anthropic(timeout=45.0)
    content = []
    if image:
        data, media_type = image
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": base64.b64encode(data).decode()},
        })
    content.append({"type": "text", "text": user})
    msg = client.messages.create(
        model=MODEL, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": content}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


def _gemini(task: str, system: str, user: str, image: Optional[Tuple[bytes, str]], max_tokens: int) -> str:
    """Call the Gemini REST API directly (no extra SDK needed)."""
    import base64
    import httpx

    parts = []
    if image:
        data, media_type = image
        parts.append({"inline_data": {"mime_type": media_type, "data": base64.b64encode(data).decode()}})
    parts.append({"text": user})
    # thinking models spend part of the output budget on reasoning, so give them room
    config = {"maxOutputTokens": max(max_tokens * 2, 2048)}
    if task in JSON_TASKS:
        config["responseMimeType"] = "application/json"
    body = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": config,
    }
    r = httpx.post(GEMINI_URL.format(model=model_name()), json=body, timeout=45.0,
                   headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    if r.status_code != 200:
        try:
            msg = r.json().get("error", {}).get("message", "")
        except ValueError:
            msg = r.text
        raise RuntimeError(f"Gemini error {r.status_code}: {msg[:150]}")
    cands = r.json().get("candidates") or []
    if not cands:
        raise RuntimeError("Gemini returned no answer (possibly blocked by safety filters)")
    return "".join(pt.get("text", "") for pt in cands[0].get("content", {}).get("parts", []) if not pt.get("thought"))
