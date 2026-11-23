/* Scam Shield service worker: keeps the app and its rules on the device so
 * message checks and the scripted trainer work with no internet.
 * Strategy: network first (always fresh when online), cache as fallback. */
var CACHE = "scamshield-v2";
var CORE = ["/", "/index.html", "/style.css", "/app.js", "/engine.js", "/icon.svg", "/manifest.webmanifest",
            "/api/rules", "/api/trainer/scenarios", "/api/meta", "/api/metrics"];
var CACHEABLE_API = ["/api/rules", "/api/trainer/scenarios", "/api/meta", "/api/metrics"];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) {
    // add one by one so a single failure does not block the rest
    return Promise.all(CORE.map(function (u) { return c.add(u).catch(function () {}); }));
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (e) {
  var req = e.request, url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin) return;
  var isApi = url.pathname.indexOf("/api/") === 0;
  if (isApi && CACHEABLE_API.indexOf(url.pathname) < 0) return; // live-only API (status, health)

  var key = req.mode === "navigate" ? "/" : url.pathname;
  e.respondWith(
    fetch(req).then(function (res) {
      if (res && res.ok) {
        var copy = res.clone();
        caches.open(CACHE).then(function (c) { c.put(key, copy); });
      }
      return res;
    }).catch(function () {
      return caches.match(key).then(function (hit) {
        return hit || (req.mode === "navigate" ? caches.match("/") : Response.error());
      });
    })
  );
});
