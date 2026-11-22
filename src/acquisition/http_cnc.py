from __future__ import annotations

import json
import math
import time
import urllib.error
import urllib.request

import numpy as np

from .base import SensorFrame, SensorSource
from .gcode_playback import GCodePlayback, extract_gcode


class HttpCncSource(SensorSource):
    """Talk to an online CNC.

    1. JSON API: GET /telemetry or /api/telemetry, POST /command
    2. ForgeMill Vercel page: no API — the mill lives in the browser.
       This client downloads the G-code from the page and replays it,
       then **stops at M30** so the monitor does not keep running after
       the cycle ends.
    """

    name = "http"

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8765",
        window_seconds: float = 0.25,
        sample_rate_hz: float = 2000,
        timeout_s: float = 12.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.window_seconds = window_seconds
        self.sample_rate_hz = sample_rate_hz
        self.timeout_s = timeout_s
        self._t0 = 0.0
        self.stopped = False
        self.feed_mm_tooth = 0.12
        self.rpm = 3000.0
        self._telemetry_path = "/telemetry"
        self._command_path = "/command"
        self._mode = "api"
        self._player: GCodePlayback | None = None

    def _fetch_bytes(self, url: str) -> tuple[int, str, str]:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json, text/html;q=0.9", "User-Agent": "ForgeMill-BTP/1.0"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            body = resp.read().decode("utf-8", "replace")
            ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            return resp.status, ctype, body

    def open(self) -> None:
        self._t0 = time.time()
        self.stopped = False
        self._player = None
        last_error: Exception | None = None
        candidates = [
            self.base_url,
            self.base_url + "/telemetry",
            self.base_url + "/api/telemetry",
        ]
        for url in candidates:
            try:
                _status, ctype, body = self._fetch_bytes(url)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                continue
            stripped = body.lstrip()
            if "json" in ctype or stripped.startswith("{") or stripped.startswith("["):
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError as exc:
                    last_error = exc
                    continue
                if isinstance(payload, dict):
                    self._mode = "api"
                    if url.endswith("/api/telemetry"):
                        self._telemetry_path = "/api/telemetry"
                        self._command_path = "/api/command"
                    elif url.endswith("/telemetry"):
                        self._telemetry_path = "/telemetry"
                        self._command_path = "/command"
                    return
            program = extract_gcode(body)
            if program:
                self._mode = "gcode"
                self._player = GCodePlayback(
                    program,
                    sample_rate_hz=self.sample_rate_hz,
                    window_seconds=self.window_seconds,
                )
                return
            last_error = RuntimeError(f"{url} returned {ctype or 'unknown'} without JSON telemetry or G-code")

        raise RuntimeError(
            f"Could not attach to {self.base_url}. "
            "ForgeMill on Vercel is a browser mill (no /telemetry API). "
            "This dashboard now reads G-code from the page; if that failed, "
            f"check the URL. Last error: {last_error}"
        )

    def close(self) -> None:
        return

    def _get(self, path: str) -> dict:
        url = self.base_url + path
        _status, _ctype, body = self._fetch_bytes(url)
        return json.loads(body)

    def _post(self, path: str, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                resp.read()
        except urllib.error.URLError as exc:
            if self._mode == "gcode":
                return
            raise RuntimeError(f"CNC command failed: {exc}") from exc

    def apply_overrides(self, *, feed_mm_tooth: float | None = None, rpm: float | None = None) -> None:
        if feed_mm_tooth is not None:
            self.feed_mm_tooth = float(feed_mm_tooth)
            if self._player is not None:
                self._player.apply_feed_override(min(max(feed_mm_tooth / 0.12, 0.25), 1.2))
            else:
                self._post(self._command_path, {"cmd": "FEED", "value": self.feed_mm_tooth})
        if rpm is not None:
            self.rpm = float(rpm)
            if self._player is None:
                self._post(self._command_path, {"cmd": "RPM", "value": self.rpm})

    def request_stop(self, reason: str = "") -> None:
        self.stopped = True
        if self._player is not None:
            self._player.request_stop(reason)
        self._post(self._command_path, {"cmd": "STOP", "reason": reason})

    def _window(self, payload: dict, key: str, rms_key: str, n: int) -> np.ndarray:
        raw = payload.get(key)
        if isinstance(raw, list) and raw:
            arr = np.asarray(raw, dtype=np.float32)
            if len(arr) >= n:
                return arr[-n:]
            return np.resize(arr, n)
        rms = float(payload.get(rms_key, 0.2))
        t = np.arange(n) / max(self.sample_rate_hz, 1.0)
        rpm = float(payload.get("rpm", self.rpm))
        tooth = (rpm / 60.0) * 4.0
        return (rms * np.sqrt(2.0) * np.sin(2 * np.pi * tooth * t)).astype(np.float32)

    def read_frame(self) -> SensorFrame:
        if self.stopped:
            raise RuntimeError("Cycle stop requested on online CNC")
        if self._player is not None:
            return self._player.step()
        payload = self._get(self._telemetry_path)
        status = str(
            payload.get("status")
            or payload.get("state")
            or payload.get("mode")
            or ""
        ).lower()
        running = payload.get("running", payload.get("cycle_running"))
        if running is False or status in {"idle", "complete", "m30", "program_end", "stopped"}:
            if float(payload.get("time_s", 1) or 0) > 0.5 or status in {"complete", "m30", "program_end"}:
                raise RuntimeError("Cycle stop: online CNC cycle ended.")

        n = max(int(self.sample_rate_hz * self.window_seconds), 64)
        rpm = float(payload.get("rpm", self.rpm))
        feed = float(payload.get("feed_mm_tooth", self.feed_mm_tooth))
        self.rpm, self.feed_mm_tooth = rpm, feed
        diameter = float(payload.get("tool_diameter_mm", 10.0))
        vc = float(payload.get("cutting_speed_m_min", math.pi * diameter * rpm / 1000.0))
        t_now = float(payload.get("time_s", time.time() - self._t0))
        return SensorFrame(
            time_s=t_now,
            vibration=self._window(payload, "vibration", "vib_rms", n),
            force=self._window(payload, "force", "force_rms", n),
            temperature_c=float(payload.get("temperature_c", 30.0)),
            spindle_power_w=float(payload.get("spindle_power_w", payload.get("spindle_current_a", 1.0) * 220.0)),
            spindle_current_a=float(payload.get("spindle_current_a", 1.0)),
            cutting_speed_m_min=vc,
            feed_mm_tooth=feed,
            rpm=rpm,
            sample_rate_hz=self.sample_rate_hz,
            source_name=f"http:{self.base_url}",
            true_ra_um=payload.get("ra_um"),
            true_vb_mm=payload.get("vb_mm"),
            true_wear_rate_um_s=payload.get("wear_rate_um_s"),
            meta={"tooth_freq_hz": rpm / 60.0 * float(payload.get("teeth", 4))},
        )
