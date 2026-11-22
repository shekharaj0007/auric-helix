"""Local ForgeMill bridge: side-by-side shop floor + Cycle Start/Stop sync.

ForgeMill on Vercel is a browser mill with no API. This process:

1. Proxies the Vercel app at /mill and injects a click/status hook.
2. Serves a split view at http://127.0.0.1:8766/  (CNC | monitor).
3. Exposes GET/POST /bridge so the Streamlit dashboard starts only on
   Cycle Start and stops on Hold / Stop / IDLE / M30.

Run together with the Streamlit app (see start_forgemill.bat).
"""
from __future__ import annotations

import json
import os
import re
import socket
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "0.0.0.0"
PORT = 8766
FORGE = "https://temporary-speedy-azure-d4iojfc.vercel.app"
MONITOR = "http://127.0.0.1:8501"
NTFY = "https://ntfy.sh/btp-forgemill-raj-integrity"

STATE = {
    "ok": True,
    "running": False,
    "status": "idle",
    "want_stop": False,
    "want_hold": False,
    "seq": 0,
    "updated": 0.0,
    "detail": "Waiting for Cycle start",
    "x": None,
    "y": None,
    "z": None,
    "frozen": False,
}
LOCK = threading.Lock()
ASSET_CACHE: dict[str, tuple[bytes, str]] = {}

_JS_RUN_EFFECT = '(0,a.useEffect)(()=>{if("run"!==i)return;'
_JS_HOLD_HOOKS = (
    '(0,a.useEffect)(()=>{let id=setInterval(()=>{fetch("/bridge/status").then(r=>r.json()).then(st=>'
    '{if(st&&(st.want_hold||st.want_stop)&&"run"===i)o("hold")}).catch(()=>{})},150);return()=>clearInterval(id)},[]);'
)
_JS_CANVAS_CLEANUP = (
    'a.addEventListener("wheel",g,{passive:!1}),h();let b=requestAnimationFrame(h);'
    'return()=>{cancelAnimationFrame(b),m.disconnect(),a.removeEventListener("wheel",g)}'
)
_JS_CANVAS_FIX = (
    'a.addEventListener("wheel",g,{passive:!1}),h();let b=requestAnimationFrame(h);'
    'return()=>{cancelAnimationFrame(b);a.removeEventListener("wheel",g)}'
)


def _patch_mill_js(text: str) -> str:
    return text

INJECT = r"""
<script id="btp-bridge">
(function () {
  const TABLE = { w: 300, d: 200 };
  const DURATION = 35000;
  let millView = "iso";
  let sawRun = false;
  const cycle = { mode: "idle", t0: 0, paused: 0, pts: [], x: 0, y: 0, z: 15 };

  const post = (cmd, extra) => {
    try {
      fetch("/bridge/event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(Object.assign({ cmd: cmd }, extra || {})),
        keepalive: true,
      });
    } catch (e) {}
    if (cmd === "start" || cmd === "complete" || cmd === "stop") {
      try {
        fetch("https://ntfy.sh/btp-forgemill-raj-integrity", {
          method: "POST",
          body: cmd === "start" ? "start" : "stop",
          keepalive: true,
        });
      } catch (e) {}
    }
  };

  const labelOf = (el) => ((el && (el.innerText || el.textContent || el.getAttribute("aria-label") || "")) || "")
    .replace(/\s+/g, " ").trim().toLowerCase();

  const ru = (x, y, z) => millView === "top"
    ? { x: x, y: y }
    : { x: (x - y) * Math.cos(Math.PI / 6), y: (x + y) * Math.sin(Math.PI / 6) - z };

  const cutColor = (z) => {
    const n = Math.max(3 - 0, 0.25);
    const l = Math.min(1, Math.max(0, (0 - z) / n));
    return "hsl(" + (48 - 42 * l) + " " + (85 + 10 * l) + "% " + (58 - 14 * l) + "%)";
  };

  const parseProgram = (src) => {
    let x = 0, y = 0, z = 15, abs = true;
    const pts = [{ x: 0, y: 0, z: 15, rapid: true }];
    String(src || "").split("\n").forEach((raw) => {
      const line = raw.replace(/\([^)]*\)/g, " ").toUpperCase();
      if (/\bG90\b/.test(line)) abs = true;
      if (/\bG91\b/.test(line)) abs = false;
      const mx = line.match(/\bX(-?\d+\.?\d*)/);
      const my = line.match(/\bY(-?\d+\.?\d*)/);
      const mz = line.match(/\bZ(-?\d+\.?\d*)/);
      if (!mx && !my && !mz) return;
      x = abs ? (mx ? Number(mx[1]) : x) : x + (mx ? Number(mx[1]) : 0);
      y = abs ? (my ? Number(my[1]) : y) : y + (my ? Number(my[1]) : 0);
      z = abs ? (mz ? Number(mz[1]) : z) : z + (mz ? Number(mz[1]) : 0);
      const rapid = (/\bG00\b|\bG0\b/.test(line)) && !(/\bG01\b|\bG1\b|\bG02\b|\bG2\b|\bG03\b|\bG3\b|\bG81\b/.test(line));
      pts.push({ x: x, y: y, z: z, rapid: rapid });
    });
    return pts;
  };

  const programText = () => {
    const ta = document.querySelector("textarea");
    if (ta && ta.value && ta.value.length > 30) return ta.value;
    return "G90 G0 Z15\nG0 X14 Y10\nG1 Z-2 F240\nG1 X76 F900\nG2 X80 Y14 R4\nG1 Y46\nG2 X76 Y50 R4\nG1 X14\nG2 X10 Y46 R4\nG1 Y14\nG2 X14 Y10 R4\nG0 Z2\nG0 X24 Y20\nG1 Z-1.2\nG1 X66\nG1 Y40\nG1 X24\nG1 Y20\nG0 Z12";
  };

  const writeStatus = (name) => {
    document.querySelectorAll("span").forEach((n) => {
      if (n.closest && n.closest("button")) return;
      const t = (n.textContent || "").trim();
      if (t === "IDLE" || t === "CYCLE ON" || t === "FEED HOLD" || t === "PROGRAM END") n.textContent = name;
    });
  };

  const writeDRO = (x, y, z) => {
    const vals = { X: x, Y: y, Z: z };
    document.querySelectorAll("span, strong").forEach((n) => {
      const lab = (n.textContent || "").trim().toUpperCase();
      if (lab === "X" || lab === "Y" || lab === "Z") {
        const sib = n.nextElementSibling;
        if (sib) sib.textContent = Number(vals[lab]).toFixed(3);
      }
    });
  };

  const xyzPayload = () => ({ x: cycle.x, y: cycle.y, z: cycle.z });

  const markStart = () => {
    sawRun = true;
    post("start", Object.assign({ status: "CYCLE ON" }, xyzPayload()));
  };
  const markComplete = (why) => {
    if (!sawRun) return;
    sawRun = false;
    post("complete", Object.assign({ status: why || "IDLE" }, xyzPayload()));
  };

  const startCycle = () => {
    if (cycle.mode === "run") return;
    if (cycle.mode === "hold") {
      cycle.mode = "run";
      cycle.t0 = performance.now() - cycle.paused;
      writeStatus("CYCLE ON");
      markStart();
      return;
    }
    cycle.pts = parseProgram(programText());
    cycle.mode = "run";
    cycle.t0 = performance.now();
    cycle.x = cycle.pts[0].x; cycle.y = cycle.pts[0].y; cycle.z = cycle.pts[0].z;
    writeStatus("CYCLE ON");
    writeDRO(cycle.x, cycle.y, cycle.z);
    markStart();
  };

  const holdCycle = () => {
    if (cycle.mode !== "run") return;
    cycle.mode = "hold";
    cycle.paused = performance.now() - cycle.t0;
    writeStatus("FEED HOLD");
    post("held", Object.assign({ status: "FEED HOLD" }, xyzPayload()));
  };

  const stopCycle = () => {
    const was = cycle.mode;
    cycle.mode = "idle";
    writeStatus("IDLE");
    if (was === "run" || was === "hold") markComplete("stop");
  };

  const paintMill = () => {
    const canvas = document.querySelector("canvas.cursor-grab") || document.querySelector("canvas");
    if (!canvas) return;
    const box = canvas.parentElement || canvas;
    const cssW = Math.max(8, Math.floor(box.clientWidth || 640));
    const cssH = Math.max(8, Math.floor(box.clientHeight || 280));
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(cssW * dpr);
    canvas.height = Math.floor(cssH * dpr);
    canvas.style.width = cssW + "px";
    canvas.style.height = cssH + "px";
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const w = cssW, h = cssH;
    const grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, "#12171d");
    grad.addColorStop(1, "#0b0e12");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);
    const pts = cycle.pts.length ? cycle.pts : parseProgram(programText());
    const samples = pts.concat([
      { x: 0, y: 0, z: 0 }, { x: TABLE.w, y: 0, z: 0 }, { x: TABLE.w, y: TABLE.d, z: 0 }, { x: 0, y: TABLE.d, z: 0 }
    ]);
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    samples.forEach((p) => {
      const q = ru(p.x, p.y, p.z);
      minX = Math.min(minX, q.x); minY = Math.min(minY, q.y);
      maxX = Math.max(maxX, q.x); maxY = Math.max(maxY, q.y);
    });
    const scale = Math.min((w - 72) / Math.max(maxX - minX, 8), (h - 72) / Math.max(maxY - minY, 8));
    const panX = w / 2 - (minX + maxX) / 2 * scale;
    const panY = h / 2 + (minY + maxY) / 2 * scale;
    const to = (p) => {
      const q = ru(p.x, p.y, p.z);
      return { x: panX + q.x * scale, y: panY - q.y * scale };
    };
    const step = scale > 8 ? 10 : scale > 3.5 ? 20 : 50;
    ctx.lineWidth = 1;
    for (let gx = 0; gx <= TABLE.w; gx += step) {
      const a = to({ x: gx, y: 0, z: 0 });
      const b = to({ x: gx, y: TABLE.d, z: 0 });
      ctx.strokeStyle = gx % 50 === 0 ? "rgba(180, 198, 214, 0.14)" : "rgba(180, 198, 214, 0.06)";
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
    }
    for (let gy = 0; gy <= TABLE.d; gy += step) {
      const a = to({ x: 0, y: gy, z: 0 });
      const b = to({ x: TABLE.w, y: gy, z: 0 });
      ctx.strokeStyle = gy % 50 === 0 ? "rgba(180, 198, 214, 0.14)" : "rgba(180, 198, 214, 0.06)";
      ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
    }
    const table = [{ x: 0, y: 0, z: 0 }, { x: TABLE.w, y: 0, z: 0 }, { x: TABLE.w, y: TABLE.d, z: 0 }, { x: 0, y: TABLE.d, z: 0 }];
    ctx.beginPath();
    table.forEach((p, i) => { const q = to(p); i ? ctx.lineTo(q.x, q.y) : ctx.moveTo(q.x, q.y); });
    ctx.closePath();
    ctx.fillStyle = "rgba(36, 48, 58, 0.45)";
    ctx.fill();
    ctx.strokeStyle = "rgba(132, 168, 186, 0.45)";
    ctx.lineWidth = 1.4;
    ctx.stroke();
    ctx.font = "11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace";
    ctx.fillStyle = "rgba(164, 188, 204, 0.7)";
    const t0 = to({ x: 0, y: 0, z: 0 });
    ctx.fillText("TABLE  " + TABLE.w + " x " + TABLE.d + " mm", t0.x + 8, t0.y - 8);
    if (pts.length > 1) {
      for (let i = 1; i < pts.length; i++) {
        const a = to(pts[i - 1]);
        const bpt = to(pts[i]);
        if (pts[i].rapid) {
          ctx.setLineDash([6, 5]);
          ctx.strokeStyle = "rgba(90, 196, 255, 0.85)";
          ctx.lineWidth = 1.15;
        } else {
          ctx.setLineDash([]);
          ctx.strokeStyle = cutColor((pts[i - 1].z + pts[i].z) / 2);
          ctx.lineWidth = 2.15;
        }
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(bpt.x, bpt.y); ctx.stroke();
      }
      ctx.setLineDash([]);
    }
    const tp = to({ x: cycle.x, y: cycle.y, z: cycle.z });
    ctx.fillStyle = cycle.mode === "run" ? "#7DFFB3" : "#d6dce6";
    ctx.beginPath(); ctx.arc(tp.x, tp.y, 5.5, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = "rgba(255,255,255,0.85)";
    ctx.lineWidth = 1;
    ctx.stroke();
  };

  const advance = () => {
    if (cycle.mode === "run") {
      const u = Math.min(1, (performance.now() - cycle.t0) / DURATION);
      const pts = cycle.pts.length ? cycle.pts : parseProgram(programText());
      const n = Math.max(pts.length - 1, 1);
      const f = u * n;
      const i = Math.min(Math.floor(f), n - 1);
      const k = f - i;
      const a = pts[i];
      const b = pts[i + 1] || a;
      cycle.x = a.x + (b.x - a.x) * k;
      cycle.y = a.y + (b.y - a.y) * k;
      cycle.z = a.z + (b.z - a.z) * k;
      writeDRO(cycle.x, cycle.y, cycle.z);
      writeStatus("CYCLE ON");
      if (u >= 1) {
        cycle.mode = "done";
        writeStatus("PROGRAM END");
        markComplete("PROGRAM END");
      }
    } else if (cycle.mode === "idle" && !cycle.pts.length) {
      cycle.pts = parseProgram(programText());
      cycle.x = 0; cycle.y = 0; cycle.z = 15;
    }
    paintMill();
    requestAnimationFrame(advance);
  };

  document.addEventListener("click", (ev) => {
    const btn = ev.target && ev.target.closest && ev.target.closest("button, [role='button']");
    if (!btn) return;
    const label = labelOf(btn);
    if (label.includes("cycle start") || label === "start") {
      ev.preventDefault(); ev.stopPropagation(); startCycle();
    } else if (label === "hold" || label.includes("feed hold")) {
      ev.preventDefault(); ev.stopPropagation(); holdCycle();
    } else if (label === "stop") {
      ev.preventDefault(); ev.stopPropagation(); stopCycle();
    } else if (label === "top") millView = "top";
    else if (label === "iso") millView = "iso";
  }, true);

  document.addEventListener("keydown", (ev) => {
    if (/input|textarea/i.test((ev.target && ev.target.tagName) || "")) return;
    if (ev.code === "Space") {
      ev.preventDefault();
      if (cycle.mode === "run") holdCycle(); else startCycle();
    } else if (ev.code === "Escape") {
      ev.preventDefault(); stopCycle();
    }
  }, true);

  setInterval(() => {
    fetch("/bridge/status").then((r) => r.json()).then((st) => {
      if (st && (st.want_hold || st.want_stop) && cycle.mode === "run") holdCycle();
    }).catch(() => {});
    if (cycle.mode === "run" || cycle.mode === "hold") {
      post("pose", Object.assign({ status: cycle.mode === "run" ? "CYCLE ON" : "FEED HOLD" }, xyzPayload()));
    }
  }, 250);

  requestAnimationFrame(advance);
  setTimeout(startCycle, 800);
})();
</script>
"""

COCKPIT = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Shop floor — ForgeMill + integrity monitor</title>
  <style>
    html, body {{ margin: 0; height: 100%; background: #0B0D10; color: #D6DCE6; font-family: Segoe UI, sans-serif; }}
    .bar {{ padding: 8px 14px; background: #12151A; border-bottom: 1px solid #2A3038; font-size: 13px; }}
    .bar b {{ color: #7DFFB3; }}
    .grid {{ display: grid; grid-template-columns: 1.15fr 0.85fr; height: calc(100vh - 38px); }}
    iframe {{ border: 0; width: 100%; height: 100%; background: #0B0D10; }}
    @media (max-width: 1100px) {{
      .grid {{ grid-template-columns: 1fr; grid-template-rows: 50% 50%; }}
    }}
  </style>
</head>
<body>
  <div class="bar">Press <b>Cycle start</b> on the mill. The monitor on the right runs only during the cut and stops when the cycle stops.</div>
  <div class="grid">
    <iframe src="/mill" title="ForgeMill CNC"></iframe>
    <iframe src="{MONITOR}" title="Integrity monitor"></iframe>
  </div>
</body>
</html>
"""


def _num(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _apply_event(cmd: str, status: str = "", x=None, y=None, z=None) -> None:
    cmd = (cmd or "").lower()
    status = (status or "").upper()
    with LOCK:
        STATE["updated"] = time.time()
        STATE["seq"] += 1
        nx, ny, nz = _num(x), _num(y), _num(z)
        if nx is not None:
            STATE["x"] = nx
        if ny is not None:
            STATE["y"] = ny
        if nz is not None:
            STATE["z"] = nz
        if cmd == "pose":
            st = (status or "").lower()
            if "feed hold" in st:
                STATE["frozen"] = True
                STATE["running"] = False
                STATE["status"] = "HOLD"
                STATE["want_hold"] = False
                STATE["want_stop"] = False
                STATE["detail"] = "Held at current position"
            elif "cycle on" in st or st in {"run", "running"}:
                STATE["running"] = True
                STATE["status"] = "RUN"
                STATE["frozen"] = False
            elif "program end" in st or st == "done":
                STATE["running"] = False
                STATE["status"] = "IDLE"
                STATE["detail"] = "Program complete"
            elif st == "idle":
                STATE["status"] = "IDLE"
            return
        if cmd == "start":
            STATE["running"] = True
            STATE["status"] = status or "RUN"
            STATE["want_stop"] = False
            STATE["want_hold"] = False
            STATE["frozen"] = False
            STATE["detail"] = "Cycle start"
        elif cmd == "held" or cmd == "ack_hold":
            STATE["status"] = "HOLD"
            STATE["frozen"] = True
            STATE["running"] = False
            STATE["want_hold"] = False
            STATE["want_stop"] = False
            STATE["detail"] = "Held at current position"
        elif cmd in {"stop", "complete"}:
            STATE["running"] = False
            STATE["status"] = status or "IDLE"
            STATE["want_stop"] = False
            STATE["want_hold"] = False
            STATE["detail"] = "Cycle stopped" if cmd != "complete" else "Program complete (M30 / IDLE)"
        elif cmd in {"want_stop", "want_hold"}:
            STATE["want_hold"] = True
            STATE["want_stop"] = False
            STATE["detail"] = "Monitor requested feed-hold in place"
        elif cmd == "ack_stop":
            STATE["want_stop"] = False
            STATE["want_hold"] = False
            STATE["running"] = False
            STATE["status"] = "HOLD"
            STATE["frozen"] = True


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, code: int, body: bytes, content_type: str, extra: dict[str, str] | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        if extra:
            for key, value in extra.items():
                self.send_header(key, value)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            return

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path.split("?")[0] != "/bridge/event":
            self._send(404, b'{"error":"not found"}', "application/json")
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        payload = json.loads(self.rfile.read(length) or b"{}")
        _apply_event(
            str(payload.get("cmd", "")),
            str(payload.get("status", "")),
            payload.get("x"),
            payload.get("y"),
            payload.get("z"),
        )
        with LOCK:
            body = json.dumps(STATE).encode("utf-8")
        self._send(200, body, "application/json")

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?")[0]
        if path == "/cockpit":
            self._send(200, COCKPIT.encode("utf-8"), "text/html; charset=utf-8")
            return
        if path == "/bridge/status":
            with LOCK:
                body = json.dumps(STATE).encode("utf-8")
            self._send(200, body, "application/json")
            return
        if path in {"/", "/mill"}:
            self._proxy("/")
            return
        self._proxy(path)

    def _proxy(self, path: str) -> None:
        if path == "/mill":
            path = "/"
        cache_key = path
        nocache = {
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
        }
        cached = ASSET_CACHE.get(cache_key) if path.startswith("/_next/") else None
        if cached:
            self._send(200, cached[0], cached[1], nocache)
            return
        url = FORGE + (path if path.startswith("/") else "/" + path)
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": self.headers.get("User-Agent") or "ForgeMill-BTP-Bridge",
                    "Accept": self.headers.get("Accept") or "*/*",
                    "Accept-Encoding": "identity",
                },
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                raw = resp.read()
                ctype = (resp.headers.get("Content-Type") or "application/octet-stream").split(";")[0].strip()
                code = resp.status
        except urllib.error.HTTPError as exc:
            raw = exc.read() or str(exc).encode()
            ctype = (exc.headers.get("Content-Type") if exc.headers else None) or "text/plain"
            code = exc.code
        except Exception as exc:  # noqa: BLE001
            msg = f"Proxy failed: {exc}".encode("utf-8")
            self._send(502, msg, "text/plain")
            return

        if ("javascript" in ctype.lower() or path.endswith(".js")) and (
            _JS_RUN_EFFECT.encode("utf-8") in raw or _JS_CANVAS_CLEANUP.encode("utf-8") in raw
        ):
            text = raw.decode("utf-8", "replace")
            patched = _patch_mill_js(text)
            if patched != text:
                raw = patched.encode("utf-8")
            ctype = "application/javascript; charset=utf-8"

        html = "html" in ctype.lower()
        extra = dict(nocache)
        if html:
            extra["X-Frame-Options"] = "ALLOWALL"
            text = raw.decode("utf-8", "replace")
            incoming = self.headers.get("Host") or f"127.0.0.1:{PORT}"
            text = text.replace(FORGE, f"http://{incoming}")
            text = re.sub(
                r'(src="/_next/static/chunks/[^"]+\.js)"',
                r'\1?btp=work1"',
                text,
            )
            text = re.sub(
                r'(href="/_next/static/chunks/[^"]+\.js)"',
                r'\1?btp=work1"',
                text,
            )
            if "</head>" in text:
                text = text.replace(
                    "</head>",
                    '<meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate"/>'
                    '<meta http-equiv="Pragma" content="no-cache"/></head>',
                    1,
                )
            if "</body>" in text:
                text = text.replace("</body>", INJECT + "</body>", 1)
            else:
                text += INJECT
            raw = text.encode("utf-8")
            ctype = "text/html; charset=utf-8"
        if path.startswith("/_next/") and code == 200:
            ASSET_CACHE[cache_key] = (raw, ctype)
        self._send(code, raw, ctype, extra)


class ExclusiveHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = False

    def server_bind(self) -> None:
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def main() -> None:
    server = ExclusiveHTTPServer((HOST, PORT), Handler)
    print(f"Hooked ForgeMill:  http://127.0.0.1:{PORT}/", flush=True)
    print(f"Bridge API:        http://127.0.0.1:{PORT}/bridge/status", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
