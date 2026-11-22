from __future__ import annotations

import html as html_lib
import math
import re
from dataclasses import dataclass

import numpy as np

from .base import SensorFrame


_WORD = re.compile(r"([A-Z])([+-]?(?:\d+\.?\d*|\.\d+))")
_TEXTAREA = re.compile(
    r'aria-label="G-code program">(.*?)</textarea>',
    re.IGNORECASE | re.DOTALL,
)
_M30_BLOCK = re.compile(r"(G21[\s\S]{20,8000}?M30)", re.IGNORECASE)


def extract_gcode(page: str) -> str | None:
    """Pull the NC program out of a ForgeMill (or similar) HTML page."""
    text = html_lib.unescape(page)
    match = _TEXTAREA.search(text)
    if match:
        return match.group(1).strip()
    match = _M30_BLOCK.search(text)
    if match:
        return match.group(1).strip()
    return None


@dataclass
class Segment:
    duration_s: float
    cutting: bool
    spindle: bool
    rpm: float
    feed_mm_min: float
    x: float
    y: float
    z: float
    end_program: bool = False


def _words(line: str) -> dict[str, float]:
    clean = re.sub(r"\([^)]*\)", " ", line)
    clean = re.sub(r";.*", " ", clean)
    found: dict[str, float] = {}
    for letter, number in _WORD.findall(clean.upper()):
        found[letter] = float(number)
    return found


def compile_program(program: str, *, rapid_mm_min: float = 9000.0) -> list[Segment]:
    x = y = z = 0.0
    rpm = 0.0
    feed = 300.0
    spindle = False
    motion = 0
    drill_z: float | None = None
    retract: float | None = None
    segments: list[Segment] = []

    def add_move(nx: float, ny: float, nz: float, *, cutting: bool, feed_now: float) -> None:
        nonlocal x, y, z
        dist = math.sqrt((nx - x) ** 2 + (ny - y) ** 2 + (nz - z) ** 2)
        speed = max(feed_now if cutting else rapid_mm_min, 30.0) / 60.0
        dt = max(dist / speed, 0.04) if dist > 1e-6 else 0.05
        segments.append(
            Segment(dt, cutting and spindle, spindle, rpm, feed_now, nx, ny, nz)
        )
        x, y, z = nx, ny, nz

    for raw in program.splitlines():
        w = _words(raw)
        if not w and "M30" not in raw.upper() and "M5" not in raw.upper() and "M3" not in raw.upper():
            continue
        if "S" in w:
            rpm = w["S"]
        if "F" in w:
            feed = w["F"]
        if "M" in w:
            m = int(w["M"])
            if m == 3:
                spindle = True
            elif m in {5, 2}:
                spindle = False
            elif m == 30:
                spindle = False
                segments.append(Segment(0.2, False, False, 0.0, feed, x, y, z, end_program=True))
                break
        if "G" in w:
            g = int(w["G"])
            if g in {0, 1, 2, 3, 81}:
                motion = g
            elif g == 80:
                motion = 0
                drill_z = None
        nx = w.get("X", x)
        ny = w.get("Y", y)
        nz = w.get("Z", z)
        moved = ("X" in w) or ("Y" in w) or ("Z" in w)
        if not moved:
            continue
        if motion == 0:
            add_move(nx, ny, nz, cutting=False, feed_now=rapid_mm_min)
        elif motion in {1, 2, 3}:
            if motion in {2, 3} and "R" in w:
                radius = abs(w["R"])
                dist = max(0.5 * math.pi * radius, 0.2)
                speed = max(feed, 30.0) / 60.0
                dt = dist / speed
                segments.append(Segment(dt, spindle, spindle, rpm, feed, nx, ny, nz))
                x, y, z = nx, ny, nz
            else:
                add_move(nx, ny, nz, cutting=True, feed_now=feed)
        elif motion == 81:
            if "R" in w:
                retract = w["R"]
            if "Z" in w:
                drill_z = w["Z"]
            plane = retract if retract is not None else z
            depth = drill_z if drill_z is not None else nz
            add_move(nx, ny, plane, cutting=False, feed_now=rapid_mm_min)
            add_move(nx, ny, depth, cutting=True, feed_now=feed)
            add_move(nx, ny, plane, cutting=False, feed_now=rapid_mm_min)

    if not any(seg.end_program for seg in segments):
        segments.append(Segment(0.2, False, False, 0.0, feed, x, y, z, end_program=True))
    return segments


class GCodePlayback:
    """Replay a ForgeMill G-code cycle and halt at M30 / program end."""

    def __init__(self, program: str, sample_rate_hz: float = 2000, window_seconds: float = 0.25) -> None:
        self.segments = compile_program(program)
        if not self.segments:
            raise RuntimeError("No motion found in the ForgeMill G-code program.")
        self.sample_rate_hz = sample_rate_hz
        self.window_seconds = window_seconds
        self.t = 0.0
        self.seg_i = 0
        self.seg_t = 0.0
        self.done = False
        self.stop_reason = ""
        self.feed_override = 1.0
        self._temp = 28.0
        self._vb = 0.02
        self._rng = np.random.default_rng(11)
        cutter = re.search(r"(\d+(?:\.\d+)?)\s*mm cutter", program, re.I)
        self.tool_diameter_mm = float(cutter.group(1)) if cutter else 6.0
        self.teeth = 2 if self.tool_diameter_mm <= 8 else 4

    def cycle_time_s(self) -> float:
        return float(sum(seg.duration_s for seg in self.segments))

    def request_stop(self, reason: str = "") -> None:
        self.done = True
        self.stop_reason = reason or "operator stop"

    def apply_feed_override(self, factor: float) -> None:
        self.feed_override = float(np.clip(factor, 0.2, 1.5))

    def _current(self) -> Segment:
        return self.segments[min(self.seg_i, len(self.segments) - 1)]

    def step(self) -> SensorFrame:
        if self.done:
            raise RuntimeError(f"Cycle stop: {self.stop_reason or 'ForgeMill program ended (M30).'}")
        dt = self.window_seconds
        remaining = dt
        cutting = False
        rpm = 0.0
        feed_mm_min = 0.0
        x = y = z = 0.0
        while remaining > 1e-9 and not self.done:
            if self.seg_i >= len(self.segments):
                self.done = True
                self.stop_reason = "ForgeMill program ended (M30)."
                break
            seg = self.segments[self.seg_i]
            x, y, z = seg.x, seg.y, seg.z
            rpm = seg.rpm if seg.spindle else 0.0
            feed_mm_min = seg.feed_mm_min * self.feed_override
            cutting = seg.cutting and seg.spindle
            if seg.end_program:
                self.done = True
                self.stop_reason = "ForgeMill program ended (M30)."
                break
            left = max(seg.duration_s / max(self.feed_override, 0.2) - self.seg_t, 0.0)
            take = min(left, remaining)
            self.seg_t += take
            remaining -= take
            if self.seg_t >= seg.duration_s / max(self.feed_override, 0.2) - 1e-9:
                self.seg_i += 1
                self.seg_t = 0.0

        self.t += dt
        if self.done and self.t > 0.3:
            raise RuntimeError(f"Cycle stop: {self.stop_reason}")

        n = max(int(self.sample_rate_hz * self.window_seconds), 64)
        t_abs = self.t + np.arange(n) / self.sample_rate_hz
        tooth = max(rpm, 1.0) / 60.0 * self.teeth
        cut = 1.0 if cutting else 0.08
        vibration = (
            0.22 * cut * np.sin(2 * np.pi * tooth * t_abs)
            + 0.05 * np.sin(2 * np.pi * 2 * tooth * t_abs)
            + (0.04 + 0.18 * cut) * self._rng.normal(0.0, 1.0, n)
        ).astype(np.float32)
        force = (
            (40.0 + 180.0 * cut) * np.ones(n)
            + 12.0 * cut * np.sin(2 * np.pi * tooth * t_abs)
            + 6.0 * self._rng.normal(0.0, 1.0, n)
        ).astype(np.float32)
        vc = math.pi * (self.tool_diameter_mm / 1000.0) * max(rpm, 0.0)
        power = 160.0 + float(np.mean(np.abs(force))) * (vc / 60.0)
        target_temp = 27.0 + 18.0 * cut + 0.004 * max(rpm - 1000.0, 0.0)
        self._temp += 0.25 * (target_temp - self._temp)
        rate = 2.2 * cut * (max(rpm, 1.0) / 12000.0)
        self._vb = min(self._vb + rate * dt / 1000.0, 0.30)
        teeth_rpm = max(rpm * self.teeth, 1.0)
        feed_mm_tooth = feed_mm_min / teeth_rpm if rpm > 1 else 0.05
        wear_frac = self._vb / 0.30
        ra = 0.22 + 2.4 * feed_mm_tooth + 0.8 * wear_frac + 0.35 * cut
        return SensorFrame(
            time_s=self.t,
            vibration=vibration,
            force=force,
            temperature_c=float(self._temp),
            spindle_power_w=float(max(power, 0.0)),
            spindle_current_a=float(max(power / 220.0, 0.0)),
            cutting_speed_m_min=float(vc),
            feed_mm_tooth=float(feed_mm_tooth),
            rpm=float(rpm),
            sample_rate_hz=float(self.sample_rate_hz),
            source_name="forgemill",
            true_ra_um=float(max(ra, 0.2)),
            true_vb_mm=float(self._vb),
            true_wear_rate_um_s=float(rate),
            meta={
                "x": x,
                "y": y,
                "z": z,
                "cutting": cutting,
                "cycle_time_s": self.cycle_time_s(),
                "program_progress": min(self.seg_i / max(len(self.segments), 1), 1.0),
            },
        )
