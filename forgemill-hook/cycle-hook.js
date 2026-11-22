/**
 * Drop this file into the ForgeMill project as public/cycle-hook.js
 * and load it from app/layout.tsx:
 *
 *   <Script src="/cycle-hook.js" strategy="afterInteractive" />
 *
 * Then redeploy Vercel. Cycle start / Hold / Stop will tell the
 * integrity monitor on the other laptop to start and stop.
 */
(function () {
  const TOPIC = "https://ntfy.sh/btp-forgemill-raj-integrity";
  const CYCLE_API = "/api/cycle";

  const report = (running, reason) => {
    const body = JSON.stringify({ running: running, reason: reason, t: Date.now() });
    try {
      fetch(CYCLE_API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body,
        keepalive: true,
      }).catch(function () {});
    } catch (e) {}
    try {
      fetch(TOPIC, {
        method: "POST",
        body: running ? "start" : "stop",
        keepalive: true,
      }).catch(function () {});
    } catch (e) {}
  };

  const labelOf = (el) =>
    ((el && (el.innerText || el.textContent || el.getAttribute("aria-label") || "")) || "")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();

  document.addEventListener(
    "click",
    (ev) => {
      const btn = ev.target && ev.target.closest && ev.target.closest("button, [role='button']");
      if (!btn) return;
      const label = labelOf(btn);
      if (label.includes("cycle start") || label === "start") report(true, "cycle-start");
      if (label.includes("hold") || label === "stop" || label.includes("feed hold")) report(false, "stop");
    },
    true
  );

  const readStatus = () => {
    const nodes = document.querySelectorAll("button, div, span, p");
    for (const n of nodes) {
      if (n.children && n.children.length > 2) continue;
      const t = (n.textContent || "").trim().toUpperCase();
      if (["IDLE", "RUN", "RUNNING", "HOLD", "STOPPED", "COMPLETE"].indexOf(t) >= 0) return t;
    }
    return "";
  };

  let last = "";
  let sawRun = false;
  setInterval(function () {
    const s = readStatus();
    if (!s || s === last) return;
    last = s;
    if (s === "RUN" || s === "RUNNING") {
      sawRun = true;
      report(true, s);
    } else if (s === "HOLD" || s === "STOPPED" || s === "COMPLETE") {
      sawRun = false;
      report(false, s);
    } else if (s === "IDLE" && sawRun) {
      sawRun = false;
      report(false, "IDLE");
    }
  }, 300);
})();
