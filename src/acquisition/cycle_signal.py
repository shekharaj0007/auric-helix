from __future__ import annotations

import json
import time
import urllib.request

from .bridge_client import bridge_status

CYCLE_TOPIC = "btp-forgemill-raj-integrity"
NTFY_URL = f"https://ntfy.sh/{CYCLE_TOPIC}"


def _remote_signal(vercel_base: str, timeout_s: float) -> dict | None:
    base = (vercel_base or "").rstrip("/")
    for url in (
        f"{base}/api/cycle" if base else "",
        f"{NTFY_URL}/json?poll=1",
    ):
        if not url:
            continue
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                raw = resp.read().decode("utf-8", "replace").strip()
            if not raw:
                continue
            if "ntfy.sh" in url:
                lines = [ln for ln in raw.splitlines() if ln.strip()]
                last = json.loads(lines[-1])
                if last.get("event") not in {None, "message"} and last.get("message") is None:
                    continue
                msg_t = float(last.get("time") or 0)
                if msg_t and (time.time() - msg_t) > 90:
                    continue
                msg = str(last.get("message") or "").strip().lower()
                running = msg in {"start", "run", "running", "1", "true"}
                return {"ok": True, "running": running, "reason": msg or "ntfy"}
            data = json.loads(raw)
            if isinstance(data, dict):
                running = bool(
                    data.get("running")
                    or str(data.get("status", "")).lower() in {"run", "running", "start"}
                )
                return {
                    "ok": True,
                    "running": running,
                    "reason": str(data.get("reason") or data.get("status") or ""),
                }
        except Exception:
            continue
    return None


def read_cycle_signal(vercel_base: str = "", timeout_s: float = 1.2) -> dict:
    """Read Cycle start/stop from the hooked mill proxy, then Vercel / ntfy."""
    br = bridge_status(timeout_s=min(timeout_s, 0.5))
    if br.get("ok"):
        return {
            "ok": True,
            "running": bool(br.get("running")),
            "reason": str(br.get("detail") or br.get("status") or "bridge"),
        }
    remote = _remote_signal(vercel_base, timeout_s)
    if remote:
        return remote
    return {"ok": False, "running": False, "reason": "no-signal"}
