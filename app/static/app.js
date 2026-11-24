(function () {
  "use strict";

  /* ------------------------------------------------------------ helpers */
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  var store = {
    get: function (k, d) { try { var v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };

  /* ------------------------------------------------------------ strings */
  var T = {
    en: {
      skip: "Skip to the tools", title: "Scam Shield", subtitle: "Check before you send, ship or share",
      tabProof: "Payment proof", tabPretx: "Message check", tabTrainer: "Scam trainer", tabHow: "How it works",
      proofH: "Did the buyer really pay?",
      proofHint: "Upload the buyer's payment screenshot and say what you expected. We compare them and look for signs of editing. Your own bKash or Nagad app is always the final word.",
      dropTitle: "Add the payment screenshot", dropHelp: "Drop it here, paste it (Ctrl+V), or tap to choose. PNG, JPEG or WebP, up to 4 MB.",
      optHint: "All fields are optional, but each detail makes the check stronger.",
      buyerRequired: "Enter the buyer's number: the number the money was sent from.", buyerInvalid: "That is not a Bangladeshi mobile number. Use 11 digits like 01712345678.",
      clearForm: "Clear", cleared: "Cleared",
      remove: "Remove", expAmount: "Amount you expected (Tk)", expRecipient: "Your number (receiver)", expSender: "Buyer's number (payer)", optional: "Optional",
      chatTime: "About when the buyer paid (rough is fine)", orderRef: "Order name or number",
      manual: "Type the screenshot details yourself",
      manualHint: "Use this if you have no screenshot, or to correct what was read. Anything you type here is used instead.",
      mAmount: "Amount shown", mTrx: "Transaction ID (TrxID)", mRecipient: "Receiver on screenshot", mSender: "Sender on screenshot", mTime: "Time shown",
      checkPayment: "Check payment",
      pretxH: "Got a strange call or message?",
      pretxHint: "Paste the SMS, or write what the caller is asking for. Bangla, English and Banglish all work. We show exactly which words are the warning signs.",
      msgLabel: "Message or what happened", msgPh: "Example: a man says he sent money to my number by mistake and wants it back",
      recVoice: "Record voice", scanScreen: "Scan a screen", camHint: "Point the camera at the phone showing the call or message, then press Capture and check.", capture: "Capture and check", srcCam: "Camera", srcShare: "Share my screen", srcUpload: "Upload screenshot", shareHint: "Pick the window or screen with the call or chat (WhatsApp Web, Messenger, a phone-mirroring app), then press Capture and check.", fileHint: "Choose a screenshot or photo of the call or message. You can also paste one here with Ctrl+V.", autoChk: "Check again by itself when the screen changes (every 10 s)", shareNo: "Screen sharing works in a computer browser. On a phone, take a screenshot and upload it.", shareEnded: "Screen sharing stopped.", camNo: "The camera is not available here. Upload a screenshot or photo of the call or message instead.", d_incoming: "Incoming call", d_outgoing: "Outgoing call (you are calling)", d_ongoing: "Call in progress", d_missed: "Missed call", d_unknown: "Call", m_outgoing: "sent by you", k_number: "Phone number", numberH: "About this number", sureH: "How sure is this?", reading: "Reading the screen…", screenH: "What we read from the screen", k_call: "Incoming call", k_sms: "SMS", k_chat: "Chat message", k_other: "Screen", nk_official: "official hotline", nk_personal: "personal 01 number", nk_foreign: "foreign number", needAI: "Reading a photo needs the AI. Type the message in the box instead.", fromScreen: "Screen photo", recording: "Recording", paused: "Paused", pause: "Pause", resume: "Resume",
      checkVoice: "Check voice", cancel: "Cancel", transcribing: "Turning your voice into text",
      micDenied: "Microphone is blocked. Allow it from the icon in the address bar, then try again.",
      noSpeech: "No words were heard. Try again closer to the microphone, or type the message.",
      voiceMax: "Limit reached, recording paused. Press Check voice.", maxNote: "up to 1:30",
      noRecorder: "This browser cannot record audio. Type the message instead.",
      voiceFallback: "AI voice-to-text was not available, so your browser's speech recognition was used.",
      tryEx: "Try one:", checkMsg: "Check message", kbd: "Tip: Ctrl+Enter checks too.",
      trainerH: "Practise saying no", trHome: "Play through a real scam, step by step. Nothing here is real and no one is calling you.",
      howH: "How Scam Shield decides",
      howP: "Every answer comes from rules you can read below. AI, when switched on, adds reasoning and reads screenshots, but it can only raise a warning, never lower one.",
      st1: "Read", st1d: "The message text, or the fields in the screenshot (by AI or typed by you).",
      st2: "Match", st2d: "Known scam patterns in Bangla, English and Banglish; links and phone numbers are checked separately.",
      st3: "Compare", st3d: "For payments: amount, your number, time, TrxID, editing-app traces and reused screenshots.",
      st4: "Explain", st4d: "You see which words or checks caused the warning, and what to do next.",
      accH: "How accurate is it?", privH: "Privacy",
      privP: "We never ask for your PIN or OTP. Checks are not stored on our server; your recent checks stay in this browser only. With AI on, the text or image is sent to the AI provider to be read.",
      limitsH: "What it cannot do", lim1: "It cannot prove a payment is real. Only your own account can.",
      lim2: "New scam wording may not match any pattern yet.", lim3: "Spotting edited images is a clue, not forensic proof.",
      libH: "The pattern library",
      footer: "Warnings, not guarantees. Scam Shield never asks for your PIN or OTP and never calls a payment safe.",
      built: "Built by team JU_Segfault for CoU AI Hackathon 2026.",
      aiOn: "AI on", aiDemo: "AI demo mode", aiOff: "Rules only",
      s_high: "High risk", s_medium: "Be careful", s_low: "No known pattern",
      s_likely_fake: "Likely fake", s_suspicious: "Suspicious", s_consistent: "Matches", s_clean: "No red flags",
      h_clean: "Nothing suspicious in the screenshot itself.",
      h_high: "Stop. This looks like a scam.", h_medium: "Slow down and check first.", h_low: "We found no known scam pattern.",
      h_likely_fake: "Do not ship this order yet.", h_suspicious: "Some details do not add up.", h_consistent: "The details match what you expected.",
      riskScore: "Risk score", yourMsg: "Your message, warning signs marked", lgStrong: "Strong warning sign", lgWeak: "Warning sign",
      whyH: "Why", linksH: "Links and numbers in the message", doH: "What to do", hotH: "Official hotlines (call them yourself)",
      checksH: "What we checked", readH: "Read from the screenshot", imgH: "The image file",
      copy: "Copy result", copied: "Result copied", share: "Share on WhatsApp", copyFail: "Could not copy. Select the text instead.",
      viaAI: "Checked by our rules and AI", viaRules: "Checked by our rules", aiFail: "AI was not available, so this is the rules result.",
      emptyT: "Paste a message and press Check message. Your result appears here.",
      emptyP: "Add a screenshot or type the details, then press Check payment. Your result appears here.",
      needInput: "Add a screenshot, or type the details under \"Type the screenshot details yourself\".",
      needText: "Type or paste a message first.",
      noMic: "Voice input does not work in this browser. Try Chrome.",
      recent: "Recent checks on this device", clear: "Clear",
      tooBig: "That image is larger than 4 MB. Send a smaller screenshot.", badType: "Use a PNG, JPEG or WebP image.",
      offline: "Cannot reach Scam Shield. Check your internet connection and try again.",
      start: "Start", step: "Step", of: "of", nextStep: "Next", seeResult: "See my result", scoreH: "Your result",
      flagsH: "Warning signs in this scam", safeH: "What to do in real life", again: "Choose another scenario",
      freeH: "Free chat with an AI scammer", freeP: "The AI plays the scammer and grows more pushy. End the chat to get graded.",
      freeStart: "Start free chat", send: "Send", end: "End and grade", you: "You", scammer: "Caller",
      typeReply: "Type your reply", grading: "Grading your chat", caught: "You handled well", missed: "You missed", tip: "Tip",
      excellent: "Strong. You spotted the traps.", okay: "Mixed. Replay and try the safer choices.", weak: "Risky. Read the warning signs and try again.",
      f_amount: "Amount", f_trx_id: "TrxID", f_sender: "From (payer)", f_recipient: "To (receiver)", f_datetime: "Time", f_provider: "Provider",
      i_format: "Format", i_size: "Size", i_editor: "Editing app",
      m_set: "Set", m_dev: "Tuning set", m_holdout: "Unseen set", m_holdout2: "Unseen set 2", m_caught: "Scams flagged", m_false: "Real messages wrongly flagged",
      m_note: "These are our own small test sets (Bangla, English, Banglish). We tuned the patterns on the tuning set only. Treat this as a sanity check, not a benchmark.",
      libName: "Pattern", libWhy: "What it looks for", libWeight: "Weight",
      linkChecks: "Plus link and number checks: look-alike links, hidden short links, risky domains, and personal numbers posing as customer care.",
      shareTpl: "Scam Shield check: {v}. {why} Check yours at {url}",
      rate: "Too many checks in a minute. Wait a little and try again.",
      offMode: "Offline: checks on this device", viaOffline: "Checked on this device with our rules (no internet needed)",
      proofOffline: "Payment checks need internet because the screenshot is read online. Message checks and the trainer work offline.",
      offH: "Works without internet", offP: "Open Scam Shield once while online and it is saved on your device. After that, message checks and the trainer work with no internet, using the same rules as the server."
    },
    bn: {
      skip: "টুলে যান", title: "স্ক্যাম শিল্ড", subtitle: "পাঠানো, ডেলিভারি বা শেয়ার করার আগে যাচাই করুন",
      tabProof: "পেমেন্ট প্রুফ", tabPretx: "মেসেজ যাচাই", tabTrainer: "স্ক্যাম ট্রেনার", tabHow: "কীভাবে কাজ করে",
      proofH: "ক্রেতা কি সত্যিই টাকা পাঠিয়েছেন?",
      proofHint: "ক্রেতার পেমেন্ট স্ক্রিনশট দিন এবং কী আশা করেছিলেন লিখুন। আমরা দুটো মিলিয়ে দেখব এবং এডিটের চিহ্ন খুঁজব। চূড়ান্ত প্রমাণ সবসময় আপনার নিজের বিকাশ বা নগদ অ্যাপ।",
      dropTitle: "পেমেন্টের স্ক্রিনশট দিন", dropHelp: "এখানে টেনে আনুন, পেস্ট করুন (Ctrl+V), বা ট্যাপ করে বেছে নিন। PNG, JPEG বা WebP, ৪ MB পর্যন্ত।",
      optHint: "সব ঘর ঐচ্ছিক, তবে প্রতিটি তথ্য যাচাইকে আরও শক্তিশালী করে।",
      buyerRequired: "ক্রেতার নম্বর দিন: যে নম্বর থেকে টাকা পাঠানো হয়েছে।", buyerInvalid: "এটি বাংলাদেশের মোবাইল নম্বর নয়। ১১ সংখ্যায় লিখুন, যেমন 01712345678।",
      clearForm: "মুছুন", cleared: "মুছে ফেলা হয়েছে",
      remove: "সরান", expAmount: "প্রত্যাশিত টাকা", expRecipient: "আপনার নম্বর (প্রাপক)", expSender: "ক্রেতার নম্বর (প্রেরক)", optional: "ঐচ্ছিক",
      chatTime: "ক্রেতা আনুমানিক কখন পাঠিয়েছেন", orderRef: "অর্ডারের নাম বা নম্বর",
      manual: "স্ক্রিনশটের তথ্য নিজে লিখুন",
      manualHint: "স্ক্রিনশট না থাকলে, বা পড়া তথ্য ঠিক করতে এটি ব্যবহার করুন। এখানে যা লিখবেন সেটাই ধরা হবে।",
      mAmount: "স্ক্রিনশটে টাকার পরিমাণ", mTrx: "লেনদেন আইডি (TrxID)", mRecipient: "স্ক্রিনশটে প্রাপক", mSender: "স্ক্রিনশটে প্রেরক", mTime: "স্ক্রিনশটে সময়",
      checkPayment: "পেমেন্ট যাচাই করুন",
      pretxH: "অদ্ভুত কল বা মেসেজ পেয়েছেন?",
      pretxHint: "এসএমএসটি পেস্ট করুন, অথবা কলকারী কী চাইছে লিখুন। বাংলা, ইংরেজি ও ইংরেজি হরফে বাংলা চলবে। কোন শব্দগুলো বিপদের সংকেত তা আমরা চিহ্নিত করে দেখাব।",
      msgLabel: "মেসেজ বা কী ঘটেছে", msgPh: "যেমন: একজন বলছে ভুল করে আমার নম্বরে টাকা পাঠিয়েছে, ফেরত চায়",
      recVoice: "ভয়েস রেকর্ড করুন", scanScreen: "স্ক্রিন যাচাই", camHint: "যে ফোনে কল বা মেসেজ দেখা যাচ্ছে তার দিকে ক্যামেরা ধরুন, তারপর ছবি তুলে যাচাই চাপুন।", capture: "ছবি তুলে যাচাই করুন", srcCam: "ক্যামেরা", srcShare: "নিজের স্ক্রিন শেয়ার", srcUpload: "স্ক্রিনশট দিন", shareHint: "কল বা চ্যাট যে উইন্ডো বা স্ক্রিনে আছে তা বেছে নিন (হোয়াটসঅ্যাপ ওয়েব, মেসেঞ্জার, ফোন-মিররিং অ্যাপ), তারপর ছবি তুলে যাচাই চাপুন।", fileHint: "কল বা মেসেজের স্ক্রিনশট বা ছবি বেছে নিন। Ctrl+V দিয়ে পেস্টও করতে পারেন।", autoChk: "স্ক্রিন বদলালে নিজে থেকে আবার যাচাই করুন (প্রতি ১০ সেকেন্ড)", shareNo: "স্ক্রিন শেয়ার কম্পিউটারের ব্রাউজারে কাজ করে। ফোনে স্ক্রিনশট নিয়ে আপলোড করুন।", shareEnded: "স্ক্রিন শেয়ার বন্ধ হয়েছে।", camNo: "এখানে ক্যামেরা পাওয়া যাচ্ছে না। কল বা মেসেজের স্ক্রিনশট বা ছবি দিন।", d_incoming: "ইনকামিং কল", d_outgoing: "আউটগোয়িং কল (আপনি কল করছেন)", d_ongoing: "চলমান কল", d_missed: "মিসড কল", d_unknown: "কল", m_outgoing: "আপনার পাঠানো", k_number: "ফোন নম্বর", numberH: "এই নম্বর সম্পর্কে", sureH: "এই ফলাফল কতটা নিশ্চিত?", reading: "স্ক্রিন পড়া হচ্ছে…", screenH: "স্ক্রিন থেকে যা পড়া হলো", k_call: "ইনকামিং কল", k_sms: "এসএমএস", k_chat: "চ্যাট মেসেজ", k_other: "স্ক্রিন", nk_official: "অফিসিয়াল হটলাইন", nk_personal: "ব্যক্তিগত ০১ নম্বর", nk_foreign: "বিদেশি নম্বর", needAI: "ছবি পড়তে এআই লাগে। বক্সে মেসেজটি লিখে চেক করুন।", fromScreen: "স্ক্রিনের ছবি", recording: "রেকর্ড হচ্ছে", paused: "থামানো আছে", pause: "থামান", resume: "আবার শুরু",
      checkVoice: "ভয়েস যাচাই করুন", cancel: "বাতিল", transcribing: "আপনার কথা লেখায় রূপান্তর হচ্ছে",
      micDenied: "মাইক্রোফোন বন্ধ করা আছে। অ্যাড্রেস বারের আইকন থেকে অনুমতি দিয়ে আবার চেষ্টা করুন।",
      noSpeech: "কোনো কথা শোনা যায়নি। মাইক্রোফোনের কাছে এসে আবার বলুন, অথবা মেসেজটি লিখুন।",
      voiceMax: "সময়সীমা শেষ, রেকর্ড থামানো হয়েছে। ভয়েস যাচাই করুন চাপুন।", maxNote: "সর্বোচ্চ ১:৩০",
      noRecorder: "এই ব্রাউজার অডিও রেকর্ড করতে পারে না। মেসেজটি লিখে দিন।",
      voiceFallback: "এআই দিয়ে ভয়েস লেখায় রূপান্তর করা যায়নি, তাই ব্রাউজারের নিজস্ব স্পিচ রিকগনিশন ব্যবহার হয়েছে।",
      tryEx: "উদাহরণ:", checkMsg: "মেসেজ যাচাই করুন", kbd: "Ctrl+Enter চাপলেও যাচাই হবে।",
      trainerH: "না বলা অনুশীলন করুন", trHome: "ধাপে ধাপে একটি বাস্তব প্রতারণা খেলে দেখুন। এখানে সবকিছু নকল, কেউ আপনাকে ফোন করছে না।",
      howH: "স্ক্যাম শিল্ড কীভাবে সিদ্ধান্ত নেয়",
      howP: "প্রতিটি উত্তর আসে নিচের নিয়মগুলো থেকে, যা আপনি পড়তে পারবেন। এআই চালু থাকলে যুক্তি যোগ করে ও স্ক্রিনশট পড়ে, কিন্তু সতর্কতা শুধু বাড়াতে পারে, কমাতে পারে না।",
      st1: "পড়া", st1d: "মেসেজের লেখা, বা স্ক্রিনশটের তথ্য (এআই পড়ে বা আপনি লেখেন)।",
      st2: "মেলানো", st2d: "বাংলা, ইংরেজি ও বাংলিশে পরিচিত প্রতারণার ধরন; লিংক ও ফোন নম্বর আলাদা করে যাচাই।",
      st3: "তুলনা", st3d: "পেমেন্টের জন্য: টাকা, আপনার নম্বর, সময়, TrxID, এডিটিং অ্যাপের চিহ্ন ও একই স্ক্রিনশট আবার ব্যবহার।",
      st4: "ব্যাখ্যা", st4d: "কোন শব্দ বা যাচাইয়ের জন্য সতর্কতা এল এবং এখন কী করবেন, তা দেখতে পাবেন।",
      accH: "এটি কতটা নির্ভুল?", privH: "গোপনীয়তা",
      privP: "আমরা কখনো আপনার পিন বা ওটিপি চাই না। যাচাইগুলো আমাদের সার্ভারে রাখা হয় না; সাম্প্রতিক যাচাই শুধু এই ব্রাউজারে থাকে। এআই চালু থাকলে লেখা বা ছবি পড়ার জন্য এআই প্রতিষ্ঠানের কাছে যায়।",
      limitsH: "যা পারে না", lim1: "পেমেন্ট আসল কি না প্রমাণ করতে পারে না। শুধু আপনার নিজের অ্যাকাউন্ট পারে।",
      lim2: "নতুন ধরনের প্রতারণার ভাষা হয়তো এখনো কোনো নিয়মে মেলে না।", lim3: "এডিট করা ছবি চেনা একটি সংকেত, ফরেনসিক প্রমাণ নয়।",
      libH: "প্রতারণার ধরনের তালিকা",
      footer: "এটি সতর্কতা দেয়, নিশ্চয়তা নয়। স্ক্যাম শিল্ড কখনো পিন বা ওটিপি চায় না এবং কোনো পেমেন্টকে নিরাপদ বলে না।",
      built: "তৈরি করেছে টিম JU_Segfault, সিওইউ এআই হ্যাকাথন ২০২৬-এর জন্য।",
      aiOn: "এআই চালু", aiDemo: "এআই ডেমো", aiOff: "শুধু নিয়ম",
      s_high: "উচ্চ ঝুঁকি", s_medium: "সতর্ক থাকুন", s_low: "পরিচিত ধরন নেই",
      s_likely_fake: "সম্ভবত ভুয়া", s_suspicious: "সন্দেহজনক", s_consistent: "মিলেছে", s_clean: "সন্দেহ পাওয়া যায়নি",
      h_clean: "স্ক্রিনশটে নিজে থেকে সন্দেহজনক কিছু পাওয়া যায়নি।",
      h_high: "থামুন। এটি প্রতারণা বলে মনে হচ্ছে।", h_medium: "তাড়াহুড়ো নয়, আগে যাচাই করুন।", h_low: "পরিচিত কোনো প্রতারণার ধরন পাওয়া যায়নি।",
      h_likely_fake: "এই অর্ডার এখনই পাঠাবেন না।", h_suspicious: "কিছু তথ্য মিলছে না।", h_consistent: "তথ্য আপনার প্রত্যাশার সঙ্গে মিলেছে।",
      riskScore: "ঝুঁকির স্কোর", yourMsg: "আপনার মেসেজ, বিপদের সংকেত চিহ্নিত", lgStrong: "বড় বিপদের সংকেত", lgWeak: "সতর্কতার সংকেত",
      whyH: "কেন", linksH: "মেসেজের লিংক ও নম্বর", doH: "কী করবেন", hotH: "অফিসিয়াল হটলাইন (নিজে ফোন করুন)",
      checksH: "যা যাচাই করা হয়েছে", readH: "স্ক্রিনশট থেকে পড়া তথ্য", imgH: "ছবির ফাইল",
      copy: "ফল কপি করুন", copied: "ফল কপি হয়েছে", share: "হোয়াটসঅ্যাপে শেয়ার", copyFail: "কপি করা যায়নি। লেখাটি সিলেক্ট করে নিন।",
      viaAI: "আমাদের নিয়ম ও এআই দিয়ে যাচাই", viaRules: "আমাদের নিয়ম দিয়ে যাচাই", aiFail: "এআই পাওয়া যায়নি, তাই এটি নিয়মভিত্তিক ফল।",
      emptyT: "মেসেজ পেস্ট করে মেসেজ যাচাই করুন চাপুন। ফল এখানে দেখাবে।",
      emptyP: "স্ক্রিনশট দিন বা তথ্য লিখুন, তারপর পেমেন্ট যাচাই করুন চাপুন। ফল এখানে দেখাবে।",
      needInput: "স্ক্রিনশট দিন, অথবা \"স্ক্রিনশটের তথ্য নিজে লিখুন\" অংশে তথ্য লিখুন।",
      needText: "আগে একটি মেসেজ লিখুন বা পেস্ট করুন।",
      noMic: "এই ব্রাউজারে ভয়েস ইনপুট চলে না। ক্রোম ব্যবহার করুন।",
      recent: "এই ডিভাইসে সাম্প্রতিক যাচাই", clear: "মুছুন",
      tooBig: "ছবিটি ৪ MB-এর বেশি। ছোট স্ক্রিনশট দিন।", badType: "PNG, JPEG বা WebP ছবি দিন।",
      offline: "স্ক্যাম শিল্ডে পৌঁছানো যাচ্ছে না। ইন্টারনেট সংযোগ দেখে আবার চেষ্টা করুন।",
      start: "শুরু", step: "ধাপ", of: "/", nextStep: "পরের ধাপ", seeResult: "ফল দেখুন", scoreH: "আপনার ফল",
      flagsH: "এই প্রতারণার বিপদ সংকেত", safeH: "বাস্তবে কী করবেন", again: "অন্য দৃশ্য বেছে নিন",
      freeH: "এআই প্রতারকের সঙ্গে ফ্রি চ্যাট", freeP: "এআই প্রতারক সাজবে এবং ক্রমশ চাপ বাড়াবে। চ্যাট শেষ করলে মূল্যায়ন পাবেন।",
      freeStart: "ফ্রি চ্যাট শুরু", send: "পাঠান", end: "শেষ করে মূল্যায়ন", you: "আপনি", scammer: "কলকারী",
      typeReply: "উত্তর লিখুন", grading: "মূল্যায়ন হচ্ছে", caught: "যা ভালো করেছেন", missed: "যা মিস করেছেন", tip: "পরামর্শ",
      excellent: "চমৎকার। ফাঁদগুলো ধরতে পেরেছেন।", okay: "মিশ্র ফল। আবার খেলে নিরাপদ বিকল্প বেছে দেখুন।", weak: "ঝুঁকিপূর্ণ। বিপদ সংকেতগুলো পড়ে আবার চেষ্টা করুন।",
      f_amount: "টাকা", f_trx_id: "TrxID", f_sender: "যেখান থেকে (প্রেরক)", f_recipient: "যেখানে (প্রাপক)", f_datetime: "সময়", f_provider: "প্রতিষ্ঠান",
      i_format: "ধরন", i_size: "মাপ", i_editor: "এডিটিং অ্যাপ",
      m_set: "সেট", m_dev: "টিউনিং সেট", m_holdout: "অদেখা সেট", m_holdout2: "অদেখা সেট ২", m_caught: "প্রতারণা ধরা পড়েছে", m_false: "আসল মেসেজ ভুল করে সতর্কিত",
      m_note: "এগুলো আমাদের নিজেদের লেখা ছোট পরীক্ষার সেট (বাংলা, ইংরেজি, বাংলিশ)। নিয়মগুলো শুধু টিউনিং সেটে ঠিক করা হয়েছে। এটিকে প্রাথমিক যাচাই হিসেবে দেখুন, মানদণ্ড হিসেবে নয়।",
      libName: "ধরন", libWhy: "যা খোঁজে", libWeight: "ওজন",
      linkChecks: "সঙ্গে লিংক ও নম্বর যাচাই: নকল লিংক, লুকানো ছোট লিংক, ঝুঁকিপূর্ণ ডোমেইন, এবং কাস্টমার কেয়ার সাজা ব্যক্তিগত নম্বর।",
      shareTpl: "স্ক্যাম শিল্ড যাচাই: {v}। {why} আপনিও যাচাই করুন: {url}",
      rate: "এক মিনিটে অনেক বেশি যাচাই। একটু অপেক্ষা করে আবার চেষ্টা করুন।",
      offMode: "অফলাইন: এই ডিভাইসেই যাচাই", viaOffline: "ইন্টারনেট ছাড়াই এই ডিভাইসে আমাদের নিয়ম দিয়ে যাচাই",
      proofOffline: "পেমেন্ট যাচাইয়ে ইন্টারনেট লাগে, কারণ স্ক্রিনশট অনলাইনে পড়া হয়। মেসেজ যাচাই ও ট্রেনার ইন্টারনেট ছাড়াই চলে।",
      offH: "ইন্টারনেট ছাড়াও চলে", offP: "অনলাইনে একবার স্ক্যাম শিল্ড খুললেই এটি আপনার ডিভাইসে থেকে যায়। এরপর ইন্টারনেট ছাড়াই মেসেজ যাচাই ও ট্রেনার চলবে, সার্ভারের একই নিয়মে।"
    }
  };

  var lang = store.get("lang", "en");
  if (lang !== "en" && lang !== "bn") lang = "en";
  var aiMode = "rules", voiceAI = false;
  var scenarios = store.get("scenarios", []), meta = null, metrics = null;
  var rulesData = store.get("rules", null);
  var isOffline = navigator.onLine === false;
  var rerender = {};
  var tr = function (k) { return (T[lang] && T[lang][k]) || T.en[k] || k; };
  var pick = function (o, base) { return o[base + "_" + lang] || o[base + "_en"] || ""; };
  var fmtNum = function (n) {
    var s = Number(n).toLocaleString("en-US", { maximumFractionDigits: 2 });
    return lang === "bn" ? s.replace(/\d/g, function (d) { return "০১২৩৪৫৬৭৮৯"[d]; }) : s;
  };

  function toast(msg) {
    var el = $("#toast"); el.textContent = msg; el.classList.add("show");
    clearTimeout(toast._t); toast._t = setTimeout(function () { el.classList.remove("show"); }, 2600);
  }

  /* ------------------------------------------------------------ i18n / theme */
  function applyLang() {
    document.documentElement.lang = lang;
    $("#langBtn").textContent = lang === "en" ? "বাংলা" : "English";
    $("#langBtn").setAttribute("aria-label", lang === "en" ? "বাংলায় দেখুন" : "Switch to English");
    $$("[data-t]").forEach(function (el) { el.textContent = tr(el.getAttribute("data-t")); });
    $$("[data-tp]").forEach(function (el) { el.placeholder = tr(el.getAttribute("data-tp")); });
    if (window.__voiceRender) window.__voiceRender();
    var be = $("#pBuyerErr"); if (be && be.getAttribute("data-k")) be.textContent = tr(be.getAttribute("data-k"));
    var b = $("#aiBadge");
    b.textContent = isOffline ? tr("offMode") : aiMode === "live" ? tr("aiOn") : aiMode === "mock" ? tr("aiDemo") : tr("aiOff");
    b.classList.toggle("on", !isOffline && aiMode === "live");
    b.classList.toggle("off", isOffline);
    Object.keys(rerender).forEach(function (k) { rerender[k](false); });
    renderHistory("pretx"); renderHistory("proof");
    renderTrainerHome(); renderHow();
  }
  $("#langBtn").addEventListener("click", function () {
    lang = lang === "en" ? "bn" : "en"; store.set("lang", lang); applyLang();
  });
  $("#themeBtn").addEventListener("click", function () {
    var next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("theme", next); } catch (e) {}
  });

  /* ------------------------------------------------------------ tabs */
  var TABS = ["proof", "pretx", "trainer", "how"];
  function showTab(id, focus) {
    if (TABS.indexOf(id) < 0) id = "proof";
    $$(".tab").forEach(function (t) {
      var on = t.dataset.tab === id;
      t.setAttribute("aria-selected", on ? "true" : "false");
      t.tabIndex = on ? 0 : -1;
      if (on && focus) t.focus();
    });
    $$(".panel").forEach(function (p) { p.hidden = p.id !== id; });
    if (id !== "pretx" && typeof camClose === "function" && $("#sPanel")) camClose();
    if (location.hash !== "#" + id) history.replaceState(null, "", "#" + id);
  }
  $$(".tab").forEach(function (t, i, all) {
    t.addEventListener("click", function () { showTab(t.dataset.tab); });
    t.addEventListener("keydown", function (e) {
      var d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0;
      if (d) { e.preventDefault(); showTab(all[(i + d + all.length) % all.length].dataset.tab, true); }
    });
  });
  window.addEventListener("hashchange", function () { showTab(location.hash.slice(1)); });

  /* ------------------------------------------------------------ api */
  function api(path, opts) {
    return fetch(path, opts).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (r.status === 429) throw new Error(tr("rate"));
        if (!r.ok) throw new Error(j.detail || ("HTTP " + r.status));
        return j;
      });
    }, function () { var e = new Error(tr("offline")); e.offline = true; throw e; });
  }
  function busy(btn, on) { btn.setAttribute("aria-busy", on ? "true" : "false"); btn.disabled = on; }

  /* ------------------------------------------------------------ shared slip parts */
  var EMPTY_ICON = '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M10 4h28v40l-4-3-4 3-4-3-4 3-4-3-4 3-4-3V4Z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M16 14h16M16 21h16M16 28h10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
  function empty(el, key) { el.innerHTML = '<div class="slip-empty"><div>' + EMPTY_ICON + "<p>" + esc(tr(key)) + "</p></div></div>"; }
  function head(kind, score, sub, animate, label) {
    label = label || kind;
    return '<div class="slip-head"><div><h2 style="margin:0">' + esc(tr("h_" + label)) + "</h2>" +
      (sub ? '<p class="fine">' + esc(sub) + "</p>" : "") +
      '<div class="score"><span class="fine">' + esc(tr("riskScore")) + ": <b>" + fmtNum(score) + "</b>/" + fmtNum(100) + "</span>" +
      '<div class="score-bar" role="img" aria-label="' + esc(tr("riskScore")) + " " + score + '/100"><i class="b-' + kind + '" style="width:' + Math.max(4, score) + '%"></i></div></div></div>' +
      '<span class="stamp t-' + kind + (animate ? " land" : "") + '">' + esc(tr("s_" + label)) + "</span></div>";
  }
  function hotlinesHtml(list) {
    if (!list || !list.length) return "";
    return '<div class="hotlines">' + list.map(function (h) {
      return '<a href="tel:' + esc(h.number) + '">' + esc(h.name) + "<b>" + esc(h.number) + "</b></a>";
    }).join("") + "</div>";
  }
  function actionsHtml() {
    return '<div class="actions"><button type="button" class="ghost" data-act="copy">' + esc(tr("copy")) +
      '</button><button type="button" class="ghost" data-act="share">' + esc(tr("share")) + "</button></div>";
  }
  function wireActions(root, summary) {
    $$("[data-act]", root).forEach(function (b) {
      b.addEventListener("click", function () {
        var text = summary();
        if (b.dataset.act === "copy") {
          (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject())
            .then(function () { toast(tr("copied")); }, function () { toast(tr("copyFail")); });
        } else {
          window.open("https://wa.me/?text=" + encodeURIComponent(text), "_blank", "noopener");
        }
      });
    });
  }

  /* ------------------------------------------------------------ history */
  var HKEY = { pretx: "hist_pretx", proof: "hist_proof" };
  function addHistory(kind, item) {
    var list = store.get(HKEY[kind], []);
    list.unshift(item); store.set(HKEY[kind], list.slice(0, 6)); renderHistory(kind);
  }
  function renderHistory(kind) {
    var box = $(kind === "pretx" ? "#tHist" : "#pHist"), list = store.get(HKEY[kind], []);
    if (!list.length) { box.innerHTML = ""; return; }
    box.innerHTML = "<h3>" + esc(tr("recent")) + "</h3>" + list.map(function (it, i) {
      var v = it.res.risk || it.res.verdict;
      var when = new Date(it.ts).toLocaleTimeString(lang === "bn" ? "bn-BD" : "en-GB", { hour: "2-digit", minute: "2-digit" });
      return '<button type="button" data-i="' + i + '"><span class="dot b-' + esc(v) + '"></span><span class="txt">' +
        esc(it.label) + "</span><time>" + esc(when) + "</time></button>";
    }).join("") + '<button type="button" class="link" data-clear style="width:auto;margin-top:4px">' + esc(tr("clear")) + "</button>";
    $$("button[data-i]", box).forEach(function (b) {
      b.addEventListener("click", function () {
        var it = list[+b.dataset.i];
        if (kind === "pretx") { $("#tText").value = it.input; countChars(); showPretx(it.res, it.input, true); }
        else showProof(it.res, true);
      });
    });
    $("[data-clear]", box).addEventListener("click", function () { store.set(HKEY[kind], []); renderHistory(kind); });
  }

  /* ------------------------------------------------------------ message check */
  function markText(text, hl) {
    var cps = Array.from(text), out = "", pos = 0;
    (hl || []).slice().sort(function (a, b) { return a.start - b.start; }).forEach(function (h) {
      if (h.start < pos || h.end > cps.length) return;
      out += esc(cps.slice(pos, h.start).join(""));
      out += '<mark class="' + (h.kind === "danger" ? "danger" : "caution") + '" title="' + esc(pick(h, "label")) + '">' +
        esc(cps.slice(h.start, h.end).join("")) + "</mark>";
      pos = h.end;
    });
    return out + esc(cps.slice(pos).join(""));
  }
  // "How sure is this?": what the verdict rests on (never changes the verdict)
  var CHECKLIST = [
    { en: "Does it ask for a PIN, OTP, password or a code that was sent to you?", bn: "পিন, ওটিপি, পাসওয়ার্ড বা আপনার কাছে আসা কোনো কোড চাইছে কি?" },
    { en: "Does it ask you to send money first, or pay a fee to receive money or a prize?", bn: "আগে টাকা পাঠাতে বা টাকা/পুরস্কার পেতে ফি দিতে বলছে কি?" },
    { en: "Does it rush or scare you (account blocked, last chance, police)?", bn: "তাড়া দিচ্ছে বা ভয় দেখাচ্ছে কি (অ্যাকাউন্ট বন্ধ, শেষ সুযোগ, পুলিশ)?" },
    { en: "Does it have a link, or ask you to install an app?", bn: "কোনো লিংক আছে কি, বা অ্যাপ ইনস্টল করতে বলছে কি?" },
    { en: "Does someone claim to be bKash, Nagad, a bank or an officer from an ordinary number?", bn: "সাধারণ নম্বর থেকে কেউ নিজেকে বিকাশ, নগদ, ব্যাংক বা কর্মকর্তা বলছে কি?" }
  ];
  function offlineHonesty(d) {
    if (d.patterns && d.patterns.length) return null;
    return { level: "unknown_rules_only", title_en: "Only known patterns were checked", title_bn: "শুধু পরিচিত ধরন যাচাই হয়েছে",
      en: "You are offline, so only our known scam patterns were checked and none matched. A new kind of scam would not be caught. Check it yourself:",
      bn: "আপনি অফলাইনে আছেন, তাই শুধু পরিচিত প্রতারণার ধরন যাচাই হয়েছে, কোনোটি মেলেনি। নতুন ধরনের প্রতারণা ধরা পড়বে না। নিজে যাচাই করুন:",
      checklist: CHECKLIST, tail: { en: "If any answer is yes, stop and call the official hotline yourself.", bn: "যেকোনো উত্তর 'হ্যাঁ' হলে থামুন এবং নিজে অফিসিয়াল হটলাইনে ফোন করুন।" } };
  }
  function honestyHtml(hn) {
    if (!hn) return "";
    var x = '<div class="sec honest lvl-' + esc(hn.level) + '"><h3>' + esc(tr("sureH")) + "</h3><p><b>" + esc(hn["title_" + lang] || hn.title_en) +
      "</b></p><p>" + esc(hn[lang] || hn.en) + "</p>";
    if (hn.checklist) x += '<ul class="self-check">' + hn.checklist.map(function (q) { return "<li>" + esc(q[lang] || q.en) + "</li>"; }).join("") + "</ul>" +
      (hn.tail ? '<p class="fine">' + esc(hn.tail[lang] || hn.tail.en) + "</p>" : "");
    if (hn.verify_en) x += '<p class="verify">' + esc(hn["verify_" + lang] || hn.verify_en) + "</p>";
    return x + "</div>";
  }
  function showPretx(d, text, fromHistory) {
    var render = function (animate) {
      var el = $("#tOut"), h = head(d.risk, d.score, null, animate);
      var hn = d.honesty !== undefined ? d.honesty : (d.source === "offline" ? offlineHonesty(d) : null);
      if (d.screen) {
        var sc = d.screen, nk = sc.number_kind;
        var kindLabel = sc.kind === "number" ? tr("k_number") : sc.kind === "call" ? tr("d_" + (sc.direction || "unknown")) :
          tr("k_" + sc.kind) + (sc.direction === "outgoing" ? " (" + tr("m_outgoing") + ")" : "");
        var tone = nk === "official" ? "good" : nk === "suspicious" ? "bad" : (nk === "foreign" || nk === "short" || nk === "hidden") ? "warn" : "";
        var nlabel = sc["number_label_" + lang] || sc.number_label_en;
        h += '<div class="sec"><h3>' + esc(tr(sc.kind === "number" ? "numberH" : "screenH")) + '</h3><div class="screen-read"><b>' + esc(kindLabel) + "</b>" +
          (sc.name ? "<span>" + esc(sc.name) + "</span>" : "") + (sc.number ? '<code>' + esc(sc.number) + "</code>" : "") +
          (nlabel ? '<span class="tag ' + tone + '">' + esc(nlabel) + "</span>" : "") +
          "</div>" + (sc.kind !== "number" && !(d.highlights && d.highlights.length) && d.text ? '<div class="quote">' + esc(d.text) + "</div>" : "") + "</div>";
      }
      if (d.highlights && d.highlights.length) {
        h += '<div class="sec"><h3>' + esc(tr("yourMsg")) + '</h3><div class="quote">' + markText(text, d.highlights) + "</div>" +
          '<div class="legend"><span><i style="background:var(--mark-danger);border-bottom:2px solid var(--red)"></i>' + esc(tr("lgStrong")) +
          '</span><span><i style="background:var(--mark-caution)"></i>' + esc(tr("lgWeak")) + "</span></div></div>";
      }
      if ((d.patterns && d.patterns.length) || (d.reasons && d.reasons.length)) {
        h += '<div class="sec"><h3>' + esc(tr("whyH")) + '</h3><ul class="finds">' + (d.patterns || []).map(function (p) {
          return "<li><b>" + esc(pick(p, "name")) + "</b><span>" + esc(pick(p, "why")) + "</span></li>";
        }).join("");
        var extra = (d.reasons || []).filter(function (r) { return !(d.patterns || []).some(function (p) { return p.why_en === r.en; }); });
        h += extra.map(function (r) { return "<li><span>" + esc(r[lang] || r.en) + "</span></li>"; }).join("") + "</ul></div>";
      }
      var ents = (d.entities || []);
      if (ents.length) {
        h += '<div class="sec"><h3>' + esc(tr("linksH")) + '</h3><div class="ents">' + ents.map(function (e) {
          return '<div class="ent ' + esc(e.verdict) + '"><code>' + esc(e.text) + "</code>" +
            (e["reasons_" + lang] || e.reasons_en || []).map(function (r) { return "<p>" + esc(r) + "</p>"; }).join("") + "</div>";
        }).join("") + "</div></div>";
      }
      h += honestyHtml(hn);
      h += '<div class="sec"><h3>' + esc(tr("doH")) + '</h3><div class="advice">' + esc(d["advice_" + lang] || d.advice_en) + "</div>";
      if (d.risk !== "low") h += '<p class="fine" style="margin-top:10px">' + esc(tr("hotH")) + "</p>" + hotlinesHtml(d.hotlines);
      h += "</div>" + actionsHtml();
      h += '<p class="via">' + esc(d.source === "ai+rules" ? tr("viaAI") : d.source === "offline" ? tr("viaOffline") : tr("viaRules")) +
        (d.ai_error ? " " + esc(tr("aiFail")) : "") + "</p>";
      el.innerHTML = h;
      wireActions(el, function () {
        var why = (d.patterns || []).map(function (p) { return pick(p, "name"); }).join(", ");
        return tr("shareTpl").replace("{v}", tr("s_" + d.risk)).replace("{why}", why ? why + "." : "")
          .replace("{url}", location.origin);
      });
    };
    rerender.pretx = render; render(!fromHistory);
    if (!fromHistory && window.matchMedia("(max-width: 840px)").matches) $("#tOut").scrollIntoView({ behavior: "smooth", block: "start" });
  }
  function countChars() { var n = $("#tText").value.length; $("#tCount").textContent = fmtNum(n) + " / " + fmtNum(4000); }
  $("#tText").addEventListener("input", countChars);
  $("#tText").addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); $("#pretxForm").requestSubmit(); }
  });
  $("#pretxForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var btn = $("#tGo"), text = $("#tText").value.trim();
    if (text.length < 3) { toast(tr("needText")); $("#tText").focus(); return; }
    busy(btn, true);
    var done = function (d) {
      showPretx(d, text);
      addHistory("pretx", { ts: Date.now(), label: text.slice(0, 60), input: text, res: d });
    };
    var local = function () {
      var d = window.ScamEngine.analyze(text, rulesData);
      d.source = "offline";
      d.reasons = d.patterns.map(function (p) { return { en: p.why_en, bn: p.why_bn }; });
      return d;
    };
    var canLocal = !!(rulesData && window.ScamEngine);
    var run = isOffline && canLocal ? Promise.resolve(local()) :
      api("/api/pretx", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: text, lang: lang }) })
        .catch(function (err) {
          if (err.offline && canLocal) { setOffline(true); return local(); }
          throw err;
        });
    run.then(done)
      .catch(function (err) { $("#tOut").innerHTML = '<p class="err">' + esc(err.message) + "</p>"; })
      .then(function () { busy(btn, false); });
  });
  // ------------------------------------- screen check: camera, own screen (live share) or screenshot
  var S = { stream: null, src: "cam", timer: null, last: null, sending: false };
  var canShare = !!(navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) &&
    !/Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
  function camStop() {
    clearInterval(S.timer); S.timer = null; S.last = null;
    if (S.stream) S.stream.getTracks().forEach(function (t) { t.onended = null; t.stop(); });
    S.stream = null; $("#sVideo").srcObject = null;
  }
  function camClose() { camStop(); $("#sPanel").hidden = true; $("#sAuto").checked = false; }
  function srcUI(src, hintKey) {
    S.src = src;
    $$(".src").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.src === src ? "true" : "false"); });
    var live = src !== "file";
    $("#sVideo").hidden = !live; $("#sShot").hidden = !live;
    $("#sAutoRow").hidden = src !== "share";
    $("#sHint").textContent = tr(hintKey || (src === "cam" ? "camHint" : src === "share" ? "shareHint" : "fileHint"));
  }
  function useStream(stream) {
    if ($("#sPanel").hidden) { stream.getTracks().forEach(function (t) { t.stop(); }); return; }
    S.stream = stream; var v = $("#sVideo"); v.srcObject = stream; v.play().catch(function () {});
  }
  function startCam() {
    camStop(); srcUI("cam");
    if (!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)) { srcUI("file", "camNo"); return; }
    navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" }, width: { ideal: 1920 }, height: { ideal: 1080 } }, audio: false })
      .then(useStream, function () { srcUI("file", "camNo"); });
  }
  function startShare() {
    camStop(); srcUI("share");
    if (!canShare) { srcUI("file", "shareNo"); return; }
    navigator.mediaDevices.getDisplayMedia({ video: { frameRate: 5 }, audio: false }).then(function (stream) {
      useStream(stream);
      stream.getVideoTracks()[0].onended = function () { camStop(); srcUI("file", "shareEnded"); };
    }, function () { srcUI("file", "fileHint"); });
  }
  function camOpen() {
    if (aiMode === "rules" || isOffline) { toast(tr("needAI")); return; }
    $("#sPanel").hidden = false;
    $('.src[data-src="share"]').hidden = !canShare;
    startCam();
  }
  // shrink to at most 1600 px so photos stay well under the 4 MB upload limit
  function toJpeg(source, w, h) {
    var k = Math.min(1, 1600 / Math.max(w, h)), c = document.createElement("canvas");
    c.width = Math.round(w * k); c.height = Math.round(h * k);
    c.getContext("2d").drawImage(source, 0, 0, c.width, c.height);
    return new Promise(function (ok) { c.toBlob(ok, "image/jpeg", 0.88); });
  }
  // a tiny grey thumbnail, to notice when the shared screen has changed
  function thumb(v) {
    var c = document.createElement("canvas"); c.width = 32; c.height = 32;
    var g = c.getContext("2d"); g.drawImage(v, 0, 0, 32, 32);
    var px = g.getImageData(0, 0, 32, 32).data, out = new Array(1024);
    for (var i = 0; i < 1024; i++) out[i] = (px[i * 4] + px[i * 4 + 1] + px[i * 4 + 2]) / 3;
    return out;
  }
  function changed(a, b) {
    if (!a || !b) return true;
    var d = 0; for (var i = 0; i < a.length; i++) d += Math.abs(a[i] - b[i]);
    return d / a.length > 4;
  }
  function screenSend(blob, keepOpen) {
    if (!keepOpen) camClose();
    if (!blob || S.sending) return;
    S.sending = true;
    var btn = $("#sStart"); busy(btn, true); busy($("#tGo"), true); busy($("#sShot"), true);
    if (!keepOpen) $("#tOut").innerHTML = '<p class="fine">' + esc(tr("reading")) + "</p>";
    var fd = new FormData(); fd.append("image", blob, "screen.jpg"); fd.append("lang", lang);
    api("/api/screen", { method: "POST", body: fd }).then(function (d) {
      if (d.needs_text) {
        if (keepOpen) { toast(lang === "bn" ? d.error_bn || d.error : d.error); return; }
        $("#tOut").innerHTML = '<p class="err">' + esc(lang === "bn" ? d.error_bn || d.error : d.error) + "</p>";
        $("#tText").focus(); return;
      }
      $("#tText").value = d.text || ""; countChars();
      showPretx(d, d.text || "");
      addHistory("pretx", { ts: Date.now(), label: tr("fromScreen") + ": " + (d.screen.name || d.screen.number || (d.text || "").slice(0, 40)), input: d.text, res: d });
    }).catch(function (err) { if (!keepOpen) $("#tOut").innerHTML = '<p class="err">' + esc(err.message) + "</p>"; else toast(err.message); })
      .then(function () { S.sending = false; busy(btn, false); busy($("#tGo"), false); busy($("#sShot"), false); });
  }
  function grab(keepOpen) {
    var v = $("#sVideo");
    if (!v.videoWidth) { toast(tr("camNo")); return; }
    S.last = thumb(v);
    toJpeg(v, v.videoWidth, v.videoHeight).then(function (b) { screenSend(b, keepOpen); });
  }
  function fileToCheck(f) {
    if (!f || f.type.indexOf("image/") !== 0) return;
    var img = new Image(), url = URL.createObjectURL(f);
    img.onload = function () { URL.revokeObjectURL(url); toJpeg(img, img.naturalWidth, img.naturalHeight).then(function (b) { screenSend(b); }); };
    img.onerror = function () { URL.revokeObjectURL(url); toast(tr("camNo")); };
    img.src = url;
  }
  $("#sStart").addEventListener("click", function () { if ($("#sPanel").hidden) camOpen(); else camClose(); });
  $("#sCancel").addEventListener("click", camClose);
  $$(".src").forEach(function (b) {
    b.addEventListener("click", function () {
      var src = b.dataset.src;
      if (src === "cam") startCam();
      else if (src === "share") startShare();
      else { camStop(); srcUI("file"); $("#sFile").click(); }
    });
  });
  // while sharing the screen live, keep the panel open so the next capture is one click away
  $("#sShot").addEventListener("click", function () { grab(S.src === "share"); });
  $("#sAuto").addEventListener("change", function () {
    clearInterval(S.timer); S.timer = null;
    if (!this.checked) return;
    grab(true);
    S.timer = setInterval(function () {
      var v = $("#sVideo");
      if (!S.stream || !v.videoWidth || S.sending) return;
      if (changed(thumb(v), S.last)) grab(true);
    }, 10000);
  });
  $("#sFile").addEventListener("change", function (e) { var f = e.target.files[0]; e.target.value = ""; fileToCheck(f); });
  // paste a screenshot straight into the Message check
  document.addEventListener("paste", function (e) {
    if ($("#pretx").hidden) return;
    var items = (e.clipboardData || {}).items || [];
    for (var i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image/") === 0) {
        e.preventDefault();
        if (aiMode === "rules" || isOffline) { toast(tr("needAI")); return; }
        fileToCheck(items[i].getAsFile()); return;
      }
    }
  });
  $$(".chip[data-ex]").forEach(function (c) {
    c.addEventListener("click", function () { $("#tText").value = c.dataset.ex; countChars(); $("#tText").focus(); });
  });

  /* ------------------------------------------------------------ voice recorder
   * Record -> Pause/Resume -> Check voice. The recording is converted to a small
   * 16 kHz mono WAV and sent to /api/voice (Gemini speech-to-text). Where that is not
   * available (no Gemini key, offline), the browser's own live speech recognition,
   * which runs alongside the recording, supplies the text instead. */
  var MAX_SEC = 90;
  var V = { state: "idle", rec: null, stream: null, chunks: [], elapsed: 0, tick: null, startedAt: 0,
            sr: null, srFinal: "", srInterim: "", srWanted: false };

  function fmtTime(sec) { var m = Math.floor(sec / 60), x = Math.floor(sec % 60); return fmtNum(m) + ":" + (x < 10 ? (lang === "bn" ? "০" : "0") : "") + fmtNum(x); }
  function liveText() { return (V.srFinal + " " + V.srInterim).replace(/\s+/g, " ").trim(); }
  function elapsedNow() { return V.elapsed + (V.state === "recording" ? (Date.now() - V.startedAt) / 1000 : 0); }

  function voiceRender() {
    var panel = $("#vPanel"), start = $("#vStart");
    start.hidden = V.state !== "idle";
    panel.hidden = V.state === "idle";
    if (V.state === "idle") return;
    panel.classList.toggle("paused", V.state === "paused");
    panel.classList.toggle("busy", V.state === "busy");
    $("#vState").textContent = V.state === "recording" ? tr("recording") : V.state === "paused" ? tr("paused") : tr("transcribing") + "…";
    $("#vTime").textContent = fmtTime(elapsedNow());
    $("#vMax").textContent = V.state === "busy" ? "" : tr("maxNote");
    $("#vText").textContent = liveText();
    $("#vPause").hidden = V.state === "busy";
    $("#vPause").textContent = V.state === "paused" ? tr("resume") : tr("pause");
    $("#vSubmit").disabled = V.state === "busy";
    $("#vSubmit").setAttribute("aria-busy", V.state === "busy" ? "true" : "false");
    $("#vCancel").hidden = V.state === "busy";
  }
  window.__voiceRender = voiceRender;

  function srStart() {
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR || V.sr) return;
    try {
      var r = new SR();
      r.lang = lang === "bn" ? "bn-BD" : "en-US"; r.continuous = true; r.interimResults = true;
      r.onresult = function (e) {
        var interim = "";
        for (var i = e.resultIndex; i < e.results.length; i++) {
          if (e.results[i].isFinal) V.srFinal += " " + e.results[i][0].transcript;
          else interim += " " + e.results[i][0].transcript;
        }
        V.srInterim = interim; voiceRender();
      };
      r.onerror = function () {};
      r.onend = function () { V.sr = null; V.srInterim = ""; if (V.srWanted && V.state === "recording") srStart(); };
      V.sr = r; V.srWanted = true; r.start();
    } catch (e) { V.sr = null; }
  }
  function srStop() { V.srWanted = false; if (V.sr) { try { V.sr.stop(); } catch (e) {} } }

  function startTick() {
    clearInterval(V.tick);
    V.tick = setInterval(function () {
      if (elapsedNow() >= MAX_SEC) { pauseRec(); toast(tr("voiceMax")); }
      voiceRender();
    }, 250);
  }
  function releaseMic() { if (V.stream) V.stream.getTracks().forEach(function (t) { t.stop(); }); V.stream = null; }
  function resetVoice() {
    clearInterval(V.tick); srStop();
    if (V.rec && V.rec.state !== "inactive") { try { V.rec.onstop = null; V.rec.stop(); } catch (e) {} }
    releaseMic();
    V.state = "idle"; V.rec = null; V.chunks = []; V.elapsed = 0; V.srFinal = ""; V.srInterim = "";
    voiceRender();
  }

  function startRec() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || typeof MediaRecorder === "undefined") {
      toast(tr("noRecorder")); return;
    }
    navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } }).then(function (stream) {
      V.stream = stream; V.chunks = []; V.elapsed = 0; V.srFinal = ""; V.srInterim = "";
      V.rec = new MediaRecorder(stream);
      V.rec.ondataavailable = function (e) { if (e.data && e.data.size) V.chunks.push(e.data); };
      V.rec.start(1000);
      V.state = "recording"; V.startedAt = Date.now();
      srStart(); startTick(); voiceRender();
      $("#vPause").focus();
    }, function () { toast(tr("micDenied")); });
  }
  function pauseRec() {
    if (V.state !== "recording") return;
    V.elapsed = elapsedNow(); V.state = "paused";
    try { V.rec.pause(); } catch (e) {}
    srStop(); voiceRender();
  }
  function resumeRec() {
    if (V.state !== "paused" || elapsedNow() >= MAX_SEC) return;
    try { V.rec.resume(); } catch (e) {}
    V.state = "recording"; V.startedAt = Date.now();
    srStart(); voiceRender();
  }

  // decode whatever the browser recorded and re-encode as 16 kHz mono 16-bit WAV
  function toWav(blob) {
    var AC = window.AudioContext || window.webkitAudioContext, OAC = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if (!AC || !OAC) return Promise.reject(new Error("no audio api"));
    return blob.arrayBuffer().then(function (buf) {
      var ac = new AC();
      return new Promise(function (ok, bad) { ac.decodeAudioData(buf, ok, bad); }).then(function (decoded) {
        try { ac.close(); } catch (e) {}
        var rate = 16000, len = Math.max(1, Math.ceil(decoded.duration * rate));
        var off = new OAC(1, len, rate), src = off.createBufferSource();
        src.buffer = decoded; src.connect(off.destination); src.start(0);
        return off.startRendering();
      });
    }).then(function (rendered) {
      var pcm = rendered.getChannelData(0), n = pcm.length, out = new DataView(new ArrayBuffer(44 + n * 2));
      var w = function (o, str) { for (var i = 0; i < str.length; i++) out.setUint8(o + i, str.charCodeAt(i)); };
      w(0, "RIFF"); out.setUint32(4, 36 + n * 2, true); w(8, "WAVE"); w(12, "fmt ");
      out.setUint32(16, 16, true); out.setUint16(20, 1, true); out.setUint16(22, 1, true);
      out.setUint32(24, 16000, true); out.setUint32(28, 32000, true); out.setUint16(32, 2, true); out.setUint16(34, 16, true);
      w(36, "data"); out.setUint32(40, n * 2, true);
      for (var i = 0; i < n; i++) { var v = Math.max(-1, Math.min(1, pcm[i])); out.setInt16(44 + i * 2, v < 0 ? v * 0x8000 : v * 0x7FFF, true); }
      return new Blob([out], { type: "audio/wav" });
    });
  }

  function useTranscript(text, note) {
    text = (text || "").trim();
    if (!text) { toast(tr("noSpeech")); resetVoice(); return; }
    var box = $("#tText");
    box.value = (box.value.trim() ? box.value.trim() + " " : "") + text;
    countChars(); resetVoice();
    if (note) toast(note);
    $("#pretxForm").requestSubmit();
  }

  function submitRec() {
    if (V.state !== "recording" && V.state !== "paused") return;
    V.elapsed = elapsedNow(); clearInterval(V.tick); srStop();
    V.state = "busy"; voiceRender();
    var rec = V.rec;
    var stopped = new Promise(function (ok) {
      if (!rec || rec.state === "inactive") { ok(); return; }
      rec.onstop = function () { ok(); };
      try { rec.stop(); } catch (e) { ok(); }
    });
    stopped.then(function () {
      releaseMic();
      // give the speech recogniser a moment to deliver its last words
      return new Promise(function (ok) { setTimeout(ok, 400); });
    }).then(function () {
      var live = liveText();
      if (!voiceAI || isOffline || !V.chunks.length) { useTranscript(live); return; }
      var blob = new Blob(V.chunks, { type: (rec && rec.mimeType) || "audio/webm" });
      return toWav(blob).catch(function () { return blob; }).then(function (audio) {
        var fd = new FormData();
        fd.append("audio", audio, audio.type === "audio/wav" ? "voice.wav" : "voice.webm");
        fd.append("lang", lang);
        return api("/api/voice", { method: "POST", body: fd });
      }).then(function (d) { useTranscript(d.transcript || live); },
        function () { useTranscript(live, live ? tr("voiceFallback") : null); });
    });
  }

  $("#vStart").addEventListener("click", startRec);
  $("#vPause").addEventListener("click", function () { if (V.state === "recording") pauseRec(); else resumeRec(); });
  $("#vSubmit").addEventListener("click", submitRec);
  $("#vCancel").addEventListener("click", resetVoice);
  document.addEventListener("keydown", function (e) {
    if (V.state === "idle" || V.state === "busy") return;
    if (e.key === "Escape") resetVoice();
  });

  /* ------------------------------------------------------------ payment proof */
  var pFile = null;
  function setFile(f) {
    if (!f) return;
    if (["image/png", "image/jpeg", "image/webp"].indexOf(f.type) < 0) { toast(tr("badType")); return; }
    if (f.size > 4 * 1024 * 1024) { toast(tr("tooBig")); return; }
    pFile = f;
    $("#pPreview").src = URL.createObjectURL(f);
    $("#pName").textContent = (f.name || "screenshot") + " (" + Math.round(f.size / 1024) + " KB)";
    $(".drop-empty").hidden = true; $(".drop-full").hidden = false;
  }
  function clearFile() {
    pFile = null; $("#pImage").value = ""; $(".drop-empty").hidden = false; $(".drop-full").hidden = true;
  }
  var drop = $("#drop");
  drop.addEventListener("click", function (e) { if (!e.target.closest("#pRemove")) $("#pImage").click(); });
  drop.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); $("#pImage").click(); } });
  $("#pImage").addEventListener("change", function (e) { setFile(e.target.files[0]); });
  $("#pRemove").addEventListener("click", function (e) { e.stopPropagation(); clearFile(); });
  ["dragenter", "dragover"].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add("over"); }); });
  ["dragleave", "drop"].forEach(function (ev) { drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove("over"); }); });
  drop.addEventListener("drop", function (e) { setFile(e.dataTransfer.files[0]); });
  document.addEventListener("paste", function (e) {
    if ($("#proof").hidden) return;
    var items = (e.clipboardData || {}).items || [];
    for (var i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image/") === 0) { setFile(items[i].getAsFile()); e.preventDefault(); return; }
    }
  });

  var ICON = { ok: "✓", warn: "!", fail: "✕", info: "i" };
  function showProof(d, fromHistory) {
    var render = function (animate) {
      var el = $("#pOut");
      if (d.needs_manual) {
        var ic = (d.checks || []).filter(function (c) { return c.status !== "info"; });
        el.innerHTML = '<div class="slip-empty"><div>' + EMPTY_ICON + '<p class="err">' + esc(d["error_" + lang] || d.error || tr("needInput")) + "</p></div></div>" +
          (ic.length ? '<div class="sec"><h3>' + esc(tr("checksH")) + "</h3>" + ic.map(function (c) {
            return '<div class="check ' + esc(c.status) + '"><span class="ic" aria-hidden="true">' + (ICON[c.status] || "•") +
              "</span><span>" + esc(c[lang] || c.en) + "</span></div>";
          }).join("") + "</div>" : "");
        if (!fromHistory && d.image) { var man = $(".manual"); man.open = true; setTimeout(function () { $("#mAmount").focus(); }, 50); }
        return;
      }
      var h = head(d.verdict, d.score || 0, null, animate, d.verdict === "consistent" && d.compared === false ? "clean" : null);
      h += '<div class="sec"><h3>' + esc(tr("checksH")) + "</h3>" + (d.checks || []).map(function (c) {
        return '<div class="check ' + esc(c.status) + '"><span class="ic" aria-hidden="true">' + (ICON[c.status] || "•") +
          "</span><span>" + esc(c[lang] || c.en) + "</span></div>";
      }).join("") + "</div>";
      h += honestyHtml(d.honesty);
      var fl = d.fields || {}, keys = ["amount", "trx_id", "recipient", "sender", "datetime", "provider"].filter(function (k) { return fl[k] != null && fl[k] !== ""; });
      if (keys.length) {
        h += '<div class="sec"><h3>' + esc(tr("readH")) + '</h3><dl class="fields">' + keys.map(function (k) {
          return "<dt>" + esc(tr("f_" + k)) + "</dt><dd>" + esc(k === "amount" ? fmtNum(fl[k]) : fl[k]) + "</dd>";
        }).join("") + "</dl></div>";
      }
      if (d.image) {
        h += '<div class="sec"><h3>' + esc(tr("imgH")) + '</h3><dl class="fields"><dt>' + esc(tr("i_format")) + "</dt><dd>" + esc(d.image.format) +
          "</dd><dt>" + esc(tr("i_size")) + "</dt><dd>" + esc(d.image.width + " × " + d.image.height) + "</dd>" +
          (d.image.editor ? "<dt>" + esc(tr("i_editor")) + "</dt><dd>" + esc(d.image.editor) + "</dd>" : "") + "</dl></div>";
      }
      if (d.extract_error) h += '<p class="fine sec">' + esc(d["extract_error_" + lang] || d.extract_error) + "</p>";
      h += '<p class="reminder">' + esc(d["reminder_" + lang] || d.reminder_en || "") + "</p>" + actionsHtml();
      el.innerHTML = h;
      wireActions(el, function () {
        var bad = (d.checks || []).filter(function (c) { return c.status === "fail"; }).map(function (c) { return c[lang] || c.en; }).join(" ");
        var lab = d.verdict === "consistent" && d.compared === false ? "clean" : d.verdict;
        return tr("shareTpl").replace("{v}", tr("s_" + lab)).replace("{why}", bad).replace("{url}", location.origin);
      });
    };
    rerender.proof = render; render(!fromHistory);
    if (!fromHistory && window.matchMedia("(max-width: 840px)").matches) $("#pOut").scrollIntoView({ behavior: "smooth", block: "start" });
  }
  // the buyer's number is optional; if given it must be a Bangladeshi mobile number (01XXXXXXXXX or +8801XXXXXXXXX, Bangla digits allowed)
  function bdMobile(v) {
    var d = String(v || "").replace(/[০-৯]/g, function (x) { return "০১২৩৪৫৬৭৮৯".indexOf(x); }).replace(/\D/g, "");
    if (d.indexOf("880") === 0) d = d.slice(2);
    return /^01[3-9]\d{8}$/.test(d) ? d : null;
  }
  function buyerError(key) {
    var input = $("#pBuyer"), err = $("#pBuyerErr");
    if (!key) { input.removeAttribute("aria-invalid"); err.hidden = true; err.textContent = ""; err.removeAttribute("data-k"); return; }
    input.setAttribute("aria-invalid", "true"); err.hidden = false; err.textContent = tr(key); err.setAttribute("data-k", key);
  }
  $("#pBuyer").addEventListener("input", function () { if ($("#pBuyer").getAttribute("aria-invalid")) buyerError(null); });
  $("#proofForm").addEventListener("submit", function (e) {
    e.preventDefault();
    var buyerRaw = $("#pBuyer").value.trim();
    if (buyerRaw && !bdMobile(buyerRaw)) { buyerError("buyerInvalid"); $("#pBuyer").focus(); return; }
    buyerError(null);
    var manual = { amount: $("#mAmount").value, trx_id: $("#mTrx").value, recipient: $("#mRecipient").value, sender: $("#mSender").value, datetime: $("#mTime").value };
    var hasManual = Object.keys(manual).some(function (k) { return manual[k]; });
    if (!pFile && !hasManual) { toast(tr("needInput")); return; }
    var fd = new FormData();
    if (pFile) fd.append("image", pFile, pFile.name || "screenshot.png");
    fd.append("expected_amount", $("#pAmount").value);
    fd.append("expected_recipient", $("#pRecipient").value);
    fd.append("expected_sender", bdMobile($("#pBuyer").value) || "");
    fd.append("chat_time", $("#pChat").value);
    fd.append("order_ref", $("#pOrder").value);
    fd.append("manual", JSON.stringify(manual));
    if (isOffline) { $("#pOut").innerHTML = '<div class="slip-empty"><div>' + EMPTY_ICON + "<p>" + esc(tr("proofOffline")) + "</p></div></div>"; return; }
    var btn = $("#pGo"); busy(btn, true);
    api("/api/proof", { method: "POST", body: fd })
      .then(function (d) {
        showProof(d);
        if (!d.needs_manual) {
          var label = ($("#pOrder").value || "") + " " + (d.fields && d.fields.amount != null ? "Tk " + d.fields.amount : "");
          addHistory("proof", { ts: Date.now(), label: label.trim() || (d.fields && d.fields.trx_id) || "Payment", res: d });
        }
      })
      .catch(function (err) { $("#pOut").innerHTML = '<p class="err">' + esc(err.message) + "</p>"; })
      .then(function () { busy(btn, false); });
  });

  /* ------------------------------------------------------------ clear buttons */
  $("#pClear").addEventListener("click", function () {
    clearFile();
    ["#pAmount", "#pRecipient", "#pBuyer", "#pChat", "#pOrder", "#mAmount", "#mTrx", "#mRecipient", "#mSender", "#mTime"].forEach(function (id) { $(id).value = ""; });
    $(".manual").open = false; buyerError(null);
    delete rerender.proof; empty($("#pOut"), "emptyP");
    toast(tr("cleared")); $("#drop").focus();
  });
  $("#tClear").addEventListener("click", function () {
    if (V.state !== "idle") resetVoice();
    camClose();
    $("#tText").value = ""; countChars();
    delete rerender.pretx; empty($("#tOut"), "emptyT");
    toast(tr("cleared")); $("#tText").focus();
  });

  /* ------------------------------------------------------------ trainer */
  function renderTrainerHome() {
    var home = $("#trHome");
    if (!scenarios.length) { home.innerHTML = ""; return; }
    var h = '<div class="scenarios">' + scenarios.map(function (s, i) {
      return '<div class="scen"><div><h3>' + esc(pick(s, "title")) + "</h3><p>" + esc(pick(s, "intro")) +
        '</p></div><button type="button" class="primary" data-i="' + i + '">' + esc(tr("start")) + "</button></div>";
    }).join("") + "</div>";
    if (aiMode !== "rules") {
      h += '<div class="free play"><h3>' + esc(tr("freeH")) + '</h3><p class="fine" style="margin-top:4px">' + esc(tr("freeP")) +
        '</p><button type="button" class="ghost" id="freeBtn" style="margin-top:12px">' + esc(tr("freeStart")) + "</button></div>";
    }
    home.innerHTML = h;
    $$("button[data-i]", home).forEach(function (b) { b.addEventListener("click", function () { startScript(scenarios[+b.dataset.i]); }); });
    var fb = $("#freeBtn"); if (fb) fb.addEventListener("click", startFree);
  }
  function showPlay(html) { $("#trHome").hidden = true; var p = $("#trPlay"); p.hidden = false; p.innerHTML = html; p.scrollIntoView({ block: "start" }); return p; }
  function backHome() { $("#trPlay").hidden = true; $("#trHome").hidden = false; delete rerender.trainer; }
  function progress(i, n) { var s = ""; for (var k = 0; k < n; k++) s += "<i" + (k < i ? ' class="done"' : "") + "></i>"; return '<div class="progress">' + s + "</div>"; }

  function startScript(sc) {
    var i = 0, total = 0, max = sc.steps.length * 2;
    function step() {
      var s = sc.steps[i];
      rerender.trainer = function () {
        var h = '<div class="play"><h3>' + esc(pick(sc, "title")) + "</h3>" + progress(i, sc.steps.length) +
          '<p class="fine">' + esc(tr("step")) + " " + fmtNum(i + 1) + " " + esc(tr("of")) + " " + fmtNum(sc.steps.length) + "</p>" +
          '<div class="bubble"><small>' + esc(tr("scammer")) + "</small>" + esc(pick(s, "scammer")) + "</div>" +
          s.choices.map(function (c, k) { return '<button type="button" class="choice" data-k="' + k + '">' + esc(c[lang] || c.en) + "</button>"; }).join("") + "</div>";
        var p = showPlay(h);
        $$(".choice", p).forEach(function (b) { b.addEventListener("click", function () { answer(s.choices[+b.dataset.k]); }); });
      };
      rerender.trainer();
    }
    function answer(c) {
      total += c.score;
      rerender.trainer = function () {
        var last = i === sc.steps.length - 1;
        var h = '<div class="play"><h3>' + esc(pick(sc, "title")) + "</h3>" + progress(i + 1, sc.steps.length) +
          '<div class="bubble"><small>' + esc(tr("scammer")) + "</small>" + esc(pick(sc.steps[i], "scammer")) + "</div>" +
          '<div class="bubble me"><small>' + esc(tr("you")) + "</small>" + esc(c[lang] || c.en) + "</div>" +
          '<div class="fb s' + c.score + '">' + esc(c["fb_" + lang] || c.fb_en) + "</div>" +
          '<button type="button" class="primary" id="nx">' + esc(last ? tr("seeResult") : tr("nextStep")) + "</button></div>";
        var p = showPlay(h);
        $("#nx", p).addEventListener("click", function () { if (last) finish(); else { i++; step(); } });
        $("#nx", p).focus();
      };
      rerender.trainer();
    }
    function finish() {
      rerender.trainer = function () {
        var pct = Math.round(100 * total / max), kind = pct >= 80 ? "low" : pct >= 50 ? "medium" : "high";
        var msg = pct >= 80 ? tr("excellent") : pct >= 50 ? tr("okay") : tr("weak");
        var h = '<div class="play"><div class="slip-head"><div><h2 style="margin:0">' + esc(tr("scoreH")) + ": " + fmtNum(total) + " / " + fmtNum(max) +
          '</h2><p class="fine">' + esc(msg) + '</p></div><span class="stamp land t-' + kind + '">' + fmtNum(pct) + "%</span></div>" +
          '<div class="sec"><h3>' + esc(tr("flagsH")) + '</h3><ul class="plain">' + (sc["red_flags_" + lang] || sc.red_flags_en).map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul></div>" +
          '<div class="sec"><h3>' + esc(tr("safeH")) + '</h3><div class="advice">' + esc(pick(sc, "safe")) + "</div></div>" +
          '<button type="button" class="primary" id="bk">' + esc(tr("again")) + "</button></div>";
        var p = showPlay(h); $("#bk", p).addEventListener("click", backHome);
      };
      rerender.trainer();
    }
    step();
  }

  function startFree() {
    var history = [];
    var opts = scenarios.map(function (s) { return '<option value="' + esc(s.id) + '">' + esc(pick(s, "title")) + "</option>"; }).join("");
    var p = showPlay('<div class="play"><h3>' + esc(tr("freeH")) + '</h3><label style="margin-top:10px"><select id="fsel">' + opts + "</select></label>" +
      '<div id="log" class="chatlog" aria-live="polite"></div><form id="fform"><label><textarea id="fin" rows="2" style="min-height:70px" placeholder="' + esc(tr("typeReply")) + '"></textarea></label>' +
      '<div class="actions"><button class="primary" style="width:auto;margin:0" type="submit">' + esc(tr("send")) + '</button><button type="button" class="ghost" id="fend">' + esc(tr("end")) +
      '</button><button type="button" class="ghost" id="fbk">' + esc(tr("again")) + '</button></div></form><div id="fres"></div></div>');
    function log() {
      $("#log", p).innerHTML = history.map(function (m) {
        return '<div class="bubble' + (m.role === "player" ? " me" : "") + '"><small>' + esc(m.role === "player" ? tr("you") : tr("scammer")) + "</small>" + esc(m.text) + "</div>";
      }).join("");
      var lg = $("#log", p); lg.scrollTop = lg.scrollHeight;
    }
    function turn() {
      return api("/api/trainer/chat", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: $("#fsel", p).value, history: history, lang: lang }) })
        .then(function (d) { history.push({ role: "scammer", text: d.text }); log(); })
        .catch(function (e) { $("#fres", p).innerHTML = '<p class="err">' + esc(e.message) + "</p>"; });
    }
    $("#fsel", p).addEventListener("change", function () { history = []; log(); $("#fres", p).innerHTML = ""; turn(); });
    $("#fform", p).addEventListener("submit", function (e) {
      e.preventDefault();
      var v = $("#fin", p).value.trim(); if (!v) return;
      history.push({ role: "player", text: v }); $("#fin", p).value = ""; log(); turn();
    });
    $("#fin", p).addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("#fform", p).requestSubmit(); } });
    $("#fend", p).addEventListener("click", function () {
      $("#fres", p).innerHTML = '<p class="fine">' + esc(tr("grading")) + "…</p>";
      api("/api/trainer/grade", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: $("#fsel", p).value, history: history, lang: lang }) })
        .then(function (g) {
          var li = function (a) { return (a || []).map(function (x) { return "<li>" + esc(x) + "</li>"; }).join(""); };
          $("#fres", p).innerHTML = '<div class="sec"><h3>' + esc(tr("scoreH")) + ": " + esc(g.score) + "/100</h3><h3>" + esc(tr("caught")) +
            '</h3><ul class="plain">' + li(g.caught) + "</ul><h3>" + esc(tr("missed")) + '</h3><ul class="plain">' + li(g.missed) +
            "</ul><h3>" + esc(tr("tip")) + '</h3><div class="advice">' + esc(g["tip_" + lang] || g.tip_en) + "</div></div>";
        })
        .catch(function (e) { $("#fres", p).innerHTML = '<p class="err">' + esc(e.message) + "</p>"; });
    });
    $("#fbk", p).addEventListener("click", backHome);
    turn();
  }

  /* ------------------------------------------------------------ how it works */
  function pct(x) { return x == null ? "–" : fmtNum(Math.round(x * 100)) + "%"; }
  function renderHow() {
    if (metrics && metrics.dev) {
      var row = function (k) {
        var m = metrics[k];
        var name = (T[lang]["m_" + k] || T.en["m_" + k]) ? tr("m_" + k) : k;
        return "<tr><td>" + esc(name) + '</td><td class="n">' + fmtNum(m.tp) + " / " + fmtNum(m.scam) + " (" + pct(m.recall) + ')</td><td class="n">' +
          fmtNum(m.fp) + " / " + fmtNum(m.genuine) + " (" + pct(m.false_alarm_rate) + ")</td></tr>";
      };
      $("#metrics").innerHTML = "<table><thead><tr><th>" + esc(tr("m_set")) + "</th><th>" + esc(tr("m_caught")) + "</th><th>" + esc(tr("m_false")) +
        "</th></tr></thead><tbody>" + (metrics.splits || ["dev", "holdout"]).map(row).join("") + '</tbody></table><p class="fine" style="margin-top:8px">' + esc(tr("m_note")) + "</p>";
    }
    if (meta && meta.patterns) {
      $("#library").innerHTML = "<table><thead><tr><th>" + esc(tr("libName")) + "</th><th>" + esc(tr("libWhy")) + "</th><th>" + esc(tr("libWeight")) +
        "</th></tr></thead><tbody>" + meta.patterns.slice().sort(function (a, b) { return b.weight - a.weight; }).map(function (p) {
          return "<tr><td>" + esc(pick(p, "name")) + "</td><td>" + esc(pick(p, "why")) + '</td><td class="w">' + fmtNum(p.weight) + "</td></tr>";
        }).join("") + '</tbody></table><p class="fine" style="padding:10px 8px">' + esc(tr("linkChecks")) + "</p>";
    }
  }

  /* ------------------------------------------------------------ boot */
  showTab(location.hash.slice(1) || "proof");
  empty($("#tOut"), "emptyT"); empty($("#pOut"), "emptyP");
  rerender.emptyT = function () { if (!rerender.pretx) empty($("#tOut"), "emptyT"); };
  rerender.emptyP = function () { if (!rerender.proof) empty($("#pOut"), "emptyP"); };
  countChars();
  applyLang();
  function setOffline(v) { if (isOffline !== v) { isOffline = v; applyLang(); } }
  window.addEventListener("online", function () { setOffline(false); });
  window.addEventListener("offline", function () { setOffline(true); });
  if ("serviceWorker" in navigator && location.protocol !== "file:") {
    window.addEventListener("load", function () { navigator.serviceWorker.register("/sw.js").catch(function () {}); });
  }
  Promise.all([
    api("/api/status").then(function (s) { aiMode = s.ai; voiceAI = !!s.voice; setOffline(false); }).catch(function (e) { if (e.offline) isOffline = true; }),
    api("/api/rules").then(function (r) { rulesData = r; store.set("rules", r); }).catch(function () {}),
    api("/api/trainer/scenarios").then(function (s) { scenarios = s; store.set("scenarios", s); }).catch(function () {}),
    api("/api/meta").then(function (m) { meta = m; }).catch(function () {}),
    api("/api/metrics").then(function (m) { metrics = m; }).catch(function () {})
  ]).then(applyLang);
})();
