"""'How sure is this?': an honest note on what a verdict rests on.

It never changes a verdict or a score. It says whether the result rests on a known scam pattern we can
point to, only on the AI's opinion, only on how a picture looks, or on nothing at all; and for a
message that matched nothing it says plainly that 'nothing found' is not 'safe'.
"""
from .library import PATTERNS

CHECKLIST = [
    {"en": "Does it ask for a PIN, OTP, password or a code that was sent to you?",
     "bn": "পিন, ওটিপি, পাসওয়ার্ড বা আপনার কাছে আসা কোনো কোড চাইছে কি?"},
    {"en": "Does it ask you to send money first, or pay a fee to receive money or a prize?",
     "bn": "আগে টাকা পাঠাতে বা টাকা/পুরস্কার পেতে ফি দিতে বলছে কি?"},
    {"en": "Does it rush or scare you (account blocked, last chance, police)?",
     "bn": "তাড়া দিচ্ছে বা ভয় দেখাচ্ছে কি (অ্যাকাউন্ট বন্ধ, শেষ সুযোগ, পুলিশ)?"},
    {"en": "Does it have a link, or ask you to install an app?",
     "bn": "কোনো লিংক আছে কি, বা অ্যাপ ইনস্টল করতে বলছে কি?"},
    {"en": "Does someone claim to be bKash, Nagad, a bank or an officer from an ordinary number?",
     "bn": "সাধারণ নম্বর থেকে কেউ নিজেকে বিকাশ, নগদ, ব্যাংক বা কর্মকর্তা বলছে কি?"},
]
CHECK_TAIL = {"en": "If any answer is yes, stop and call the official hotline yourself.",
              "bn": "যেকোনো উত্তর 'হ্যাঁ' হলে থামুন এবং নিজে অফিসিয়াল হটলাইনে ফোন করুন।"}

VERIFY_EN = ("The only real proof is your own account: open your bKash/Nagad/Rocket app, go to the statement or "
             "transaction list, and find this amount and transaction ID. If it is not there, the money has not "
             "arrived, whatever the screenshot shows.")
VERIFY_BN = ("আসল প্রমাণ শুধু আপনার নিজের অ্যাকাউন্ট: বিকাশ/নগদ/রকেট অ্যাপ খুলে স্টেটমেন্ট বা লেনদেনের তালিকায় এই "
             "টাকা ও লেনদেন আইডি খুঁজুন। সেখানে না থাকলে টাকা আসেনি, স্ক্রিনশটে যা-ই দেখাক।")

# proof checks about how the picture looks, not about the payment details
LOOK_CHECKS = {"visual", "meta_editor", "meta_crop", "meta_size", "status_bar"}


def _n(k: int, bn: bool = False) -> str:
    s = str(k)
    return s.translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")) if bn else s


def for_message(rule_signs: int, base_risk: str, final_risk: str, ai_ran: bool) -> dict:
    """rule_signs: warning signs found by our rules (before the AI). base_risk: the rules' risk."""
    rank = {"low": 0, "medium": 1, "high": 2}
    raised = rank.get(final_risk, 0) > rank.get(base_risk, 0)
    total = len(PATTERNS)
    if rule_signs:
        out = {"level": "known_pattern",
               "title_en": "Based on warning signs we can show you",
               "title_bn": "যে সংকেত দেখাতে পারি তার ভিত্তিতে",
               "en": f"This result rests on {rule_signs} known warning sign{'s' if rule_signs > 1 else ''}, listed under Why.",
               "bn": f"এই ফলাফল {_n(rule_signs, True)}টি পরিচিত সতর্ক সংকেতের ভিত্তিতে, 'কেন' অংশে দেখানো হয়েছে।"}
        if raised:
            out["en"] += " The AI rated it higher than our rules did."
            out["bn"] += " আমাদের নিয়মের চেয়ে এআই এটিকে বেশি ঝুঁকিপূর্ণ বলেছে।"
        return out
    if raised:
        return {"level": "ai_only",
                "title_en": "AI opinion only: no known pattern matched",
                "title_bn": "শুধু এআই-এর মত: কোনো পরিচিত ধরন মেলেনি",
                "en": f"None of our {total} known scam patterns matched. The AI thinks this looks like a scam. It may be a "
                      "new trick, or the AI may be wrong, so treat this as a warning, not as proof.",
                "bn": f"আমাদের {_n(total, True)}টি পরিচিত প্রতারণার ধরনের কোনোটি মেলেনি। এআই মনে করছে এটি প্রতারণার মতো। এটি "
                      "নতুন কৌশল হতে পারে, আবার এআই ভুলও হতে পারে; তাই এটিকে সতর্কতা হিসেবে নিন, প্রমাণ হিসেবে নয়।",
                "checklist": CHECKLIST, "tail": CHECK_TAIL}
    if ai_ran:
        return {"level": "unknown",
                "title_en": "Not recognised. That does not mean safe.",
                "title_bn": "চেনা যায়নি। এর মানে নিরাপদ নয়।",
                "en": f"Neither our {total} known scam patterns nor the AI found a warning sign. Scammers write new "
                      "messages every week, so 'nothing found' is not proof that this is safe. Check it yourself:",
                "bn": f"আমাদের {_n(total, True)}টি পরিচিত ধরন বা এআই কোনো সতর্ক সংকেত পায়নি। প্রতারকেরা প্রতি সপ্তাহে নতুন "
                      "মেসেজ লেখে, তাই 'কিছু পাওয়া যায়নি' মানে নিরাপদ নয়। নিজে যাচাই করুন:",
                "checklist": CHECKLIST, "tail": CHECK_TAIL}
    return {"level": "unknown_rules_only",
            "title_en": "Only known patterns were checked",
            "title_bn": "শুধু পরিচিত ধরন যাচাই হয়েছে",
            "en": f"We compared this with our {total} known scam patterns and found none. The AI check did not run, so a "
                  "new kind of scam would not be caught. Check it yourself:",
            "bn": f"আমাদের {_n(total, True)}টি পরিচিত প্রতারণার ধরনের সাথে মিলিয়ে কিছু পাওয়া যায়নি। এআই যাচাই চলেনি, তাই "
                  "নতুন ধরনের প্রতারণা ধরা পড়বে না। নিজে যাচাই করুন:",
            "checklist": CHECKLIST, "tail": CHECK_TAIL}


def for_number() -> dict:
    return {"level": "number_only",
            "title_en": "Judged from the number only",
            "title_bn": "শুধু নম্বর দেখে বিচার",
            "en": "We can tell whether a number is official, foreign or impossible, but not who owns an ordinary number. "
                  "A normal-looking number can still belong to a scammer: judge the call by what they ask for.",
            "bn": "নম্বরটি অফিসিয়াল, বিদেশি নাকি অসম্ভব তা বলা যায়, কিন্তু সাধারণ নম্বরের মালিক কে তা নয়। স্বাভাবিক "
                  "দেখতে নম্বরও প্রতারকের হতে পারে: তারা কী চায় তা দেখে বিচার করুন।",
            "checklist": CHECKLIST, "tail": CHECK_TAIL}


def for_proof(res: dict) -> dict:
    checks = res.get("checks", [])
    bad = [c for c in checks if c["status"] in ("fail", "warn")]
    look = [c for c in bad if c["id"] in LOOK_CHECKS]
    facts = [c for c in bad if c["id"] not in LOOK_CHECKS]
    fact_fails = [c for c in facts if c["status"] == "fail"]
    base = {"verify_en": VERIFY_EN, "verify_bn": VERIFY_BN}
    if res.get("verdict") == "consistent":
        if res.get("compared"):
            return {**base, "level": "no_red_flags",
                    "title_en": "Nothing contradicts it, but that is not proof",
                    "title_bn": "কিছুই অমিল নয়, তবে এটি প্রমাণ নয়",
                    "en": "Every detail we could check lines up. A careful fake can still match every detail, so this "
                          "screenshot alone cannot prove the money arrived.",
                    "bn": "যা যাচাই করা গেছে সব মিলেছে। তবে যত্ন করে বানানো নকলও সব মেলাতে পারে, তাই শুধু এই স্ক্রিনশট "
                          "টাকা আসার প্রমাণ নয়।"}
        return {**base, "level": "self_only",
                "title_en": "Checked against itself only",
                "title_bn": "শুধু নিজের সাথে মিলিয়ে দেখা",
                "en": "With nothing to compare (amount, numbers), we could only look for signs inside the picture. "
                      "Finding none does not mean the payment is real.",
                "bn": "মেলানোর মতো তথ্য (টাকা, নম্বর) না থাকায় শুধু ছবির ভেতরের সংকেত দেখা গেছে। কিছু না পাওয়া মানে "
                      "পেমেন্ট আসল নয়।"}
    if not facts and look:
        return {**base, "level": "looks_only",
                "title_en": "Only the picture looks edited; the details match",
                "title_bn": "শুধু ছবিটি এডিট করা মনে হচ্ছে; তথ্য মিলেছে",
                "en": "None of the payment details contradict what you expected. The doubts come only from how the "
                      "image looks (editing app, cropping, uneven digits). Real screenshots are often cropped, marked "
                      "up or re-saved by WhatsApp or Messenger, so this may be a genuine payment. The picture alone "
                      "cannot settle it.",
                "bn": "পেমেন্টের কোনো তথ্য আপনার প্রত্যাশার সাথে অমিল নয়। সন্দেহ শুধু ছবির চেহারা থেকে (এডিটিং অ্যাপ, "
                      "কাটা, অসমান সংখ্যা)। আসল স্ক্রিনশটও প্রায়ই কাটা, দাগানো বা হোয়াটসঅ্যাপ/মেসেঞ্জারে আবার সেভ হয়, "
                      "তাই এটি আসল পেমেন্টও হতে পারে। শুধু ছবি দেখে নিশ্চিত হওয়া যায় না।"}
    if fact_fails:
        return {**base, "level": "facts_contradict",
                "title_en": "Hard facts do not match",
                "title_bn": "মূল তথ্য মেলেনি",
                "en": f"{len(fact_fails)} payment detail{'s' if len(fact_fails) > 1 else ''} (amount, numbers, time or "
                      "transaction ID) contradict what a real payment would show. This rests on facts, not only on "
                      "how the picture looks.",
                "bn": f"পেমেন্টের {_n(len(fact_fails), True)}টি তথ্য (টাকা, নম্বর, সময় বা লেনদেন আইডি) আসল পেমেন্টের "
                      "সাথে মেলে না। এটি ছবির চেহারা নয়, তথ্যের ভিত্তিতে।"}
    extra_en = (" The editing signs alone do not prove a fake: real screenshots are often cropped or re-saved."
                if look else "")
    extra_bn = (" শুধু এডিটের চিহ্ন নকলের প্রমাণ নয়: আসল স্ক্রিনশটও প্রায়ই কাটা বা আবার সেভ হয়।" if look else "")
    return {**base, "level": "details_unclear",
            "title_en": "Some details do not line up",
            "title_bn": "কিছু তথ্য পুরোপুরি মেলেনি",
            "en": "Some details are off, but each could have an innocent reason (a late payment, a family member's "
                  "number). We cannot tell which from the screenshot." + extra_en,
            "bn": "কিছু তথ্য মেলেনি, তবে প্রতিটির নির্দোষ কারণও থাকতে পারে (দেরিতে পেমেন্ট, পরিবারের কারো নম্বর)। "
                  "স্ক্রিনশট দেখে কোনটি তা বলা যায় না।" + extra_bn}
