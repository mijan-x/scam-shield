"""Scam Trainer scenarios (scripted mode: works offline, deterministic for demos).

Each step has the scammer's message and three replies for the user to choose from.
score: 2 = safe, 1 = partly safe, 0 = risky. All scenarios are our own writing,
based on widely reported scam patterns.
"""


def _c(cid, en, bn, score, fb_en, fb_bn):
    return {"id": cid, "en": en, "bn": bn, "score": score, "fb_en": fb_en, "fb_bn": fb_bn}


SCENARIOS = [
    {
        "id": "refund",
        "title_en": "The wrong-number refund",
        "title_bn": "ভুল নম্বরে টাকা পাঠানোর ফাঁদ",
        "intro_en": "You get an SMS saying Tk 5,000 arrived from an unknown number. A few minutes later your phone rings.",
        "intro_bn": "আপনার ফোনে এসএমএস এল, অচেনা নম্বর থেকে ৫,০০০ টাকা এসেছে। কয়েক মিনিট পরে ফোন বাজল।",
        "red_flags_en": ["Emotional pressure", "Asks you to move money before you have checked", "Asks for your PIN", "Threats"],
        "red_flags_bn": ["আবেগি চাপ", "যাচাই না করেই টাকা পাঠাতে বলা", "পিন চাওয়া", "হুমকি"],
        "safe_en": "Check your own transaction history. If money really arrived, ask the provider's official hotline to reverse it. Never send it back yourself and never share your PIN.",
        "safe_bn": "নিজের অ্যাপে লেনদেন দেখুন। টাকা সত্যিই এসে থাকলে অফিসিয়াল হটলাইনে জানিয়ে ফেরত পাঠান। নিজে ফেরত পাঠাবেন না এবং পিন কখনো দেবেন না।",
        "steps": [
            {
                "scammer_en": "Hello brother, I sent Tk 5,000 to your number by mistake. I'm in big trouble. Please send it back right now.",
                "scammer_bn": "ভাই, ভুল করে আপনার নম্বরে ৫,০০০ টাকা পাঠিয়ে ফেলেছি। খুব বিপদে আছি। এখনই ফেরত পাঠিয়ে দিন প্লিজ।",
                "choices": [
                    _c("a", "Send it back right away to help him.", "সাহায্য করতে এখনই টাকা ফেরত পাঠাই।", 0,
                       "Risky. The SMS may be fake and the money may never have arrived.", "ঝুঁকিপূর্ণ। এসএমএসটি ভুয়া হতে পারে, টাকা হয়তো আসেইনি।"),
                    _c("b", "Check my own bKash app and transaction history first.", "আগে নিজের বিকাশ অ্যাপে লেনদেন দেখি।", 2,
                       "Correct. Always check your own account before anything else.", "ঠিক। আগে সবসময় নিজের অ্যাকাউন্ট দেখুন।"),
                    _c("c", "Tell him I'll think about it.", "বলি, ভেবে দেখছি।", 1,
                       "Not bad, but use the time to check your account.", "খারাপ নয়, তবে এই সময়ে নিজের অ্যাকাউন্ট দেখে নিন।"),
                ],
            },
            {
                "scammer_en": "My father is in hospital, I need it in 5 minutes! Just tell me your PIN and I'll reverse it myself.",
                "scammer_bn": "আমার বাবা হাসপাতালে, ৫ মিনিটের মধ্যে টাকাটা লাগবে! শুধু আপনার পিনটা বলুন, আমি নিজেই ফেরত নিয়ে নেব।",
                "choices": [
                    _c("a", "Give the PIN so he can reverse it.", "পিন দিয়ে দিই, সে ফেরত নিয়ে নিক।", 0,
                       "Dangerous. Anyone with your PIN can empty your account.", "বিপজ্জনক। পিন পেলে যে কেউ আপনার অ্যাকাউন্ট খালি করতে পারে।"),
                    _c("b", "Ask for his name and number so I can call him back.", "তার নাম ও নম্বর চেয়ে পরে কল করি।", 1,
                       "Careful, but the real issue is that he asked for your PIN.", "সতর্ক, তবে আসল সমস্যা হল সে পিন চেয়েছে।"),
                    _c("c", "Refuse: a PIN is never shared. Hang up.", "পিন কখনো কাউকে দেওয়া যায় না। কল কেটে দিই।", 2,
                       "Correct. A real refund never needs your PIN.", "ঠিক। সত্যিকারের ফেরতের জন্য পিন লাগে না।"),
                ],
            },
            {
                "scammer_en": "You are a thief! I'll report you to the police and get your SIM blocked!",
                "scammer_bn": "আপনি চোর! পুলিশে দেব, আপনার সিম ব্লক করাব!",
                "choices": [
                    _c("a", "Panic and send the money to stop the threats.", "ভয় পেয়ে টাকা পাঠিয়ে দিই।", 0,
                       "That is what the threat is for. Scammers rely on panic.", "হুমকির উদ্দেশ্যই এটি। প্রতারকরা ভয়ের ওপর নির্ভর করে।"),
                    _c("b", "Stay calm. If money did arrive, ask the official hotline to reverse it.", "শান্ত থাকি। টাকা এসে থাকলে অফিসিয়াল হটলাইনে জানাই।", 2,
                       "Correct. Official channels handle genuine mistakes.", "ঠিক। প্রকৃত ভুল অফিসিয়াল মাধ্যমেই সমাধান হয়।"),
                    _c("c", "Block the number.", "নম্বরটি ব্লক করে দিই।", 1,
                       "Good, and also check your account and report the number.", "ভালো, সঙ্গে নিজের অ্যাকাউন্ট দেখুন ও নম্বরটি রিপোর্ট করুন।"),
                ],
            },
        ],
    },
    {
        "id": "care",
        "title_en": "The fake customer-care call",
        "title_bn": "ভুয়া কাস্টমার কেয়ারের ফোন",
        "intro_en": "A caller says he is from bKash customer care.",
        "intro_bn": "একজন ফোন করে বলছে সে বিকাশ কাস্টমার কেয়ার থেকে বলছে।",
        "red_flags_en": ["Threat to block your account", "KYC by phone", "Asks for a code", "Asks you to install a remote-access app"],
        "red_flags_bn": ["অ্যাকাউন্ট ব্লকের হুমকি", "ফোনে কেওয়াইসি", "কোড চাওয়া", "রিমোট অ্যাক্সেস অ্যাপ ইনস্টল করতে বলা"],
        "safe_en": "Hang up. Open the official app or call the hotline yourself. No provider asks for your PIN or OTP, or asks you to install a screen-sharing app.",
        "safe_bn": "কল কেটে দিন। নিজে অফিসিয়াল অ্যাপ খুলুন বা হটলাইনে ফোন করুন। কোনো প্রতিষ্ঠান পিন, ওটিপি বা স্ক্রিন শেয়ারের অ্যাপ চায় না।",
        "steps": [
            {
                "scammer_en": "Sir, your bKash account will be blocked today because your KYC is incomplete. I will help you update it now.",
                "scammer_bn": "স্যার, আপনার কেওয়াইসি অসম্পূর্ণ থাকায় আজই আপনার বিকাশ অ্যাকাউন্ট ব্লক হয়ে যাবে। আমি এখনই আপডেট করে দিচ্ছি।",
                "choices": [
                    _c("a", "Okay, tell me what to do.", "ঠিক আছে, কী করতে হবে বলুন।", 0,
                       "Risky. You are following a stranger's instructions.", "ঝুঁকিপূর্ণ। আপনি অচেনা লোকের নির্দেশ মানছেন।"),
                    _c("b", "Hang up and call the official hotline myself.", "কল কেটে নিজে অফিসিয়াল হটলাইনে ফোন করি।", 2,
                       "Correct. Always call back on the official number you find yourself.", "ঠিক। সবসময় নিজে খুঁজে পাওয়া অফিসিয়াল নম্বরে ফোন করুন।"),
                    _c("c", "Ask for his employee ID.", "তার কর্মচারী আইডি চাই।", 1,
                       "He can invent one. Verify through the official channel instead.", "সে একটা বানিয়ে বলতে পারে। অফিসিয়াল মাধ্যমে যাচাই করুন।"),
                ],
            },
            {
                "scammer_en": "To verify you, please read me the 6-digit code that was just sent to your phone.",
                "scammer_bn": "আপনাকে যাচাই করতে এইমাত্র আপনার ফোনে যে ৬ সংখ্যার কোড গেছে সেটা পড়ে শোনান।",
                "choices": [
                    _c("a", "Read out the code.", "কোডটা পড়ে শোনাই।", 0,
                       "Dangerous. That code lets him into your account.", "বিপজ্জনক। ওই কোড দিয়ে সে আপনার অ্যাকাউন্টে ঢুকে যাবে।"),
                    _c("b", "Say: no bKash staff ever asks for this code. End the call.", "বলি, বিকাশের কেউ এই কোড চায় না। কল কেটে দিই।", 2,
                       "Correct.", "ঠিক।"),
                    _c("c", "Ask him to send an email instead.", "বলি ইমেইলে পাঠাতে।", 1,
                       "Fine, but the request itself is the warning sign.", "ঠিক আছে, তবে অনুরোধটাই সতর্কসংকেত।"),
                ],
            },
            {
                "scammer_en": "Then install the QuickSupport app so I can fix your account from my side.",
                "scammer_bn": "তাহলে QuickSupport অ্যাপটা ইনস্টল করুন, আমি আমার দিক থেকে ঠিক করে দিচ্ছি।",
                "choices": [
                    _c("a", "Install it.", "ইনস্টল করে দিই।", 0,
                       "Dangerous. He could then see your screen and your PIN.", "বিপজ্জনক। এতে সে আপনার স্ক্রিন ও পিন দেখতে পাবে।"),
                    _c("b", "Refuse and end the call.", "রাজি না হয়ে কল কেটে দিই।", 2,
                       "Correct.", "ঠিক।"),
                    _c("c", "Say I'll visit a bKash point instead.", "বলি, আমি বিকাশ পয়েন্টে গিয়ে দেখব।", 1,
                       "Reasonable. Better still: end the call right away.", "যুক্তিসঙ্গত। আরও ভালো হত সঙ্গে সঙ্গে কল কেটে দেওয়া।"),
                ],
            },
        ],
    },
    {
        "id": "proof",
        "title_en": "The buyer with a screenshot",
        "title_bn": "স্ক্রিনশট দেখানো ক্রেতা",
        "intro_en": "You sell clothes on Facebook. A buyer says he has paid.",
        "intro_bn": "আপনি ফেসবুকে কাপড় বিক্রি করেন। একজন ক্রেতা বলছে সে টাকা পাঠিয়ে দিয়েছে।",
        "red_flags_en": ["A screenshot instead of a confirmed payment", "Pressure to ship today", "'Regular customer' pressure", "Threat of a bad review"],
        "red_flags_bn": ["নিশ্চিত পেমেন্টের বদলে স্ক্রিনশট", "আজই পাঠানোর চাপ", "'নিয়মিত ক্রেতা' বলে চাপ", "খারাপ রিভিউয়ের হুমকি"],
        "safe_en": "Ship only after the money shows in your own app or you get the provider's SMS. Offer cash on delivery as a safe alternative.",
        "safe_bn": "নিজের অ্যাপে টাকা দেখলে বা প্রতিষ্ঠানের এসএমএস পেলে তবেই পণ্য পাঠান। বিকল্প হিসেবে ক্যাশ অন ডেলিভারি দিন।",
        "steps": [
            {
                "scammer_en": "Brother I sent Tk 3,500 by bKash, here is the screenshot. Please send the parcel today, it's urgent.",
                "scammer_bn": "ভাই ৩,৫০০ টাকা বিকাশে পাঠিয়েছি, স্ক্রিনশট দিলাম। আজই পার্সেল পাঠিয়ে দিন, খুব জরুরি।",
                "choices": [
                    _c("a", "It looks fine, ship it.", "ঠিকই দেখাচ্ছে, পাঠিয়ে দিই।", 0,
                       "Risky. Screenshots can be edited.", "ঝুঁকিপূর্ণ। স্ক্রিনশট এডিট করা যায়।"),
                    _c("b", "Check my own bKash app for the money first.", "আগে নিজের বিকাশ অ্যাপে টাকা এসেছে কিনা দেখি।", 2,
                       "Correct. Your own account is the only proof.", "ঠিক। আপনার নিজের অ্যাকাউন্টই একমাত্র প্রমাণ।"),
                    _c("c", "Compare the amount and TrxID with the screenshot.", "স্ক্রিনশটের টাকা ও ট্রানজ্যাকশন আইডি মিলিয়ে দেখি।", 1,
                       "Useful, but a good fake can match. Check your own account too.", "কাজের, কিন্তু ভালো নকল মিলেও যেতে পারে। নিজের অ্যাকাউন্টও দেখুন।"),
                ],
            },
            {
                "scammer_en": "The money may take time to show, there's a network problem. Just ship it, I'm a regular customer.",
                "scammer_bn": "নেটওয়ার্কের সমস্যায় টাকা দেখাতে দেরি হতে পারে। আপনি পাঠিয়ে দিন, আমি তো নিয়মিত ক্রেতা।",
                "choices": [
                    _c("a", "Ship it to keep him happy.", "ক্রেতাকে খুশি রাখতে পাঠিয়ে দিই।", 0,
                       "Risky. A real payment arrives within moments.", "ঝুঁকিপূর্ণ। প্রকৃত পেমেন্ট কয়েক মুহূর্তেই আসে।"),
                    _c("b", "Wait until the money or the provider's SMS appears.", "টাকা বা প্রতিষ্ঠানের এসএমএস না আসা পর্যন্ত অপেক্ষা করি।", 2,
                       "Correct.", "ঠিক।"),
                    _c("c", "Ask him to send the payment again.", "আবার পেমেন্ট করতে বলি।", 1,
                       "Cautious, but you may end up double-paid. Check first.", "সতর্ক, তবে দুইবার টাকা আসতে পারে। আগে যাচাই করুন।"),
                ],
            },
            {
                "scammer_en": "I'll leave a bad review if you don't send the tracking number right now.",
                "scammer_bn": "এখনই ট্র্যাকিং নম্বর না দিলে আমি খারাপ রিভিউ দেব।",
                "choices": [
                    _c("a", "Give the tracking number to avoid the review.", "রিভিউয়ের ভয়ে ট্র্যাকিং নম্বর দিয়ে দিই।", 0,
                       "That is the pressure working.", "এটাই চাপের কাজ।"),
                    _c("b", "Politely hold firm: no confirmed payment, no shipping.", "বিনয়ের সঙ্গে বলি, নিশ্চিত পেমেন্ট ছাড়া পাঠানো যাবে না।", 2,
                       "Correct.", "ঠিক।"),
                    _c("c", "Offer cash on delivery instead.", "বিকল্পে ক্যাশ অন ডেলিভারি দিই।", 2,
                       "Also correct. A genuine buyer accepts this.", "এটিও ঠিক। প্রকৃত ক্রেতা এতে রাজি হবে।"),
                ],
            },
        ],
    },
]

BY_ID = {s["id"]: s for s in SCENARIOS}

PERSONA = {
    "refund": "someone who claims to have sent money to the player's mobile-money account by mistake and wants it back",
    "care": "a fake mobile-money customer-care agent who threatens to block the player's account",
    "proof": "a buyer who claims to have paid for goods and shows a screenshot, pressing the player to ship quickly",
}
