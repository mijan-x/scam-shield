"""Find and judge the links and phone numbers inside a message.

Each finding can add a synthetic "pattern" to the rules result, so links and numbers
are explained to the user in the same way as text patterns.

All settings and texts live in the constants below and are exported by /api/rules,
so the in-browser (offline) engine in static/engine.js uses exactly the same data.
"""
import re
from urllib.parse import urlparse

OFFICIAL_DOMAINS = {
    "bkash.com": "bKash", "nagad.com.bd": "Nagad", "dutchbanglabank.com": "Rocket (DBBL)",
    "upaybd.com": "Upay", "bb.org.bd": "Bangladesh Bank",
}
BRANDS = r"bkash|bikash|nagad|rocket|upay|dbbl|dutchbangla|bangladeshbank"
SHORTENERS = ["bit.ly", "tinyurl.com", "cutt.ly", "t.co", "rb.gy", "is.gd", "shorturl.at", "tiny.cc",
              "ow.ly", "s.id", "rebrand.ly", "goo.gl", "t.ly", "v.gd", "shorte.st"]
RISKY_TLDS = ["xyz", "top", "click", "icu", "buzz", "online", "site", "live", "shop", "info", "link", "gq",
              "tk", "ml", "cf", "ga", "cc", "biz", "win", "vip", "loan", "work", "rest", "cyou", "sbs", "cfd"]
HOTLINES = {"16247": "bKash", "16167": "Nagad", "16216": "Rocket", "16268": "Upay"}

URL_PATTERN = (
    r"(?:https?://|www\.)[^\s<>\"']+"
    r"|\b(?:[a-z0-9-]+\.)+(?:com|net|org|xyz|top|click|icu|buzz|online|site|live|shop|info|link|me|ly|io|co|bd"
    r"|gq|tk|ml|cf|ga|cc|biz|win|vip|loan|work|rest|cyou|sbs|cfd|at|gd)(?:\.[a-z]{2})?(?:/[^\s<>\"']*)?"
)
PHONE_PATTERN = r"(?<!\d)(?:\+?880|0)1[3-9]\d{8}(?!\d)"
HOTLINE_PATTERN = r"(?<!\d)(16247|16167|16216|16268)(?!\d)"
CARE_PATTERN = (r"bkash|bikash|nagad|rocket|upay|বিকাশ|নগদ|রকেট|customer care|কাস্টমার কেয়ার|head office|"
                r"হেড অফিস|helpline|হেল্পলাইন|agent|এজেন্ট|office|অফিস")
TRAIL = ".,;:!?)।'\""

URL_RE = re.compile(URL_PATTERN, re.I)
PHONE_RE = re.compile(PHONE_PATTERN)
HOTLINE_RE = re.compile(HOTLINE_PATTERN)
CARE_RE = re.compile(CARE_PATTERN)
BRANDS_RE = re.compile(BRANDS)

LINK_ADVICE_EN = "Do not open the link or enter any details. Open the official app yourself instead."
LINK_ADVICE_BN = "লিংকে ঢুকবেন না, কোনো তথ্য দেবেন না। দরকার হলে নিজে অফিসিয়াল অ্যাপ খুলুন।"

# Reason texts; {host}, {tld}, {name} are filled in.
REASONS = {
    "official": ("Official {name} domain. Still, never enter your PIN on a page you reached from a message.",
                 "{name}-এর অফিসিয়াল ডোমেইন। তবুও মেসেজের লিংক থেকে কোনো পেজে পিন দেবেন না।"),
    "lookalike": ("Uses a provider's name but '{host}' is not an official domain.",
                  "প্রতিষ্ঠানের নাম ব্যবহার করছে, কিন্তু '{host}' অফিসিয়াল ডোমেইন নয়।"),
    "short": ("Shortened link: you cannot see where it really goes.",
              "ছোট করা লিংক: আসলে কোথায় নিয়ে যাবে তা বোঝা যায় না।"),
    "tld": ("Ends in .{tld}, a cheap domain often used for scam sites.",
            ".{tld} দিয়ে শেষ, এমন সস্তা ডোমেইন প্রায়ই প্রতারণায় ব্যবহৃত হয়।"),
    "ip": ("The address is a raw IP number or a disguised international name.",
           "ঠিকানাটি সরাসরি আইপি নম্বর বা ছদ্মবেশী নাম।"),
    "unknown_link": ("Unknown website. Be careful before opening it.",
                     "অপরিচিত ওয়েবসাইট। খোলার আগে সতর্ক থাকুন।"),
    "hotline": ("Official {name} hotline.", "{name}-এর অফিসিয়াল হটলাইন।"),
    "care_number": ("A personal mobile number. Provider support never calls or texts from a personal 01… number.",
                    "এটি ব্যক্তিগত মোবাইল নম্বর। প্রতিষ্ঠানের সাপোর্ট কখনো ব্যক্তিগত 01… নম্বর থেকে ফোন বা মেসেজ দেয় না।"),
    "number": ("A mobile number. Check who it belongs to before sending money.",
               "একটি মোবাইল নম্বর। টাকা পাঠানোর আগে নম্বরটি কার তা যাচাই করুন।"),
}


def _synth(pid, weight, name_en, name_bn, why_en, why_bn, advice_en=LINK_ADVICE_EN, advice_bn=LINK_ADVICE_BN):
    return {"id": pid, "weight": weight, "name_en": name_en, "name_bn": name_bn, "why_en": why_en,
            "why_bn": why_bn, "advice_en": advice_en, "advice_bn": advice_bn}


SYNTH = {
    "lookalike_link": _synth(
        "lookalike_link", 70, "Fake look-alike link", "নকল লিংক",
        "The link pretends to belong to bKash, Nagad or another provider but goes to a different website.",
        "লিংকটি বিকাশ, নগদ বা অন্য প্রতিষ্ঠানের মনে হলেও আসলে অন্য ওয়েবসাইটে নিয়ে যায়।"),
    "short_link": _synth(
        "short_link", 30, "Hidden (shortened) link", "লুকানো (ছোট করা) লিংক",
        "A shortened link hides the real website address.", "ছোট করা লিংক আসল ওয়েবসাইটের ঠিকানা লুকিয়ে রাখে।"),
    "risky_domain": _synth(
        "risky_domain", 30, "Risky website address", "ঝুঁকিপূর্ণ ওয়েবসাইট ঠিকানা",
        "The link uses a kind of domain that is common in scam messages.",
        "লিংকটিতে এমন ডোমেইন আছে যা প্রতারণার মেসেজে প্রায়ই দেখা যায়।"),
    "hidden_owner": _synth(
        "risky_domain", 40, "Risky website address", "ঝুঁকিপূর্ণ ওয়েবসাইট ঠিকানা",
        "The link hides its real owner.", "লিংকটির আসল মালিক লুকানো।"),
    "unknown_link": _synth(
        "unknown_link", 15, "Contains a link", "লিংক আছে",
        "The message contains a link to a website we cannot vouch for.",
        "মেসেজে এমন একটি লিংক আছে যা আমরা নিশ্চিত করতে পারি না।"),
    "personal_number_care": _synth(
        "personal_number_care", 35, "'Support' from a personal number", "ব্যক্তিগত নম্বর থেকে 'সাপোর্ট'",
        "The message mentions a provider or customer care but gives a personal mobile number.",
        "মেসেজে প্রতিষ্ঠান বা কাস্টমার কেয়ারের কথা আছে, কিন্তু একটি ব্যক্তিগত মোবাইল নম্বর দেওয়া হয়েছে।",
        "Call only the official hotline printed on the provider's app or website.",
        "শুধু প্রতিষ্ঠানের অ্যাপ বা ওয়েবসাইটে দেওয়া অফিসিয়াল হটলাইনে ফোন করুন।"),
}


def export() -> dict:
    """Everything the browser engine needs, as plain JSON."""
    return {
        "official_domains": OFFICIAL_DOMAINS, "brands": BRANDS, "shorteners": SHORTENERS,
        "risky_tlds": RISKY_TLDS, "hotlines": HOTLINES, "url": URL_PATTERN, "phone": PHONE_PATTERN,
        "hotline": HOTLINE_PATTERN, "care": CARE_PATTERN, "trail": TRAIL,
        "reasons": {k: {"en": v[0], "bn": v[1]} for k, v in REASONS.items()}, "synth": SYNTH,
    }


def _r(key, **kw):
    en, bn = REASONS[key]
    return en.format(**kw), bn.format(**kw)


def _host(url: str) -> str:
    u = url if re.match(r"https?://", url, re.I) else "http://" + url
    try:
        return (urlparse(u).hostname or "").lower().strip(".")
    except ValueError:
        return ""


def _official(host: str):
    for d, name in OFFICIAL_DOMAINS.items():
        if host == d or host.endswith("." + d):
            return name
    return None


def analyze(text: str):
    """text: same-length normalised text (lower case). Returns (entities, synthetic_patterns, spans)."""
    entities, synth, spans = [], {}, []

    for m in URL_RE.finditer(text):
        raw = m.group().rstrip(TRAIL)
        host = _host(raw)
        if not host or "." not in host:
            continue
        start, end = m.start(), m.start() + len(raw)
        en, bn, verdict = [], [], "unknown"

        def say(key, **kw):
            a, b = _r(key, **kw)
            en.append(a)
            bn.append(b)

        official = _official(host)
        tld = host.rsplit(".", 1)[-1]
        if official:
            verdict = "official"
            say("official", name=official)
        else:
            if BRANDS_RE.search(host) or (host in SHORTENERS and BRANDS_RE.search(raw.lower())):
                verdict = "danger"
                say("lookalike", host=host)
                synth["lookalike_link"] = SYNTH["lookalike_link"]
            if host in SHORTENERS:
                verdict = "danger" if verdict == "danger" else "caution"
                say("short")
                synth.setdefault("short_link", SYNTH["short_link"])
            if tld in RISKY_TLDS:
                verdict = "danger" if verdict == "danger" else "caution"
                say("tld", tld=tld)
                synth.setdefault("risky_domain", SYNTH["risky_domain"])
            if re.fullmatch(r"[\d.]+", host) or host.startswith("xn--") or ".xn--" in host:
                verdict = "danger"
                say("ip")
                synth.setdefault("risky_domain", SYNTH["hidden_owner"])
            if verdict == "unknown":
                verdict = "caution"
                say("unknown_link")
                synth.setdefault("unknown_link", SYNTH["unknown_link"])
        entities.append({"kind": "link", "text": raw, "host": host, "verdict": verdict,
                         "reasons_en": en, "reasons_bn": bn})
        if verdict in ("danger", "caution"):
            spans.append((start, end, verdict, "lookalike_link" if verdict == "danger" else "short_link"))

    care_context = bool(CARE_RE.search(text))
    for m in HOTLINE_RE.finditer(text):
        a, b = _r("hotline", name=HOTLINES[m.group(1)])
        entities.append({"kind": "phone", "text": m.group(1), "verdict": "official", "reasons_en": [a], "reasons_bn": [b]})
    for m in PHONE_RE.finditer(text):
        if care_context:
            a, b = _r("care_number")
            entities.append({"kind": "phone", "text": m.group(), "verdict": "caution", "reasons_en": [a], "reasons_bn": [b]})
            spans.append((m.start(), m.end(), "caution", "personal_number_care"))
            synth.setdefault("personal_number_care", SYNTH["personal_number_care"])
        else:
            a, b = _r("number")
            entities.append({"kind": "phone", "text": m.group(), "verdict": "unknown", "reasons_en": [a], "reasons_bn": [b]})
    return entities, list(synth.values()), spans
