"""Minimal online-CNC API so the BTP dashboard can attach to another project.

Run this stub, then in the Streamlit sidebar:
  Data source = http
  CNC URL     = http://127.0.0.1:8765

Copy GET /telemetry and POST /command into your real web CNC.
"""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STATE = {
    "time_s": 0.0,
    "rpm": 3000.0,
    "feed_mm_tooth": 0.12,
    "temperature_c": 32.0,
    "spindle_current_a": 1.4,
    "spindle_power_w": 310.0,
    "vib_rms": 0.35,
    "force_rms": 210.0,
    "running": True,
}


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/telemetry":
            self._json(404, {"error": "use GET /telemetry"})
            return
        if STATE["running"]:
            STATE["time_s"] += 0.25
            STATE["vib_rms"] = 0.28 + 0.012 * STATE["time_s"]
            STATE["temperature_c"] = 30.0 + 0.35 * STATE["time_s"]
        self._json(200, STATE)

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/command":
            self._json(404, {"error": "use POST /command"})
            return
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        cmd = str(payload.get("cmd", "")).upper()
        if cmd == "FEED":
            STATE["feed_mm_tooth"] = float(payload["value"])
        elif cmd == "RPM":
            STATE["rpm"] = float(payload["value"])
        elif cmd == "STOP":
            STATE["running"] = False
        self._json(200, {"ok": True, "state": STATE})

    def log_message(self, fmt: str, *args: object) -> None:
        print("[online-cnc]", fmt % args)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("Online CNC API at http://127.0.0.1:8765")
    print("  GET  /telemetry")
    print("  POST /command   {cmd: FEED|RPM|STOP, value?, reason?}")
    server.serve_forever()
