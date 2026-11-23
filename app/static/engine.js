/* Scam Shield offline engine.
 *
 * A JavaScript port of app/rules.py + app/entities.py. It does not contain any
 * patterns itself: it runs the rule data served by /api/rules, so the browser and
 * the server always use the same library. tests/test_offline_parity.py checks that
 * both engines give identical results on every evaluation message.
 *
 * Character positions in the result are counted in Unicode code points, like Python.
 */
(function (root) {
  "use strict";

  var BN_DIGITS = "০১২৩৪৫৬৭৮৯";
  function toAsciiDigits(s) {
    return s.replace(/[০-৯]/g, function (d) { return String(BN_DIGITS.indexOf(d)); });
  }

  // rules.py _norm: lower case, Bangla digits to ASCII, whitespace collapsed
  function norm(text) {
    return toAsciiDigits(text.toLowerCase()).replace(/\s+/g, " ").trim();
  }

  // rules.py _same_len: same number of code points as the original text
  function sameLen(text) {
    var out = "";
    Array.from(text).forEach(function (c) {
      var l = c.toLowerCase();
      if (Array.from(l).length !== 1) l = c;
      l = toAsciiDigits(l);
      out += /\s/.test(l) ? " " : l;
    });
    return out;
  }

  // map UTF-16 offsets in s to code-point offsets
  function cpIndex(s) {
    var map = new Array(s.length + 1), cp = 0;
    for (var i = 0; i < s.length; i++) {
      map[i] = cp;
      var c = s.charCodeAt(i);
      if (c >= 0xD800 && c <= 0xDBFF && i + 1 < s.length) { map[i + 1] = cp; i++; }
      cp++;
    }
    map[s.length] = cp;
    return map;
  }

  function compile(data) {
    if (data._compiled) return data._compiled;
    var re = function (src, flags) { return new RegExp(src, flags || ""); };
    var c = {
      patterns: data.patterns.map(function (p) {
        return {
          p: p,
          groups: p.groups.map(function (g) { return g.map(function (s) { return re(s); }); }),
          groupsG: p.groups.map(function (g) { return g.map(function (s) { return re(s, "g"); }); }),
          unless: (p.unless || []).map(function (s) { return re(s); })
        };
      }),
      url: re(data.entities.url, "gi"),
      phone: re(data.entities.phone, "g"),
      hotline: re(data.entities.hotline, "g"),
      care: re(data.entities.care),
      brands: re(data.entities.brands)
    };
    Object.defineProperty(data, "_compiled", { value: c, enumerable: false });
    return c;
  }

  // urllib.parse.urlparse(u).hostname, then .strip(".")
  function hostOf(url) {
    var u = /^https?:\/\//i.test(url) ? url : "http://" + url;
    var rest = u.replace(/^[a-z][a-z0-9+.-]*:\/\//i, "");
    var netloc = rest.split(/[\/?#]/)[0];
    var h = netloc.slice(netloc.lastIndexOf("@") + 1);
    if (h.charAt(0) === "[") h = h.slice(1, h.indexOf("]") > 0 ? h.indexOf("]") : h.length);
    else h = h.split(":")[0];
    return h.toLowerCase().replace(/^\.+|\.+$/g, "");
  }

  function fill(tpl, kw) {
    return tpl.replace(/\{(\w+)\}/g, function (_, k) { return kw[k] != null ? kw[k] : ""; });
  }

  function rstrip(s, chars) {
    var i = s.length;
    while (i > 0 && chars.indexOf(s.charAt(i - 1)) >= 0) i--;
    return s.slice(0, i);
  }

  function entities(tl, data, c) {
    var E = data.entities, found = [], synth = {}, synthOrder = [], spans = [];
    var setdefault = function (key, val) { if (!(key in synth)) { synth[key] = val; synthOrder.push(key); } };
    var m;

    c.url.lastIndex = 0;
    while ((m = c.url.exec(tl)) !== null) {
      if (m[0] === "") { c.url.lastIndex++; continue; }
      var raw = rstrip(m[0], E.trail), host = hostOf(raw);
      if (!host || host.indexOf(".") < 0) continue;
      var start = m.index, end = m.index + raw.length;
      var en = [], bn = [], verdict = "unknown";
      var say = function (key, kw) { en.push(fill(E.reasons[key].en, kw || {})); bn.push(fill(E.reasons[key].bn, kw || {})); };
      var official = null;
      Object.keys(E.official_domains).some(function (d) {
        if (host === d || host.slice(-(d.length + 1)) === "." + d) { official = E.official_domains[d]; return true; }
        return false;
      });
      var tld = host.split(".").pop();
      if (official) {
        verdict = "official"; say("official", { name: official });
      } else {
        var isShort = E.shorteners.indexOf(host) >= 0;
        if (c.brands.test(host) || (isShort && c.brands.test(raw.toLowerCase()))) {
          verdict = "danger"; say("lookalike", { host: host });
          if (!("lookalike_link" in synth)) synthOrder.push("lookalike_link");
          synth.lookalike_link = E.synth.lookalike_link;
        }
        if (isShort) {
          verdict = verdict === "danger" ? "danger" : "caution"; say("short");
          setdefault("short_link", E.synth.short_link);
        }
        if (E.risky_tlds.indexOf(tld) >= 0) {
          verdict = verdict === "danger" ? "danger" : "caution"; say("tld", { tld: tld });
          setdefault("risky_domain", E.synth.risky_domain);
        }
        if (/^[\d.]+$/.test(host) || host.indexOf("xn--") === 0 || host.indexOf(".xn--") >= 0) {
          verdict = "danger"; say("ip");
          setdefault("risky_domain", E.synth.hidden_owner);
        }
        if (verdict === "unknown") {
          verdict = "caution"; say("unknown_link");
          setdefault("unknown_link", E.synth.unknown_link);
        }
      }
      found.push({ kind: "link", text: raw, host: host, verdict: verdict, reasons_en: en, reasons_bn: bn });
      if (verdict === "danger" || verdict === "caution") {
        spans.push([start, end, verdict, verdict === "danger" ? "lookalike_link" : "short_link"]);
      }
    }

    var care = c.care.test(tl);
    c.hotline.lastIndex = 0;
    while ((m = c.hotline.exec(tl)) !== null) {
      var name = E.hotlines[m[1]];
      found.push({ kind: "phone", text: m[1], verdict: "official",
        reasons_en: [fill(E.reasons.hotline.en, { name: name })], reasons_bn: [fill(E.reasons.hotline.bn, { name: name })] });
    }
    c.phone.lastIndex = 0;
    while ((m = c.phone.exec(tl)) !== null) {
      if (care) {
        found.push({ kind: "phone", text: m[0], verdict: "caution",
          reasons_en: [E.reasons.care_number.en], reasons_bn: [E.reasons.care_number.bn] });
        spans.push([m.index, m.index + m[0].length, "caution", "personal_number_care"]);
        setdefault("personal_number_care", E.synth.personal_number_care);
      } else {
        found.push({ kind: "phone", text: m[0], verdict: "unknown",
          reasons_en: [E.reasons.number.en], reasons_bn: [E.reasons.number.bn] });
      }
    }
    return { found: found, synth: synthOrder.map(function (k) { return synth[k]; }), spans: spans };
  }

  function merge(spans) {
    var order = { danger: 0, caution: 1 }, chosen = [];
    spans.slice().sort(function (a, b) { return (order[a[2]] - order[b[2]]) || (a[0] - b[0]); }).forEach(function (s) {
      if (chosen.every(function (c) { return s[1] <= c[0] || s[0] >= c[1]; })) chosen.push(s);
    });
    var cmp = function (x, y) { return x < y ? -1 : x > y ? 1 : 0; };
    return chosen.sort(function (a, b) { return (a[0] - b[0]) || (a[1] - b[1]) || cmp(a[2], b[2]) || cmp(a[3], b[3]); });
  }

  function analyze(text, data) {
    text = text || "";
    var c = compile(data), t = norm(text), tl = sameLen(text), cp = cpIndex(tl);
    var matches = [], spans = [];
    c.patterns.forEach(function (cp_) {
      if (cp_.unless.length && cp_.unless.some(function (r) { return r.test(t); })) return;
      if (!cp_.groups.every(function (g) { return g.some(function (r) { return r.test(t); }); })) return;
      matches.push(cp_.p);
      var kind = cp_.p.weight >= 60 ? "danger" : "caution";
      cp_.groupsG.forEach(function (g) {
        g.forEach(function (r) {
          r.lastIndex = 0;
          var k = 0, m;
          while ((m = r.exec(tl)) !== null) {
            if (m[0] === "") { r.lastIndex++; continue; }
            if (k >= data.max_spans_per_group) break;
            spans.push([m.index, m.index + m[0].length, kind, cp_.p.id]);
            k++;
          }
        });
      });
    });

    var ent = entities(tl, data, c);
    matches = matches.concat(ent.synth);
    spans = spans.concat(ent.spans);

    var score = Math.min(matches.reduce(function (s, p) { return s + p.weight; }, 0), 100);
    var risk = score >= data.high_at ? "high" : score >= data.medium_at ? "medium" : "low";
    var ordered = matches.map(function (p, i) { return [p, i]; })
      .sort(function (a, b) { return (b[0].weight - a[0].weight) || (a[1] - b[1]); })
      .map(function (x) { return x[0]; });
    var top = ordered[0];
    var names = {};
    matches.forEach(function (p) { names[p.id] = [p.name_en, p.name_bn]; });

    return {
      risk: risk,
      score: score,
      patterns: ordered.map(function (p) {
        return { id: p.id, name_en: p.name_en, name_bn: p.name_bn, why_en: p.why_en, why_bn: p.why_bn, weight: p.weight };
      }),
      highlights: merge(spans).map(function (s) {
        var n = names[s[3]] || ["", ""];
        return { start: cp[s[0]], end: cp[s[1]], kind: s[2], pattern: s[3], label_en: n[0], label_bn: n[1] };
      }),
      entities: ent.found,
      advice_en: top ? top.advice_en : data.safe_note_en,
      advice_bn: top ? top.advice_bn : data.safe_note_bn,
      hotlines: data.hotlines
    };
  }

  var api = { analyze: analyze, version: function (d) { return d && d.version; } };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.ScamEngine = api;
})(typeof self !== "undefined" ? self : this);
