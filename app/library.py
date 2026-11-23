"""Scam-pattern library.

Each pattern matches when EVERY group has at least one regex hit (AND of ORs).
A pattern is skipped when any `unless` regex hits (for example "do not share your OTP"
in a genuine provider SMS). Texts are matched lower-cased; Bangla, English and
Banglish (Bangla typed in Latin letters) forms are included.

This library is our own work, written from public scam warnings. Extend it: every
pattern you add improves the Pre-transaction Check and the Scam Trainer together.
"""

SECRET = (
    r"(?<![a-z])(otp|pin|cvv|password|passcode)(?![a-z])|পিন|ওটিপি|পাসওয়ার্ড|"
    r"verification code|secret code|ভেরিফিকেশন কোড|গোপন কোড|confirmation code|"
    r"(?:sms|message|mobile|phone|মেসেজ|মোবাইলে|ফোনে)\s*(?:e|এ)?\s*(?:asha|asa|আসা|আসবে)\s*(?:code|কোড)|"
    r"code\s*(?:ta|ti|টা|টি)?\s*(?:ashbe|asbe|ashle|ashlo|eseche|jabe|pathano hobe)|কোডটি|কোডটা|কোড টি|কোড টা|"
    r"code (?:we|i) (?:just )?sent|the code (?:you )?(?:got|received)"
)
ASK = (
    r"(?<![a-z])(tell|give|share|send|provide|enter|say|read|bolun|bolo|bolen|den|dien|dao|dile|dite|"
    r"janan|janaan|pathan|pathao|pathiye|likhun|dinn|bolben|boliyen|janaben|diben|verify)(?![a-z])|"
    r"বলুন|বলেন|বলো|বলবেন|দিন|দেন|দিয়ে|দাও|দেবেন|জানান|জানাবেন|শেয়ার|পাঠান|পাঠাও|পাঠিয়ে|লিখুন|পড়ে শোনান"
)
# phrases that turn the message into a warning rather than a request
WARNING = (
    r"do not share|don't share|dont share|never share|do not disclose|never ask|never asks|"
    r"share korben na|share korben nah|kawke bolben na|kauke bolben na|keu chay na|"
    r"কাউকে বলবেন না|শেয়ার করবেন না|কাউকে দেবেন না|কখনো চায় না|কেউ চায় না|কাউকে জানাবেন না"
)

PATTERNS = [
    {
        "id": "otp_pin_request",
        "name_en": "Request for PIN or OTP",
        "name_bn": "পিন বা ওটিপি চাওয়া",
        "weight": 90,
        "groups": [[SECRET], [ASK]],
        "unless": [WARNING],
        "why_en": "Someone is asking you to give or read out a PIN, OTP or code. No real provider ever asks for it.",
        "why_bn": "কেউ আপনার কাছে পিন, ওটিপি বা কোড চাইছে। কোনো প্রকৃত প্রতিষ্ঠান এটি কখনো চায় না।",
        "advice_en": "Never tell anyone your PIN or OTP, even someone claiming to be customer care. End the call and ring the official hotline yourself.",
        "advice_bn": "আপনার পিন বা ওটিপি কাউকে কখনো বলবেন না, নিজেকে কাস্টমার কেয়ার দাবি করলেও না। কল কেটে দিন এবং নিজে অফিসিয়াল হটলাইনে ফোন করুন।",
    },
    {
        "id": "wrong_number_refund",
        "name_en": "Wrong-number refund trick",
        "name_bn": "ভুল নম্বরে টাকা পাঠানোর প্রতারণা",
        "weight": 70,
        "groups": [
            [r"vul kore|bhul kore|ভুল করে|ভুলে|by mistake|mistakenly|accidentally|wrong number|vul number|ভুল নম্বর|ভুল নাম্বার|chole gese|চলে গেছে|চলে গেছে"],
            [r"ferot|ফেরত|refund|return|send back|back kore|ফিরিয়ে|firiye|pathiye din|পাঠিয়ে দিন|pathan|send it back|kindly send"],
        ],
        "unless": [WARNING],
        "why_en": "The sender says money was sent to you by mistake and asks you to return it. This is a known trick.",
        "why_bn": "প্রেরক বলছেন ভুল করে টাকা পাঠিয়েছেন এবং ফেরত চাইছেন। এটি একটি পরিচিত প্রতারণা।",
        "advice_en": "Check your own transaction history first. If nothing arrived, there is nothing to refund. If money did arrive, do not send it back yourself; ask the provider's official hotline to reverse it.",
        "advice_bn": "আগে নিজের অ্যাপে লেনদেনের হিসাব দেখুন। টাকা না এসে থাকলে ফেরত দেওয়ার কিছু নেই। টাকা এসে থাকলে নিজে ফেরত না পাঠিয়ে অফিসিয়াল হটলাইনে জানান।",
    },
    {
        "id": "prize_lottery",
        "name_en": "Prize or lucky-draw scam",
        "name_bn": "পুরস্কার বা লটারির প্রতারণা",
        "weight": 70,
        "groups": [
            [r"prize|lottery|lucky draw|lucky winner|you have won|you won|jitechen|jitesen|জিতেছেন|জিতেছো|পুরস্কার|লটারি|লাকি ড্র|উপহার জিতে|inam|ইনাম"],
            [r"claim|click|link|fee|charge|bkash|nagad|taka|tk|টাকা|ক্লিক|লিংক|লিঙ্ক|dite hobe|দিতে হবে|পাঠান|send|call|কল"],
        ],
        "unless": [],
        "why_en": "You are told you have won a prize and must act (pay, click or call) to claim it.",
        "why_bn": "বলা হচ্ছে আপনি পুরস্কার জিতেছেন এবং তা পেতে কিছু করতে হবে (টাকা দেওয়া, ক্লিক বা কল)।",
        "advice_en": "Real prizes never ask you to pay a fee or click a link first. Ignore the message and do not open the link.",
        "advice_bn": "সত্যিকারের পুরস্কারের জন্য আগে টাকা দিতে বা লিংকে ক্লিক করতে হয় না। বার্তাটি উপেক্ষা করুন এবং লিংক খুলবেন না।",
    },
    {
        "id": "fake_care_kyc",
        "name_en": "Fake customer care or KYC threat",
        "name_bn": "ভুয়া কাস্টমার কেয়ার বা কেওয়াইসি হুমকি",
        "weight": 65,
        "groups": [
            [r"kyc|কেওয়াইসি|verify|ভেরিফাই|যাচাই|update|আপডেট|suspend|block|ব্লক|বন্ধ|closed|will be close|deactivat|bondho|incomplete|অসম্পূর্ণ"],
            [r"bkash|nagad|rocket|upay|bank|বিকাশ|নগদ|রকেট|ব্যাংক|ব্যাঙ্ক|account|একাউন্ট|অ্যাকাউন্ট|অ্যাকাউন্ট|sim|সিম|customer care|কাস্টমার কেয়ার"],
            [r"call|ring|number|link|click|otp|pin|hotline|হটলাইন|within|ghonta|ঘণ্টা|ঘন্টা|today|aj |আজ|immediately|এখনই|akhoni|now|কল|ক্লিক|লিংক|লিঙ্ক|নম্বরে"],
        ],
        "unless": [WARNING],
        "why_en": "The message threatens to block or close your account unless you update details through a call or link.",
        "why_bn": "বার্তায় ফোন বা লিংকের মাধ্যমে তথ্য আপডেট না করলে অ্যাকাউন্ট বন্ধ করার হুমকি দেওয়া হচ্ছে।",
        "advice_en": "Providers do not close accounts over a call or SMS. Do not follow the link or call back; open the official app or ring the hotline yourself.",
        "advice_bn": "ফোন বা এসএমএসে অ্যাকাউন্ট বন্ধ করার হুমকি দেওয়া হয় না। লিংকে ক্লিক বা ফিরতি কল করবেন না; নিজে অফিসিয়াল অ্যাপ খুলুন বা হটলাইনে ফোন করুন।",
    },
    {
        "id": "job_fee",
        "name_en": "Job offer that asks for a fee",
        "name_bn": "টাকা চাওয়া চাকরির প্রস্তাব",
        "weight": 65,
        "groups": [
            [r"job|চাকরি|চাকুরি|chakri|recruit|selected|নিয়োগ|part.?time|work from home|home based|ঘরে বসে"],
            [r"fee|registration|deposit|advance|joma|জমা|ফি|রেজিস্ট্রেশন|অগ্রিম|taka|টাকা|send|পাঠান"],
        ],
        "unless": [],
        "why_en": "A job offer asks you to pay a fee or deposit first.",
        "why_bn": "একটি চাকরির প্রস্তাবে আগে ফি বা জমা দিতে বলা হচ্ছে।",
        "advice_en": "Real employers do not charge to hire you. Do not pay; verify the company independently.",
        "advice_bn": "সত্যিকারের নিয়োগকর্তা চাকরি দিতে টাকা চায় না। টাকা পাঠাবেন না; প্রতিষ্ঠানটি আলাদাভাবে যাচাই করুন।",
    },
    {
        "id": "parcel_fee",
        "name_en": "Parcel or customs fee demand",
        "name_bn": "পার্সেল বা কাস্টম ফি চাওয়া",
        "weight": 65,
        "groups": [
            [r"parcel|package|courier|custom|কাস্টম|পার্সেল|কুরিয়ার"],
            [r"atke|atkie|held|seized|আটক|release|ছাড়|clearance|ছাড়পত্র"],
            [r"joma|জমা|pay|fee|ফি|taka|tk|টাকা|pathan|পাঠান"],
        ],
        "unless": [WARNING],
        "why_en": "A parcel is said to be held and you must pay first to release it. Couriers and customs do not collect fees through personal mobile money.",
        "why_bn": "বলা হচ্ছে পার্সেল আটকে আছে, ছাড়াতে আগে টাকা দিতে হবে। কুরিয়ার বা কাস্টম ব্যক্তিগত মোবাইল ব্যাংকিংয়ে ফি নেয় না।",
        "advice_en": "Do not pay. Contact the courier through its official app or website, and check whether you ordered anything.",
        "advice_bn": "টাকা পাঠাবেন না। কুরিয়ারের অফিসিয়াল অ্যাপ বা ওয়েবসাইটে যোগাযোগ করুন এবং আপনি কিছু অর্ডার করেছেন কি না দেখুন।",
    },
    {
        "id": "investment_doubling",
        "name_en": "Guaranteed returns or money doubling",
        "name_bn": "নিশ্চিত লাভ বা টাকা দ্বিগুণ",
        "weight": 65,
        "groups": [
            [r"double|দ্বিগুণ|dugun|invest|বিনিয়োগ|profit|লাভ|guaranteed|নিশ্চিত"],
            [r"daily|prottek din|প্রতিদিন|per day|weekly|সাপ্তাহিক|2x|3x|bkash|nagad|taka|টাকা|বিকাশ|নগদ"],
        ],
        "unless": [WARNING],
        "why_en": "It promises guaranteed profit or doubled money.",
        "why_bn": "এখানে নিশ্চিত লাভ বা টাকা দ্বিগুণ করার প্রতিশ্রুতি দেওয়া হচ্ছে।",
        "advice_en": "Guaranteed daily returns are a classic scam. Do not send money.",
        "advice_bn": "প্রতিদিন নিশ্চিত লাভের প্রতিশ্রুতি একটি পরিচিত প্রতারণা। টাকা পাঠাবেন না।",
    },
    {
        "id": "remote_access_app",
        "name_en": "Remote-access app request",
        "name_bn": "রিমোট অ্যাক্সেস অ্যাপের অনুরোধ",
        "weight": 85,
        "groups": [[r"anydesk|any desk|teamviewer|team viewer|quicksupport|quick support|rustdesk|screen share|স্ক্রিন শেয়ার|এনিডেস্ক|টিমভিউয়ার"]],
        "unless": [WARNING],
        "why_en": "You are asked to install a screen-sharing app. This lets the caller see your PIN and move your money.",
        "why_bn": "আপনাকে স্ক্রিন শেয়ারের অ্যাপ ইনস্টল করতে বলা হচ্ছে। এতে প্রতারক আপনার পিন দেখে টাকা সরাতে পারে।",
        "advice_en": "Never install AnyDesk, TeamViewer or similar at a caller's request.",
        "advice_bn": "কারও কথায় AnyDesk, TeamViewer বা এমন অ্যাপ ইনস্টল করবেন না।",
    },
    {
        "id": "pay_to_receive",
        "name_en": "Fee demanded before you receive money",
        "name_bn": "টাকা পাওয়ার আগে ফি চাওয়া",
        "weight": 70,
        "groups": [
            [r"to receive|pete hole|পেতে হলে|পাওয়ার জন্য|processing fee|clearance|tax|কর |ট্যাক্স|release fee|loan|ঋণ|লোন"],
            [r"send|pathan|pay|জমা|joma|পাঠান|দিতে হবে|dite hobe|আগে|first|advance|অগ্রিম"],
        ],
        "unless": [WARNING],
        "why_en": "You must pay first to receive a loan, parcel or money.",
        "why_bn": "ঋণ, পার্সেল বা টাকা পেতে আপনাকে আগে টাকা দিতে বলা হচ্ছে।",
        "advice_en": "Being asked to pay before you receive something is a red flag. Stop and verify through the official channel.",
        "advice_bn": "কিছু পাওয়ার আগে টাকা দিতে বলা একটি সতর্কসংকেত। থামুন এবং অফিসিয়াল মাধ্যমে যাচাই করুন।",
    },
    {
        "id": "govt_allowance",
        "name_en": "Fake government allowance or stipend",
        "name_bn": "ভুয়া সরকারি ভাতা বা উপবৃত্তি",
        "weight": 65,
        "groups": [
            [r"bhata|ভাতা|allowance|stipend|upobritti|উপবৃত্তি|sorkari|সরকারি|government|govt|প্রণোদনা|relief|ত্রাণ"],
            [SECRET + r"|fee|ফি|charge|চার্জ|joma|জমা|taka pathan|টাকা পাঠান|code|কোড"],
        ],
        "unless": [WARNING],
        "why_en": "Someone says you will get a government allowance or stipend, but first wants a code, PIN or fee.",
        "why_bn": "বলা হচ্ছে আপনি সরকারি ভাতা বা উপবৃত্তি পাবেন, কিন্তু আগে কোড, পিন বা ফি চাওয়া হচ্ছে।",
        "advice_en": "Government payments never need your PIN, OTP or a fee. Check with your school or the local office in person.",
        "advice_bn": "সরকারি টাকা পেতে কখনো পিন, ওটিপি বা ফি লাগে না। স্কুল বা স্থানীয় অফিসে সরাসরি যাচাই করুন।",
    },
    {
        "id": "emergency_relative",
        "name_en": "Emergency money request",
        "name_bn": "জরুরি বিপদের কথা বলে টাকা চাওয়া",
        "weight": 50,
        "groups": [
            [r"accident|এক্সিডেন্ট|দুর্ঘটনা|hospital|হাসপাতাল|haspatal|arrest|গ্রেফতার|police|পুলিশ|thana|থানা|"
             r"bipode|বিপদে|emergency|ইমার্জেন্সি|notun number|নতুন নম্বর|new number|phone hariye|ফোন হারিয়ে"],
            [r"taka|টাকা|tk|send|pathao|pathan|পাঠাও|পাঠান|bkash|nagad|বিকাশ|নগদ|lagbe|লাগবে"],
        ],
        "unless": [WARNING],
        "why_en": "A message claims an emergency or a 'new number' and asks for money quickly.",
        "why_bn": "বিপদ বা 'নতুন নম্বর'-এর কথা বলে তাড়াতাড়ি টাকা চাওয়া হচ্ছে।",
        "advice_en": "Call the person on the number you already know before sending anything.",
        "advice_bn": "কিছু পাঠানোর আগে মানুষটির আগের চেনা নম্বরে ফোন করে নিশ্চিত হোন।",
    },
    {
        "id": "cashback_offer",
        "name_en": "Too-good cashback or bonus offer",
        "name_bn": "অবিশ্বাস্য ক্যাশব্যাক বা বোনাস অফার",
        "weight": 45,
        "groups": [
            [r"cashback|cash back|ক্যাশব্যাক|bonus|বোনাস|free taka|ফ্রি টাকা|gift|গিফট|offer|অফার|reward|রিওয়ার্ড"],
            [r"click|ক্লিক|link|লিংক|লিঙ্ক|claim|ক্লেইম|code|কোড|" + SECRET],
        ],
        "unless": [WARNING],
        "why_en": "An offer of free money or cashback asks you to click a link or share a code.",
        "why_bn": "ফ্রি টাকা বা ক্যাশব্যাকের অফারে লিংকে ক্লিক বা কোড দিতে বলা হচ্ছে।",
        "advice_en": "Real offers appear inside the official app. Do not click links or share codes.",
        "advice_bn": "সত্যিকারের অফার অফিসিয়াল অ্যাপের ভেতরেই দেখা যায়। লিংকে ক্লিক বা কোড শেয়ার করবেন না।",
    },
    {
        "id": "authority_threat",
        "name_en": "Fake authority or operator threat",
        "name_bn": "ভুয়া কর্তৃপক্ষ বা অপারেটরের হুমকি",
        "weight": 65,
        "groups": [
            [r"btrc|বিটিআরসি|police|পুলিশ|থানা|(?<![a-z])(?:rab|cid|sim|robi)(?![a-z])|র‍্যাব|সিআইডি|court|আদালত|দুদক|"
             r"tax office|কর অফিস|grameenphone|banglalink|teletalk|গ্রামীণফোন|রবি|বাংলালিংক|টেলিটক|operator|অপারেটর|সিম"],
            [r"bondho|বন্ধ|block|ব্লক|deactivat|replace|রিপ্লেস|(?<![a-z])(?:case|fine|spam|jail)(?![a-z])|মামলা|জেল|"
             r"জরিমানা|warrant|ওয়ারেন্ট|স্প্যাম|illegal|অবৈধ"],
            [r"call|কল|code|কোড|taka|টাকা|pathan|পাঠান|link|লিংক|" + SECRET],
        ],
        "unless": [WARNING],
        "why_en": "Someone claims to be from BTRC, the police, a court or your mobile operator and threatens to block your SIM or file a case unless you call, pay or share a code.",
        "why_bn": "কেউ বিটিআরসি, পুলিশ, আদালত বা মোবাইল অপারেটর পরিচয় দিয়ে কল, টাকা বা কোড না দিলে সিম বন্ধ বা মামলার হুমকি দিচ্ছে।",
        "advice_en": "Officials do not threaten you by phone or ask for money or codes. Hang up and contact the office yourself through its official number.",
        "advice_bn": "সরকারি কর্মকর্তারা ফোনে হুমকি দিয়ে টাকা বা কোড চান না। কল কেটে নিজে অফিসের অফিসিয়াল নম্বরে যোগাযোগ করুন।",
    },
    {
        "id": "task_scam",
        "name_en": "Paid tasks or online earning group",
        "name_bn": "টাস্ক বা অনলাইন আয়ের গ্রুপ",
        "weight": 65,
        "groups": [
            [r"earn|earning|income|ইনকাম|আয়|ay korun|commission|কমিশন|profit|লাভ"],
            [r"task|টাস্ক|like|লাইক|subscribe|সাবস্ক্রাইব|review|রিভিউ|rating|রেটিং|telegram|টেলিগ্রাম|whatsapp group|"
             r"youtube|ইউটিউব|video|ভিডিও|tiktok|টিকটক"],
            [r"deposit|ডিপোজিট|fee|ফি|joma|জমা|invest|ইনভেস্ট|recharge|রিচার্জ|registration|রেজিস্ট্রেশন|"
             r"tk|taka|টাকা|bkash|nagad|বিকাশ|নগদ"],
        ],
        "unless": [WARNING],
        "why_en": "Easy money for liking videos, writing reviews or doing tasks, but you must deposit or pay first. The first small payouts are bait.",
        "why_bn": "ভিডিও লাইক, রিভিউ বা টাস্কের বিনিময়ে সহজ আয়ের প্রস্তাব, কিন্তু আগে টাকা জমা দিতে হবে। প্রথমে অল্প টাকা দেওয়া হয় ফাঁদ হিসেবে।",
        "advice_en": "Real jobs never ask you to pay to start. Do not deposit anything, and leave the group.",
        "advice_bn": "সত্যিকারের কাজে শুরু করতে টাকা দিতে হয় না। কোনো টাকা জমা দেবেন না, গ্রুপ থেকে বের হয়ে যান।",
    },
    {
        "id": "betting_gambling",
        "name_en": "Online betting or gambling bait",
        "name_bn": "অনলাইন বেটিং বা জুয়ার প্রলোভন",
        "weight": 65,
        "groups": [
            [r"(?<![a-z])(?:bet|betting|jua)(?![a-z])|বেটিং|casino|ক্যাসিনো|জুয়া|aviator|crash game|slot game|"
             r"স্লট গেম|1xbet|ludo khela"],
            [r"taka|টাকা|tk|deposit|ডিপোজিট|win|jit|জিত|জেত|bkash|nagad|বিকাশ|নগদ|account|একাউন্ট|অ্যাকাউন্ট"],
        ],
        "unless": [WARNING],
        "why_en": "An invitation to online betting or gambling with promised big wins. Online gambling is illegal in Bangladesh and the money is usually lost.",
        "why_bn": "বড় জেতার লোভ দেখিয়ে অনলাইন বেটিং বা জুয়ায় আমন্ত্রণ। বাংলাদেশে অনলাইন জুয়া অবৈধ এবং টাকা সাধারণত হারিয়ে যায়।",
        "advice_en": "Do not send money or open an account. Block the sender.",
        "advice_bn": "টাকা পাঠাবেন না বা একাউন্ট খুলবেন না। প্রেরককে ব্লক করুন।",
    },
    {
        "id": "advance_payment",
        "name_en": "Advance payment to a stranger",
        "name_bn": "অচেনা কাউকে অগ্রিম টাকা",
        "weight": 45,
        "groups": [
            [r"advance|অ্যাডভান্স|এডভান্স|ogrim|অগ্রিম|booking money|বুকিং মানি|token money|টোকেন"],
            [r"rent|ভাড়া|bhara|flat|ফ্ল্যাট|basa|বাসা|room|রুম|chabi|চাবি|seat|সিট|visa|ভিসা|ticket|টিকিট|"
             r"product|পণ্য|order|অর্ডার|delivery|ডেলিভারি|courier|কুরিয়ার"],
            [r"bkash|nagad|rocket|বিকাশ|নগদ|রকেট|pathan|পাঠান|korun|করুন|taka|টাকা|tk"],
        ],
        "unless": [WARNING],
        "why_en": "You are asked to pay in advance by mobile money for a flat, ticket, visa or product before you have seen it.",
        "why_bn": "দেখার আগেই ফ্ল্যাট, টিকিট, ভিসা বা পণ্যের জন্য মোবাইল ব্যাংকিংয়ে অগ্রিম টাকা চাওয়া হচ্ছে।",
        "advice_en": "Pay only after you have seen the flat or product, or use cash on delivery. Check the person through someone you know.",
        "advice_bn": "ফ্ল্যাট বা পণ্য নিজে দেখে তবেই টাকা দিন, অথবা ক্যাশ অন ডেলিভারি নিন। পরিচিত কারও মাধ্যমে মানুষটিকে যাচাই করুন।",
    },
    {
        "id": "urgency_pressure",
        "name_en": "Pressure to act immediately",
        "name_bn": "তাড়াহুড়ার চাপ",
        "weight": 30,
        "groups": [[r"urgent|immediately|right now|akhoni|এখনই|এক্ষুনি|within \d+ ?(hour|minute|min|hr)|জরুরি|joruri|last chance|tonight|তাড়াতাড়ি|taratari|hurry|\d+ মিনিটের মধ্যে|\d+ ঘণ্টার মধ্যে"]],
        "unless": [WARNING],
        "why_en": "The message pushes you to decide immediately.",
        "why_bn": "বার্তাটি আপনাকে এখনই সিদ্ধান্ত নিতে চাপ দিচ্ছে।",
        "advice_en": "Scammers rush you. A real provider gives you time and never needs an instant decision.",
        "advice_bn": "প্রতারকরা তাড়াহুড়া করায়। প্রকৃত প্রতিষ্ঠান সময় দেয়, তাৎক্ষণিক সিদ্ধান্ত চায় না।",
    },
    {
        "id": "payment_claim",
        "name_en": "Buyer says payment is done",
        "name_bn": "ক্রেতা বলছেন পেমেন্ট হয়ে গেছে",
        "weight": 20,
        "groups": [
            [r"payment (done|complete|sent|kore)|paid|pathiye diyechi|পাঠিয়ে দিয়েছি|পেমেন্ট (করে|হয়ে)|টাকা পাঠিয়েছি|taka pathiyechi|screenshot|স্ক্রিনশট"],
            [r"parcel|product|ship|dispatch|delivery|পার্সেল|প্রোডাক্ট|পণ্য|পাঠান|pathan|courier|কুরিয়ার"],
        ],
        "unless": [],
        "why_en": "A buyer claims they have paid and wants the goods sent.",
        "why_bn": "ক্রেতা বলছেন টাকা পাঠিয়েছেন এবং পণ্য পাঠাতে বলছেন।",
        "advice_en": "Confirm the money in your own bKash or Nagad app before shipping. A screenshot is not proof.",
        "advice_bn": "পণ্য পাঠানোর আগে নিজের বিকাশ বা নগদ অ্যাপে টাকা এসেছে কিনা দেখুন। স্ক্রিনশট প্রমাণ নয়।",
    },
]

BY_ID = {p["id"]: p for p in PATTERNS}

HOTLINES = [
    {"name": "bKash", "number": "16247"},
    {"name": "Nagad", "number": "16167"},
    {"name": "Rocket", "number": "16216"},
]

SAFE_NOTE_EN = "We cannot prove a message is safe. If in doubt, stop and use the official app or hotline."
SAFE_NOTE_BN = "আমরা নিশ্চিত করতে পারি না যে কোনো বার্তা নিরাপদ। সন্দেহ হলে থামুন এবং অফিসিয়াল অ্যাপ বা হটলাইন ব্যবহার করুন।"
