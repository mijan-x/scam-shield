"""Thin LLM client. One function, so you can swap the provider in one place.

Set GEMINI_API_KEY (Google AI Studio, has a free tier) or ANTHROPIC_API_KEY to
enable AI features. If both are set, Gemini is used. Without either the app still works in
"rules mode": rules-based message check, manual fields for the Payment Proof Check
and the scripted Scam Trainer. Set MOCK_LLM=1 to develop without any key.
"""
import hashlib
import json
import os
import time
import re
from collections import OrderedDict
from typing import Optional, Tuple

MODEL = os.getenv("SHIELD_MODEL", "claude-sonnet-5-5")
GEMINI_MODEL_DEFAULT = "gemini-3.5-flash-lite"
GEMINI_FALLBACK_DEFAULT = "gemini-3.8-flash"  # tried when the main model is overloaded
TRANSIENT = {429, 500, 502, 503, 504}


class AIBusy(RuntimeError):
    """The AI provider is overloaded or rate-limited; worth trying again later."""
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
JSON_TASKS = {"pretx", "extract", "trainer_grade", "screen"}


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


def can_transcribe() -> bool:
    """Speech-to-text needs Gemini (Claude does not take audio) or mock mode."""
    return os.getenv("MOCK_LLM") == "1" or provider() == "gemini"


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
            "datetime": "2026-11-23 10:15", "screen_status": "success", "status_bar_visible": True,
            "status_bar_time": "10:16", "visual_flags": ["(mock) spacing around the amount looks uneven"],
            "edit_suspicion": "medium", "notes": "mock extraction",
            "text_checks": [{"field": "amount", "issue": "bolder", "confidence": "medium",
                             "detail": "(mock) the amount digits look heavier than the other digits",
                             "box": [420, 300, 470, 700]}],
            "reference_used": "Image 1" in user, "reference_same_app": True,
        })
    if task == "screen":
        return json.dumps({
            "is_phone_screen": True, "kind": "sms", "number": "01812345678", "name": "bKash Care",
            "text": "Apnar bKash account block hoye jabe. Ekhoni ei number e call kore PIN ta bolun.",
            "risk": "high", "pattern_ids": ["otp_pin_request"],
            "reasons_en": ["(mock) It asks for your PIN."], "reasons_bn": ["(মক) পিন চাওয়া হয়েছে।"],
            "advice_en": "(mock) Do not share it.", "advice_bn": "(মক) এটি কাউকে দেবেন না।",
        })
    if task == "trainer_chat":
        return "(mock scammer) Please hurry, I need the money back now!"
    if task == "transcribe":
        return "Apnar bKash account block hoye jabe, ekhoni PIN ta bolun"
    if task == "trainer_grade":
        return json.dumps({
            "caught": ["(mock) you checked your own account"],
            "missed": ["(mock) you almost shared a code"],
            "tip_en": "(mock) Never share a PIN or OTP.",
            "tip_bn": "(মক) পিন বা ওটিপি কখনো দেবেন না।",
            "score": 70,
        })
    return "{}"


_CACHE: "OrderedDict[str, Tuple[float, str]]" = OrderedDict()
CACHE_SIZE, CACHE_TTL = 256, 6 * 3600


def _cache_key(task, system, user, image) -> str:
    h = hashlib.sha256()
    for part in (task, system, user):
        h.update(part.encode("utf-8", "replace") + b"\0")
    for data, _ in _as_list(image):
        h.update(data)
    return h.hexdigest()


def complete(task: str, system: str, user: str, image: Optional[Tuple[bytes, str]] = None,
             max_tokens: int = 1200) -> str:
    """Return the model's text reply. `image` is (bytes, media_type): an image, or audio for Gemini.

    The same request (same screenshot, same message) is answered from a short memory instead of
    calling the AI again, which saves the free-tier quota when a demo repeats an example."""
    if os.getenv("MOCK_LLM") == "1":
        return _mock(task, user)
    if provider() is None:
        raise RuntimeError("No GEMINI_API_KEY or ANTHROPIC_API_KEY set")
    key = _cache_key(task, system, user, image)
    hit = _CACHE.get(key)
    if hit and time.time() - hit[0] < CACHE_TTL:
        _CACHE.move_to_end(key)
        return hit[1]
    text = _complete(task, system, user, image, max_tokens)
    if text and text.strip():
        _CACHE[key] = (time.time(), text)
        while len(_CACHE) > CACHE_SIZE:
            _CACHE.popitem(last=False)
    return text


def _complete(task, system, user, image, max_tokens) -> str:
    if provider() == "gemini":
        try:
            return _gemini(task, system, user, image, max_tokens)
        except AIBusy:
            # Claude as a backup when both keys are set (it cannot take audio)
            if os.getenv("ANTHROPIC_API_KEY") and task != "transcribe":
                return _claude(system, user, image, max_tokens)
            raise
    return _claude(system, user, image, max_tokens)


def _claude(system, user, image, max_tokens) -> str:
    import base64
    import anthropic

    client = anthropic.Anthropic(timeout=45.0)
    content = []
    for data, media_type in _as_list(image):
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": media_type, "data": base64.b64encode(data).decode()},
        })
    content.append({"type": "text", "text": user})
    try:
        msg = client.messages.create(
            model=MODEL, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": content}],
        )
    except anthropic.APIStatusError as e:
        if e.status_code in TRANSIENT or e.status_code == 529:
            raise AIBusy(f"Claude error {e.status_code}") from e
        raise
    except anthropic.APIConnectionError as e:
        raise AIBusy("Claude connection problem") from e
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


def _as_list(image) -> list:
    """One (bytes, media_type) pair, a list of them, or None."""
    if not image:
        return []
    return list(image) if isinstance(image, list) else [image]


def _fallbacks() -> list:
    """Gemini models to try, in order: the main model, then GEMINI_FALLBACK_MODEL (comma-separated)."""
    models = [model_name()]
    for m in os.getenv("GEMINI_FALLBACK_MODEL", GEMINI_FALLBACK_DEFAULT).split(","):
        m = m.strip()
        if m and m not in models:
            models.append(m)
    return models


def _retry_delay(r) -> Optional[float]:
    """Seconds Google asks us to wait (Retry-After header or RetryInfo), if it says."""
    try:
        if r.headers.get("retry-after"):
            return float(r.headers["retry-after"])
        for d in r.json().get("error", {}).get("details", []):
            if str(d.get("retryDelay", "")).endswith("s"):
                return float(d["retryDelay"][:-1])
    except (ValueError, TypeError, AttributeError):
        pass
    return None


def _gemini(task: str, system: str, user: str, image: Optional[Tuple[bytes, str]], max_tokens: int) -> str:
    """Call the Gemini REST API directly (no extra SDK needed).

    Busy answers (429/5xx) are retried with growing waits, then the next model is tried, all
    inside a time budget (AI_TIME_BUDGET seconds, default 30) so the page never hangs."""
    import base64
    import random
    import httpx

    parts = []
    for data, media_type in _as_list(image):
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
    headers = {"x-goog-api-key": os.environ["GEMINI_API_KEY"]}
    deadline = time.monotonic() + float(os.getenv("AI_TIME_BUDGET", "30"))
    waits = (1.0, 2.5)  # waits before the 2nd and 3rd try of the same model
    last: Exception = AIBusy("Gemini is unavailable")
    was_busy = False
    models = _fallbacks()
    for n, model in enumerate(models):
        for attempt in range(len(waits) + 1):
            left = deadline - time.monotonic()
            if left < 3:
                raise last if was_busy else AIBusy("Gemini took too long")
            try:
                r = httpx.post(GEMINI_URL.format(model=model), json=body, timeout=min(30.0, left), headers=headers)
            except (httpx.TimeoutException, httpx.TransportError) as e:
                last, was_busy = AIBusy(f"Gemini connection problem: {type(e).__name__}"), True
                break  # a slow model: try the next one
            if r.status_code == 200:
                return _gemini_text(r.json())
            try:
                msg = r.json().get("error", {}).get("message", "")
            except ValueError:
                msg = r.text
            if r.status_code in TRANSIENT:
                last, was_busy = AIBusy(f"Gemini error {r.status_code} on {model}: {msg[:150]}"), True
                if "per day" in msg.lower() or attempt == len(waits):
                    break  # daily quota used up, or still busy: move on to the next model
                wait = _retry_delay(r) or waits[attempt] * (1 + random.random() * 0.3)
                if wait > 8 or wait > deadline - time.monotonic() - 3:
                    break  # asked to wait too long: the next model is quicker
                time.sleep(wait)
                continue
            if r.status_code == 404:
                if n + 1 < len(models):
                    break  # model not available on this key: try the next one
                if was_busy:
                    raise last  # an earlier model was only busy
            raise RuntimeError(f"Gemini error {r.status_code}: {msg[:150]}")
    raise last


def _gemini_text(data: dict) -> str:
    cands = data.get("candidates") or []
    if not cands:
        raise RuntimeError("Gemini returned no answer (possibly blocked by safety filters)")
    return "".join(pt.get("text", "") for pt in cands[0].get("content", {}).get("parts", []) if not pt.get("thought"))
