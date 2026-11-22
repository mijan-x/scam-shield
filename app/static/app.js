(function () {
  "use strict";
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };

  var T = {
    en: {
      title: "Mobile Money Scam Shield", subtitle: "Check a payment or a message before you act.",
      tabProof: "Payment Proof Check", tabPretx: "Check Before You Pay", tabTrainer: "Scam Trainer",
      proofHint: "For sellers: upload the buyer's payment screenshot and tell us what you expected. We compare the two. The final check is always your own bKash or Nagad app.",
      shot: "Payment screenshot", expAmount: "Expected amount (Tk)", expRecipient: "Your number",
      chatTime: "Time buyer said they paid", orderRef: "Order reference",
      manual: "Enter details by hand (if no screenshot or AI is off)",
      mAmount: "Amount in screenshot", mTrx: "Transaction ID", mRecipient: "Recipient number", mTime: "Time in screenshot",
      check: "Check", checking: "Checking…",
      pretxHint: "Paste the message, or describe what the caller is asking. Works with Bangla, English and Banglish.",
      msgLabel: "Message or situation", msgPh: "Example: someone says they sent money by mistake and wants it back",
      mic: "🎤 Speak", micStop: "⏹ Stop", tryEx: "Try an example:",
      footer: "This tool gives warnings, not guarantees. It never sees your PIN or OTP, and never says a payment is \"safe\". Built by JU_Segfault for CoU AI Hackathon 2026.",
      riskhigh: "High risk", riskmedium: "Be careful", risklow: "No known scam pattern found",
      vcons: "Looks consistent", vsusp: "Suspicious", vfake: "Likely fake",
      why: "Why", next: "What to do", pats: "Matches", checksH: "Checks", read: "Read from the screenshot",
      flags: "Signs the image may be edited", viaAI: "Checked by rules and AI", viaRules: "Checked by rules",
      needInput: "Upload a screenshot or enter the details by hand.",
      aiOn: "AI on", aiMock: "AI demo mode", aiOff: "Rules mode",
      trHome: "Pick a scam to practise against. Nothing here is real; no one is calling you.",
      start: "Start", step: "Step", of: "of", feedback: "Feedback", nextStep: "Next", seeResult: "See result",
      scoreH: "Your result", flagsH: "Red flags in this scam", safeH: "What to do in real life", again: "Back to scenarios",
      freeChat: "Free chat (AI plays the scammer)", send: "Send", end: "End and grade", you: "You", scammer: "Scammer",
      typeReply: "Type your reply…", grading: "Grading…", caught: "You handled well", missed: "You missed", tip: "Tip",
      noMic: "Voice input is not supported in this browser.", close: "Reminder",
      excellent: "Strong. You spotted the traps.", okay: "Mixed. Replay and try the safer choices.", weak: "Risky. Read the red flags and try again."
    },
    bn: {
      title: "মোবাইল মানি স্ক্যাম শিল্ড", subtitle: "টাকা পাঠানোর বা কিছু করার আগে যাচাই করুন।",
      tabProof: "পেমেন্ট প্রুফ চেক", tabPretx: "পাঠানোর আগে যাচাই", tabTrainer: "স্ক্যাম ট্রেনার",
      proofHint: "বিক্রেতাদের জন্য: ক্রেতার পেমেন্ট স্ক্রিনশট দিন এবং কী আশা করেছিলেন লিখুন। আমরা দুটো মিলিয়ে দেখব। চূড়ান্ত যাচাই সবসময় আপনার নিজের বিকাশ বা নগদ অ্যাপে।",
      shot: "পেমেন্টের স্ক্রিনশট", expAmount: "প্রত্যাশিত টাকা", expRecipient: "আপনার নম্বর",
      chatTime: "ক্রেতা কখন পেমেন্ট করেছেন বলেছেন", orderRef: "অর্ডার রেফারেন্স",
      manual: "হাতে লিখুন (স্ক্রিনশট না থাকলে বা এআই বন্ধ থাকলে)",
      mAmount: "স্ক্রিনশটে টাকার পরিমাণ", mTrx: "লেনদেন আইডি", mRecipient: "প্রাপকের নম্বর", mTime: "স্ক্রিনশটে সময়",
      check: "যাচাই করুন", checking: "যাচাই হচ্ছে…",
      pretxHint: "মেসেজটি পেস্ট করুন, অথবা কলকারী কী চাইছে লিখুন। বাংলা, ইংরেজি ও ইংরেজি হরফে বাংলা চলবে।",
      msgLabel: "মেসেজ বা ঘটনা", msgPh: "যেমন: কেউ বলছে ভুল করে টাকা পাঠিয়েছে, ফেরত চায়",
      mic: "🎤 বলুন", micStop: "⏹ থামুন", tryEx: "উদাহরণ দেখুন:",
      footer: "এই টুল সতর্কতা দেয়, নিশ্চয়তা নয়। এটি আপনার পিন বা ওটিপি দেখে না এবং কোনো পেমেন্টকে \"নিরাপদ\" বলে না। জেইউ_সেগফল্ট, সিওইউ এআই হ্যাকাথন ২০২৬।",
      riskhigh: "উচ্চ ঝুঁকি", riskmedium: "সতর্ক থাকুন", risklow: "পরিচিত কোনো প্রতারণার ধরন পাওয়া যায়নি",
      vcons: "সঙ্গতিপূর্ণ মনে হচ্ছে", vsusp: "সন্দেহজনক", vfake: "ভুয়া হওয়ার সম্ভাবনা বেশি",
      why: "কেন", next: "কী করবেন", pats: "মিলেছে", checksH: "যাচাইয়ের ফল", read: "স্ক্রিনশট থেকে পড়া তথ্য",
      flags: "ছবি এডিট করার সম্ভাব্য চিহ্ন", viaAI: "নিয়ম ও এআই দিয়ে যাচাই", viaRules: "নিয়ম দিয়ে যাচাই",
      needInput: "স্ক্রিনশট দিন অথবা হাতে তথ্য লিখুন।",
      aiOn: "এআই চালু", aiMock: "এআই ডেমো", aiOff: "নিয়মভিত্তিক মোড",
      trHome: "কোন প্রতারণার বিরুদ্ধে অনুশীলন করবেন বেছে নিন। এখানে সবকিছু নকল; কেউ আপনাকে ফোন করছে না।",
      start: "শুরু", step: "ধাপ", of: "/", feedback: "প্রতিক্রিয়া", nextStep: "পরের ধাপ", seeResult: "ফল দেখুন",
      scoreH: "আপনার ফল", flagsH: "এই প্রতারণার লাল সংকেত", safeH: "বাস্তবে কী করবেন", again: "সব দৃশ্যে ফিরুন",
      freeChat: "ফ্রি চ্যাট (এআই প্রতারক সাজবে)", send: "পাঠান", end: "শেষ করে মূল্যায়ন", you: "আপনি", scammer: "প্রতারক",
      typeReply: "উত্তর লিখুন…", grading: "মূল্যায়ন হচ্ছে…", caught: "যা ভালো করেছেন", missed: "যা মিস করেছেন", tip: "পরামর্শ",
      noMic: "এই ব্রাউজারে ভয়েস ইনপুট চলে না।", close: "মনে রাখুন",
      excellent: "চমৎকার। ফাঁদগুলো ধরতে পেরেছেন।", okay: "মিশ্র ফল। আবার খেলে নিরাপদ বিকল্পগুলো বেছে দেখুন।", weak: "ঝুঁকিপূর্ণ। লাল সংকেতগুলো পড়ে আবার চেষ্টা করুন।"
    }
  };

  var lang = (function () { try { return localStorage.getItem("lang") || "en"; } catch (e) { return "en"; } })();
  var aiMode = "rules";
  var scenarios = [];
  var lastRender = {};
  var tr = function (k) { return T[lang][k] || T.en[k] || k; };
  var pick = function (o, base) { return o[base + "_" + lang] || o[base + "_en"] || ""; };

  function applyLang() {
    document.documentElement.lang = lang;
    $("#langBtn").textContent = lang === "en" ? "বাংলা" : "English";
    $$("[data-t]").forEach(function (el) { el.textContent = tr(el.getAttribute("data-t")); });
    $$("[data-tp]").forEach(function (el) { el.placeholder = tr(el.getAttribute("data-tp")); });
    var mic = $("#tMic"); if (mic && !mic.classList.contains("rec")) mic.textContent = tr("mic");
    var b = $("#aiBadge");
    b.textContent = aiMode === "live" ? tr("aiOn") : aiMode === "mock" ? tr("aiMock") : tr("aiOff");
    b.className = "badge" + (aiMode === "live" ? " live" : "");
    Object.keys(lastRender).forEach(function (k) { lastRender[k](); });
    renderTrainerHome();
  }

  // ----- tabs
  $$(".tab").forEach(function (b) {
    b.addEventListener("click", function () {
      $$(".tab").forEach(function (x) { x.classList.toggle("on", x === b); });
      $$(".panel").forEach(function (p) { p.classList.toggle("on", p.id === b.dataset.tab); });
    });
  });
  $("#langBtn").addEventListener("click", function () {
    lang = lang === "en" ? "bn" : "en";
    try { localStorage.setItem("lang", lang); } catch (e) {}
    applyLang();
  });

  function api(path, opts) {
    return fetch(path, opts).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) throw new Error(j.detail || ("HTTP " + r.status));
        return j;
      });
    });
  }

  // ----- Pre-transaction check
  var riskLabel = function (r) { return tr("risk" + r); };
  function renderPretx(d) {
    var h = '<div class="res"><span class="verdict ' + esc(d.risk) + '">' + esc(riskLabel(d.risk)) + "</span>";
    if (d.patterns && d.patterns.length) {
      h += "<h3>" + tr("pats") + "</h3><ul>" + d.patterns.map(function (p) { return "<li>" + esc(pick(p, "name")) + "</li>"; }).join("") + "</ul>";
    }
    if (d.reasons && d.reasons.length) {
      h += "<h3>" + tr("why") + "</h3><ul>" + d.reasons.map(function (r) { return "<li>" + esc(r[lang] || r.en) + "</li>"; }).join("") + "</ul>";
    }
    h += "<h3>" + tr("next") + "</h3><p>" + esc(d["advice_" + lang] || d.advice_en) + "</p>";
    h += '<p class="note">' + (d.source === "ai+rules" ? tr("viaAI") : tr("viaRules")) + "</p></div>";
    $("#tOut").innerHTML = h;
  }
  $("#tGo").addEventListener("click", function () {
    var btn = $("#tGo"), text = $("#tText").value.trim();
    if (!text) return;
    btn.disabled = true; $("#tOut").innerHTML = '<p class="spin">' + tr("checking") + "</p>";
    api("/api/pretx", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: text, lang: lang }) })
      .then(function (d) { lastRender.pretx = function () { renderPretx(d); }; renderPretx(d); })
      .catch(function (e) { $("#tOut").innerHTML = '<p class="err">' + esc(e.message) + "</p>"; })
      .then(function () { btn.disabled = false; });
  });
  $$(".chip[data-ex]").forEach(function (c) { c.addEventListener("click", function () { $("#tText").value = c.dataset.ex; }); });

  // voice input (Web Speech API; needs Chrome/Edge and internet)
  var rec = null;
  $("#tMic").addEventListener("click", function () {
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition, btn = $("#tMic");
    if (!SR) { alert(tr("noMic")); return; }
    if (rec) { rec.stop(); return; }
    rec = new SR(); rec.lang = lang === "bn" ? "bn-BD" : "en-US"; rec.interimResults = false;
    rec.onresult = function (e) {
      var t = Array.prototype.map.call(e.results, function (r) { return r[0].transcript; }).join(" ");
      var box = $("#tText"); box.value = (box.value ? box.value + " " : "") + t;
    };
    rec.onend = function () { rec = null; btn.classList.remove("rec"); btn.textContent = tr("mic"); };
    rec.onerror = function () { rec = null; btn.classList.remove("rec"); btn.textContent = tr("mic"); };
    btn.classList.add("rec"); btn.textContent = tr("micStop"); rec.start();
  });

  // ----- Proof check
  $("#pImage").addEventListener("change", function (e) {
    var f = e.target.files[0], im = $("#pPreview");
    if (!f) { im.hidden = true; return; }
    im.src = URL.createObjectURL(f); im.hidden = false;
  });
  var verdictLabel = { consistent: "vcons", suspicious: "vsusp", likely_fake: "vfake" };
  var ICON = { ok: "✓", warn: "!", fail: "✗" };
  function renderProof(d) {
    if (d.needs_manual) {
      $("#pOut").innerHTML = '<div class="res"><p class="err">' + esc(d.error || tr("needInput")) + "</p></div>";
      return;
    }
    var h = '<div class="res"><span class="verdict ' + esc(d.verdict) + '">' + esc(tr(verdictLabel[d.verdict] || "vsusp")) + "</span>";
    h += "<h3>" + tr("checksH") + "</h3>" + (d.checks || []).map(function (c) {
      return '<div class="chk ' + esc(c.status) + '"><b>' + (ICON[c.status] || "•") + "</b><span>" + esc(c[lang] || c.en) + "</span></div>";
    }).join("");
    if (d.visual_flags && d.visual_flags.length) {
      h += "<h3>" + tr("flags") + "</h3><ul>" + d.visual_flags.map(function (f) {
        return "<li>" + esc(typeof f === "string" ? f : (f[lang] || f.en || f.text || JSON.stringify(f))) + "</li>";
      }).join("") + "</ul>";
    }
    var fl = d.fields || {}, keys = Object.keys(fl).filter(function (k) { return fl[k] != null && fl[k] !== ""; });
    if (keys.length) h += "<h3>" + tr("read") + "</h3><p>" + keys.map(function (k) { return esc(k) + ": <b>" + esc(fl[k]) + "</b>"; }).join(" · ") + "</p>";
    if (d.extract_error) h += '<p class="note">' + esc(d.extract_error) + "</p>";
    h += '<p class="note"><b>' + tr("close") + ":</b> " + esc(d["reminder_" + lang] || d.reminder_en || "") + "</p></div>";
    $("#pOut").innerHTML = h;
  }
  $("#pGo").addEventListener("click", function () {
    var btn = $("#pGo"), fd = new FormData(), f = $("#pImage").files[0];
    if (f) fd.append("image", f);
    fd.append("expected_amount", $("#pAmount").value);
    fd.append("expected_recipient", $("#pRecipient").value);
    fd.append("chat_time", $("#pChat").value);
    fd.append("order_ref", $("#pOrder").value);
    fd.append("manual", JSON.stringify({
      amount: $("#mAmount").value, trx_id: $("#mTrx").value, recipient: $("#mRecipient").value, datetime: $("#mTime").value
    }));
    btn.disabled = true; $("#pOut").innerHTML = '<p class="spin">' + tr("checking") + "</p>";
    api("/api/proof", { method: "POST", body: fd })
      .then(function (d) { lastRender.proof = function () { renderProof(d); }; renderProof(d); })
      .catch(function (e) { $("#pOut").innerHTML = '<p class="err">' + esc(e.message) + "</p>"; })
      .then(function () { btn.disabled = false; });
  });

  // ----- Trainer
  function renderTrainerHome() {
    var home = $("#trHome");
    if (!scenarios.length) { home.innerHTML = ""; return; }
    var h = '<p class="hint">' + tr("trHome") + '</p><div class="sc">' + scenarios.map(function (s, i) {
      return '<div class="card" data-i="' + i + '"><h3>' + esc(pick(s, "title")) + "</h3><p>" + esc(pick(s, "intro")) +
        '</p><button class="primary">' + tr("start") + "</button></div>";
    }).join("") + "</div>";
    if (aiMode !== "rules") {
      h += '<p><button class="linkbtn" id="freeBtn">' + tr("freeChat") + "</button></p>";
    }
    home.innerHTML = h;
    $$(".sc .card", home).forEach(function (c) { c.addEventListener("click", function () { startScript(scenarios[+c.dataset.i]); }); });
    var fb = $("#freeBtn"); if (fb) fb.addEventListener("click", function () { startFree(scenarios); });
  }
  function showPlay(html) { $("#trHome").hidden = true; var p = $("#trPlay"); p.hidden = false; p.innerHTML = html; return p; }
  function backHome() { $("#trPlay").hidden = true; $("#trHome").hidden = false; delete lastRender.trainer; }

  function startScript(sc) {
    var i = 0, total = 0, max = sc.steps.length * 2;
    function step() {
      var s = sc.steps[i];
      var render = function () {
        var h = '<div class="card"><p class="progress">' + esc(pick(sc, "title")) + " · " + tr("step") + " " + (i + 1) + " " + tr("of") + " " + sc.steps.length + "</p>";
        h += '<div class="bubble">' + esc(pick(s, "scammer")) + "</div>";
        h += s.choices.map(function (c, k) { return '<button class="choice" data-k="' + k + '">' + esc(pick(c, "")) + "</button>"; }).join("") + "</div>";
        var p = showPlay(h);
        $$(".choice", p).forEach(function (b) { b.addEventListener("click", function () { answer(s.choices[+b.dataset.k]); }); });
      };
      lastRender.trainer = render; render();
    }
    function answer(c) {
      total += c.score;
      var render = function () {
        var last = i === sc.steps.length - 1;
        var h = '<div class="card"><div class="bubble me">' + esc(c[lang] || c.en) + "</div>" +
          '<div class="fb s' + c.score + '"><b>' + tr("feedback") + ":</b> " + esc(c["fb_" + lang] || c.fb_en) + "</div>" +
          '<button class="primary" id="nx">' + (last ? tr("seeResult") : tr("nextStep")) + "</button></div>";
        var p = showPlay(h);
        $("#nx", p).addEventListener("click", function () { if (last) finish(); else { i++; step(); } });
      };
      lastRender.trainer = render; render();
    }
    function finish() {
      var render = function () {
        var pct = Math.round(100 * total / max), msg = pct >= 80 ? tr("excellent") : pct >= 50 ? tr("okay") : tr("weak");
        var h = '<div class="card"><h3>' + tr("scoreH") + ": " + total + " / " + max + "</h3>" +
          '<div class="bar2"><i style="width:' + pct + '%"></i></div><p>' + esc(msg) + "</p>" +
          "<h3>" + tr("flagsH") + "</h3><ul>" + (sc["red_flags_" + lang] || sc.red_flags_en).map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" +
          "<h3>" + tr("safeH") + "</h3><p>" + esc(pick(sc, "safe")) + '</p><button class="primary" id="bk">' + tr("again") + "</button></div>";
        var p = showPlay(h); $("#bk", p).addEventListener("click", backHome);
      };
      lastRender.trainer = render; render();
    }
    step();
  }

  function startFree(list) {
    var sc = list[0], history = [];
    var pickHtml = list.map(function (s, k) { return '<option value="' + esc(s.id) + '">' + esc(pick(s, "title")) + "</option>"; }).join("");
    var p = showPlay('<div class="card"><select id="fsel" style="width:100%;padding:8px;margin-bottom:8px">' + pickHtml + '</select><div id="log"></div>' +
      '<textarea id="fin" rows="2" placeholder="' + esc(tr("typeReply")) + '"></textarea>' +
      '<div class="btns"><button class="primary" id="fsend">' + tr("send") + '</button><button class="ghost" id="fend">' + tr("end") + '</button><button class="ghost" id="fbk">' + tr("again") + '</button></div><div id="fres"></div></div>');
    function log() {
      $("#log", p).innerHTML = history.map(function (m) {
        return '<div class="bubble' + (m.role === "player" ? " me" : "") + '"><b>' + (m.role === "player" ? tr("you") : tr("scammer")) + ":</b> " + esc(m.text) + "</div>";
      }).join("");
    }
    function turn() {
      return api("/api/trainer/chat", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: $("#fsel", p).value, history: history, lang: lang }) })
        .then(function (d) { history.push({ role: "scammer", text: d.text }); log(); })
        .catch(function (e) { $("#fres", p).innerHTML = '<p class="err">' + esc(e.message) + "</p>"; });
    }
    $("#fsel", p).addEventListener("change", function () { history = []; log(); $("#fres", p).innerHTML = ""; turn(); });
    $("#fsend", p).addEventListener("click", function () {
      var v = $("#fin", p).value.trim(); if (!v) return;
      history.push({ role: "player", text: v }); $("#fin", p).value = ""; log(); turn();
    });
    $("#fend", p).addEventListener("click", function () {
      $("#fres", p).innerHTML = '<p class="spin">' + tr("grading") + "</p>";
      api("/api/trainer/grade", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario: $("#fsel", p).value, history: history, lang: lang }) })
        .then(function (g) {
          var li = function (a) { return (a || []).map(function (x) { return "<li>" + esc(x) + "</li>"; }).join(""); };
          $("#fres", p).innerHTML = '<div class="res"><h3>' + tr("scoreH") + ": " + esc(g.score) + "/100</h3><h3>" + tr("caught") + "</h3><ul>" + li(g.caught) +
            "</ul><h3>" + tr("missed") + "</h3><ul>" + li(g.missed) + "</ul><h3>" + tr("tip") + "</h3><p>" + esc(g["tip_" + lang] || g.tip_en) + "</p></div>";
        })
        .catch(function (e) { $("#fres", p).innerHTML = '<p class="err">' + esc(e.message) + "</p>"; });
    });
    $("#fbk", p).addEventListener("click", backHome);
    turn();
  }

  // ----- boot
  Promise.all([
    api("/api/status").then(function (s) { aiMode = s.ai; }).catch(function () {}),
    api("/api/trainer/scenarios").then(function (s) { scenarios = s; }).catch(function () {})
  ]).then(applyLang);
  applyLang();
})();
