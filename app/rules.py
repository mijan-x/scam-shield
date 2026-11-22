"""Rules engine for the Pre-transaction Check. Works with no API key and no internet.

Returns a risk level, the matched patterns with plain-language reasons, the exact
phrases that triggered them (character spans in the ORIGINAL text, for highlighting),
and the links / phone numbers found in the message.
"""
import re

from . import entities as ent
from .library import HOTLINES, PATTERNS, SAFE_NOTE_BN, SAFE_NOTE_EN

HIGH_AT = 65
MEDIUM_AT = 30
MAX_SPANS_PER_GROUP = 3
_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def _norm(text: str) -> str:
    """Normalised text used for the yes/no decisions (whitespace collapsed)."""
    text = (text or "").lower().translate(_DIGITS)
    return re.sub(r"\s+", " ", text).strip()


def _same_len(text: str) -> str:
    """Normalised text with exactly the same length as the original, so match
    positions can be mapped back for highlighting."""
    low = "".join(c.lower() if len(c.lower()) == 1 else c for c in text)
    low = low.translate(_DIGITS)
    return "".join(" " if c.isspace() else c for c in low)


def _any(patterns, text):
    return any(re.search(p, text) for p in patterns)


def _spans_for(pattern, text):
    out = []
    for group in pattern["groups"]:
        for rx in group:
            for k, m in enumerate(re.finditer(rx, text)):
                if k >= MAX_SPANS_PER_GROUP:
                    break
                if m.end() > m.start():
                    out.append((m.start(), m.end()))
    return out


def _merge(spans):
    """Drop overlapping spans, keeping the stronger (danger before caution), then earlier."""
    order = {"danger": 0, "caution": 1}
    chosen = []
    for s in sorted(spans, key=lambda x: (order[x[2]], x[0])):
        if all(s[1] <= c[0] or s[0] >= c[1] for c in chosen):
            chosen.append(s)
    return sorted(chosen)


def _public(p):
    return {k: p[k] for k in ("id", "name_en", "name_bn", "why_en", "why_bn")} | {"weight": p["weight"]}


def analyze(text: str) -> dict:
    text = text or ""
    t = _norm(text)
    tl = _same_len(text)
    matches, spans = [], []
    for p in PATTERNS:
        if p["unless"] and _any(p["unless"], t):
            continue
        if all(_any(group, t) for group in p["groups"]):
            matches.append(p)
            kind = "danger" if p["weight"] >= 60 else "caution"
            spans += [(a, b, kind, p["id"]) for a, b in _spans_for(p, tl)]

    found, synth, ent_spans = ent.analyze(tl)
    matches += synth
    spans += ent_spans

    score = min(sum(p["weight"] for p in matches), 100)
    risk = "high" if score >= HIGH_AT else "medium" if score >= MEDIUM_AT else "low"
    ordered = sorted(matches, key=lambda p: -p["weight"])
    top = ordered[0] if ordered else None
    names = {p["id"]: (p["name_en"], p["name_bn"]) for p in matches}
    highlights = [
        {"start": a, "end": b, "kind": k, "pattern": pid,
         "label_en": names.get(pid, ("", ""))[0], "label_bn": names.get(pid, ("", ""))[1]}
        for a, b, k, pid in _merge(spans)
    ]
    return {
        "risk": risk,
        "score": score,
        "patterns": [_public(p) for p in ordered],
        "highlights": highlights,
        "entities": found,
        "advice_en": top["advice_en"] if top else SAFE_NOTE_EN,
        "advice_bn": top["advice_bn"] if top else SAFE_NOTE_BN,
        "hotlines": HOTLINES,
    }
