"""Rules engine for the Pre-transaction Check. Works with no API key and no internet."""
import re
from .library import PATTERNS, SAFE_NOTE_EN, SAFE_NOTE_BN

HIGH_AT = 65
MEDIUM_AT = 30


def _norm(text: str) -> str:
    text = (text or "").lower()
    # Bangla digits -> ASCII so patterns with \d work on both
    text = text.translate(str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789"))
    return re.sub(r"\s+", " ", text).strip()


def _any(patterns, text):
    return any(re.search(p, text) for p in patterns)


def analyze(text: str) -> dict:
    t = _norm(text)
    matches = []
    score = 0
    for p in PATTERNS:
        if p["unless"] and _any(p["unless"], t):
            continue
        if all(_any(group, t) for group in p["groups"]):
            matches.append(p)
            score += p["weight"]
    score = min(score, 100)
    risk = "high" if score >= HIGH_AT else "medium" if score >= MEDIUM_AT else "low"
    # the strongest matched pattern gives the headline advice
    top = max(matches, key=lambda p: p["weight"]) if matches else None
    return {
        "risk": risk,
        "score": score,
        "patterns": [
            {
                "id": p["id"],
                "name_en": p["name_en"],
                "name_bn": p["name_bn"],
                "why_en": p["why_en"],
                "why_bn": p["why_bn"],
            }
            for p in sorted(matches, key=lambda p: -p["weight"])
        ],
        "advice_en": top["advice_en"] if top else SAFE_NOTE_EN,
        "advice_bn": top["advice_bn"] if top else SAFE_NOTE_BN,
    }
