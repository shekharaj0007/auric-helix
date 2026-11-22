from __future__ import annotations

import json
import urllib.error
import urllib.request

BRIDGE_URL = "http://127.0.0.1:8766"


def bridge_status(timeout_s: float = 0.45) -> dict:
    try:
        req = urllib.request.Request(BRIDGE_URL + "/bridge/status", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        data["ok"] = True
        return data
    except Exception:
        return {
            "ok": False,
            "running": False,
            "status": "offline",
            "detail": "Bridge offline. Start start_forgemill.bat",
        }


def bridge_event(cmd: str, status: str = "", **extra) -> None:
    payload = json.dumps({"cmd": cmd, "status": status, **extra}).encode("utf-8")
    req = urllib.request.Request(
        BRIDGE_URL + "/bridge/event",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=0.6) as resp:
            resp.read()
    except urllib.error.URLError:
        return
