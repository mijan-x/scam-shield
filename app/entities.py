"""Find and judge the links and phone numbers inside a message.

Each finding can add a synthetic "pattern" to the rules result, so links and numbers
are explained to the user in the same way as text patterns.
"""
import re
from urllib.parse import urlparse

OFFICIAL_DOMAINS = {
    "bkash.com": "bKash", "nagad.com.bd": "Nagad", "dutchbanglabank.com": "Rocket (DBBL)",
    "upaybd.com": "Upay", "bb.org.bd": "Bangladesh Bank",
}
BRANDS = re.compile(r"bkash|bikash|nagad|rocket|upay|dbbl|dutchbangla|bangladeshbank")
SHORTENERS = {"bit.ly", "tinyurl.com", "cutt.ly", "t.co", "rb.gy", "is.gd", "shorturl.at", "tiny.cc",
              "ow.ly", "s.id", "rebrand.ly", "goo.gl", "t.ly", "v.gd", "shorte.st"}
RISKY_TLDS = {"xyz", "top", "click", "icu", "buzz", "online", "site", "live", "shop", "info", "link", "gq",
              "tk", "ml", "cf", "ga", "cc", "biz", "win", "vip", "loan", "work", "rest", "cyou", "sbs", "cfd"}
HOTLINES = {
    "16247": "bKash", "16167": "Nagad", "16216": "Rocket", "16268": "Upay",
}

URL_RE = re.compile(
    r"(?:https?://|www\.)[^\s<>\"']+"
    r"|\b(?:[a-z0-9-]+\.)+(?:com|net|org|xyz|top|click|icu|buzz|online|site|live|shop|info|link|me|ly|io|co|bd"
    r"|gq|tk|ml|cf|ga|cc|biz|win|vip|loan|work|rest|cyou|sbs|cfd|at|gd)(?:\.[a-z]{2})?(?:/[^\s<>\"']*)?",
    re.I,
)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?880|0)1[3-9]\d{8}(?!\d)")
HOTLINE_RE = re.compile(r"(?<!\d)(16247|16167|16216|16268)(?!\d)")
CARE_RE = re.compile(r"bkash|bikash|nagad|rocket|upay|বিকাশ|নগদ|রকেট|customer care|কাস্টমার কেয়ার|head office|"
                     r"হেড অফিস|helpline|হেল্পলাইন|agent|এজেন্ট|office|অফিস")


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


def _synth(pid, weight, name_en, name_bn, why_en, why_bn, advice_en, advice_bn):
    return {"id": pid, "weight": weight, "name_en": name_en, "name_bn": name_bn, "why_en": why_en,
            "why_bn": why_bn, "advice_en": advice_en, "advice_bn": advice_bn}


LINK_ADVICE_EN = "Do not open the link or enter any details. Open the official app yourself instead."
LINK_ADVICE_BN = "লিংকে ঢুকবেন না, কোনো তথ্য দেবেন না। দরকার হলে নিজে অফিসিয়াল অ্যাপ খুলুন।"


def analyze(text: str):
    """text: same-length normalised text (lower case). Returns (entities, synthetic_patterns, spans)."""
    entities, synth, spans = [], {}, []

    for m in URL_RE.finditer(text):
        raw = m.group().rstrip(".,;:!?)।'\"")
        host = _host(raw)
        if not host or "." not in host:
            continue
        start, end = m.start(), m.start() + len(raw)
        reasons_en, reasons_bn, verdict = [], [], "unknown"
        official = _official(host)
        tld = host.rsplit(".", 1)[-1]
        if official:
            verdict = "official"
            reasons_en.append(f"Official {official} domain. Still, never enter your PIN on a page you reached from a message.")
            reasons_bn.append(f"{official}-এর অফিসিয়াল ডোমেইন। তবুও মেসেজের লিংক থেকে কোনো পেজে পিন দেবেন না।")
        else:
            if BRANDS.search(host) or (host in SHORTENERS and BRANDS.search(raw.lower())):
                verdict = "danger"
                reasons_en.append(f"Uses a provider's name but '{host}' is not an official domain.")
                reasons_bn.append(f"প্রতিষ্ঠানের নাম ব্যবহার করছে, কিন্তু '{host}' অফিসিয়াল ডোমেইন নয়।")
                synth["lookalike_link"] = _synth(
                    "lookalike_link", 70, "Fake look-alike link", "নকল লিংক",
                    "The link pretends to belong to bKash, Nagad or another provider but goes to a different website.",
                    "লিংকটি বিকাশ, নগদ বা অন্য প্রতিষ্ঠানের মনে হলেও আসলে অন্য ওয়েবসাইটে নিয়ে যায়।",
                    LINK_ADVICE_EN, LINK_ADVICE_BN)
            if host in SHORTENERS:
                verdict = "danger" if verdict == "danger" else "caution"
                reasons_en.append("Shortened link: you cannot see where it really goes.")
                reasons_bn.append("ছোট করা লিংক: আসলে কোথায় নিয়ে যাবে তা বোঝা যায় না।")
                synth.setdefault("short_link", _synth(
                    "short_link", 30, "Hidden (shortened) link", "লুকানো (ছোট করা) লিংক",
                    "A shortened link hides the real website address.", "ছোট করা লিংক আসল ওয়েবসাইটের ঠিকানা লুকিয়ে রাখে।",
                    LINK_ADVICE_EN, LINK_ADVICE_BN))
            if tld in RISKY_TLDS:
                verdict = "danger" if verdict == "danger" else "caution"
                reasons_en.append(f"Ends in .{tld}, a cheap domain often used for scam sites.")
                reasons_bn.append(f".{tld} দিয়ে শেষ, এমন সস্তা ডোমেইন প্রায়ই প্রতারণায় ব্যবহৃত হয়।")
                synth.setdefault("risky_domain", _synth(
                    "risky_domain", 30, "Risky website address", "ঝুঁকিপূর্ণ ওয়েবসাইট ঠিকানা",
                    "The link uses a kind of domain that is common in scam messages.",
                    "লিংকটিতে এমন ডোমেইন আছে যা প্রতারণার মেসেজে প্রায়ই দেখা যায়।",
                    LINK_ADVICE_EN, LINK_ADVICE_BN))
            if re.fullmatch(r"[\d.]+", host) or host.startswith("xn--") or ".xn--" in host:
                verdict = "danger"
                reasons_en.append("The address is a raw IP number or a disguised international name.")
                reasons_bn.append("ঠিকানাটি সরাসরি আইপি নম্বর বা ছদ্মবেশী নাম।")
                synth.setdefault("risky_domain", _synth(
                    "risky_domain", 40, "Risky website address", "ঝুঁকিপূর্ণ ওয়েবসাইট ঠিকানা",
                    "The link hides its real owner.", "লিংকটির আসল মালিক লুকানো।", LINK_ADVICE_EN, LINK_ADVICE_BN))
            if verdict == "unknown":
                verdict = "caution"
                reasons_en.append("Unknown website. Be careful before opening it.")
                reasons_bn.append("অপরিচিত ওয়েবসাইট। খোলার আগে সতর্ক থাকুন।")
                synth.setdefault("unknown_link", _synth(
                    "unknown_link", 15, "Contains a link", "লিংক আছে",
                    "The message contains a link to a website we cannot vouch for.",
                    "মেসেজে এমন একটি লিংক আছে যা আমরা নিশ্চিত করতে পারি না।",
                    LINK_ADVICE_EN, LINK_ADVICE_BN))
        entities.append({"kind": "link", "text": raw, "host": host, "verdict": verdict,
                         "reasons_en": reasons_en, "reasons_bn": reasons_bn})
        if verdict in ("danger", "caution"):
            spans.append((start, end, verdict, "lookalike_link" if verdict == "danger" else "short_link"))

    care_context = bool(CARE_RE.search(text))
    for m in HOTLINE_RE.finditer(text):
        name = HOTLINES[m.group(1)]
        entities.append({"kind": "phone", "text": m.group(1), "verdict": "official",
                         "reasons_en": [f"Official {name} hotline."], "reasons_bn": [f"{name}-এর অফিসিয়াল হটলাইন।"]})
    for m in PHONE_RE.finditer(text):
        if care_context:
            entities.append({"kind": "phone", "text": m.group(), "verdict": "caution",
                             "reasons_en": ["A personal mobile number. Provider support never calls or texts from a personal 01… number."],
                             "reasons_bn": ["এটি ব্যক্তিগত মোবাইল নম্বর। প্রতিষ্ঠানের সাপোর্ট কখনো ব্যক্তিগত 01… নম্বর থেকে ফোন বা মেসেজ দেয় না।"]})
            spans.append((m.start(), m.end(), "caution", "personal_number_care"))
            synth.setdefault("personal_number_care", _synth(
                "personal_number_care", 35, "'Support' from a personal number", "ব্যক্তিগত নম্বর থেকে 'সাপোর্ট'",
                "The message mentions a provider or customer care but gives a personal mobile number.",
                "মেসেজে প্রতিষ্ঠান বা কাস্টমার কেয়ারের কথা আছে, কিন্তু একটি ব্যক্তিগত মোবাইল নম্বর দেওয়া হয়েছে।",
                "Call only the official hotline printed on the provider's app or website.",
                "শুধু প্রতিষ্ঠানের অ্যাপ বা ওয়েবসাইটে দেওয়া অফিসিয়াল হটলাইনে ফোন করুন।"))
        else:
            entities.append({"kind": "phone", "text": m.group(), "verdict": "unknown",
                             "reasons_en": ["A mobile number. Check who it belongs to before sending money."],
                             "reasons_bn": ["একটি মোবাইল নম্বর। টাকা পাঠানোর আগে নম্বরটি কার তা যাচাই করুন।"]})
    return entities, list(synth.values()), spans
