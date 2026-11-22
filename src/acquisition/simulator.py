from __future__ import annotations

import math

import numpy as np

from .base import SensorFrame, SensorSource

# ISO 8688-style flank-wear limit used as 100% tool life in the demo.
VB_LIMIT_MM = 0.30


class SimulatedMillingSource(SensorSource):
    """Physics-inspired milling run with explicit wear, wear-rate and temperature.

    Flank wear VB grows with a Taylor-type rate (faster at higher Vc and feed).
    Temperature follows a first-order lag toward a power-and-wear steady state.
    Time is accelerated so a full wear curve fits in about one minute on screen.
    """

    name = "simulator"

    def __init__(
        self,
        sample_rate_hz: float = 5000,
        window_seconds: float = 0.25,
        spindle_rpm: float = 3000,
        teeth: int = 4,
        tool_diameter_mm: float = 10.0,
        feed_mm_tooth: float = 0.12,
        ra_spec_um: float = 1.6,
        failure_time_s: float = 42.0,
        seed: int = 7,
    ) -> None:
        self.sample_rate_hz = sample_rate_hz
        self.window_seconds = window_seconds
        self.spindle_rpm = spindle_rpm
        self.teeth = teeth
        self.tool_diameter_mm = tool_diameter_mm
        self.feed_mm_tooth = feed_mm_tooth
        self.ra_spec_um = ra_spec_um
        self.failure_time_s = failure_time_s
        self._rng = np.random.default_rng(seed)
        self._t = 0.0
        self._n = 0
        self._vb_mm = 0.02
        self._temp_c = 28.0
        self.stopped = False
        self.stop_reason = ""

    def open(self) -> None:
        self._t = 0.0
        self._n = 0
        self._vb_mm = 0.02 + 0.004 * float(self._rng.normal())
        self._temp_c = 27.0 + float(self._rng.normal())
        self.stopped = False
        self.stop_reason = ""

    def close(self) -> None:
        return

    def apply_overrides(self, *, feed_mm_tooth: float | None = None, rpm: float | None = None) -> None:
        if feed_mm_tooth is not None:
            self.feed_mm_tooth = float(max(feed_mm_tooth, 0.03))
        if rpm is not None:
            self.spindle_rpm = float(max(rpm, 800.0))

    def request_stop(self, reason: str = "") -> None:
        self.stopped = True
        self.stop_reason = reason or "supervisor stop"

    def _wear_rate_um_s(self, vc: float, chatter: float) -> float:
        # dVB/dt ∝ Vc^n · f^m · (1 + chatter + current wear). Scaled for a ~50 s demo life.
        return float(
            6.8
            * (vc / 94.0) ** 2.1
            * (self.feed_mm_tooth / 0.12) ** 1.3
            * (1.0 + 1.8 * chatter + 0.7 * (self._vb_mm / VB_LIMIT_MM))
        )

    def read_frame(self) -> SensorFrame:
        if self.stopped:
            raise RuntimeError(f"Cycle stop: {self.stop_reason}")
        n = int(self.sample_rate_hz * self.window_seconds)
        dt = 1.0 / self.sample_rate_hz
        t_abs = self._t + np.arange(n) * dt

        rpm = self.spindle_rpm
        f_spindle = rpm / 60.0
        f_tooth = f_spindle * self.teeth
        f_chatter = f_tooth * 1.37
        vc = math.pi * (self.tool_diameter_mm / 1000.0) * rpm
        wear_frac = float(np.clip(self._vb_mm / VB_LIMIT_MM, 0.0, 1.6))
        chatter_on = float(
            1.0
            / (1.0 + math.exp(-16.0 * (wear_frac - 0.62)))
            * min(self.feed_mm_tooth / 0.12, 1.4)
            * min(rpm / 3000.0, 1.3)
        )

        rate_um_s = self._wear_rate_um_s(vc, chatter_on)
        self._vb_mm = float(min(self._vb_mm + rate_um_s * self.window_seconds / 1000.0, 0.55))

        fc_mean = 170.0 + 950.0 * self.feed_mm_tooth + 120.0 * wear_frac
        force = (
            fc_mean
            + 18.0 * np.sin(2 * np.pi * f_tooth * t_abs)
            + 8.0 * np.sin(2 * np.pi * 2 * f_tooth * t_abs)
            + chatter_on * 55.0 * np.sin(2 * np.pi * f_chatter * t_abs)
            + (6.0 + 32.0 * wear_frac) * self._rng.normal(0.0, 1.0, n)
        )

        vibration = (
            0.32 * np.sin(2 * np.pi * f_tooth * t_abs)
            + 0.12 * np.sin(2 * np.pi * 2 * f_tooth * t_abs)
            + chatter_on * 1.85 * np.sin(2 * np.pi * f_chatter * t_abs)
            + wear_frac * 0.60 * np.sin(2 * np.pi * 3.1 * f_tooth * t_abs)
            + (0.08 + 0.50 * wear_frac) * self._rng.normal(0.0, 1.0, n)
        )

        vc_m_s = vc / 60.0
        cutting_power = float(np.mean(np.abs(force)) * vc_m_s)
        idle_power = 180.0
        spindle_power = idle_power + cutting_power + 12.0 * self._rng.normal()
        spindle_current = spindle_power / 220.0

        t_ss = 26.0 + 0.048 * cutting_power + 28.0 * wear_frac + 7.0 * chatter_on
        alpha = 1.0 - math.exp(-self.window_seconds / 2.4)
        self._temp_c = float(self._temp_c + alpha * (t_ss - self._temp_c) + 0.15 * self._rng.normal())

        ra = (
            0.18
            + 2.8 * self.feed_mm_tooth
            + 1.05 * wear_frac
            + 0.95 * chatter_on
            + 0.014 * max(self._temp_c - 38.0, 0.0)
            + 0.03 * self._rng.normal()
        )
        # ISO texture family from Ra (typical milled aluminium ratios, plus chatter peaks).
        rq = float(max(1.25 * ra + 0.02 * self._rng.normal(), 0.2))
        rz = float(max(5.1 * ra + 1.8 * chatter_on + 0.08 * self._rng.normal(), 0.8))
        rt = float(max(rz * (1.12 + 0.08 * chatter_on) + 0.05 * self._rng.normal(), rz))

        # Remaining useful life until ISO-style VB limit, from the current wear rate.
        rate_mm_s = max(rate_um_s / 1000.0, 1e-9)
        rul_s = float(max((VB_LIMIT_MM - self._vb_mm) / rate_mm_s, 0.0))
        # MRR ≈ ap · ae · vf ; ae ≈ 0.4 D for a typical slot/side cut in this demo.
        vf_mm_min = self.feed_mm_tooth * self.teeth * rpm
        mrr_cm3_min = float(1.0 * (0.4 * self.tool_diameter_mm) * vf_mm_min / 1000.0)

        frame = SensorFrame(
            time_s=self._t,
            vibration=vibration.astype(np.float32),
            force=force.astype(np.float32),
            temperature_c=float(self._temp_c),
            spindle_power_w=float(max(spindle_power, 0.0)),
            spindle_current_a=float(max(spindle_current, 0.0)),
            cutting_speed_m_min=float(vc),
            feed_mm_tooth=float(self.feed_mm_tooth),
            rpm=float(rpm),
            sample_rate_hz=float(self.sample_rate_hz),
            source_name=self.name,
            true_ra_um=float(max(ra, 0.2)),
            true_rq_um=rq,
            true_rz_um=rz,
            true_rt_um=rt,
            true_vb_mm=float(self._vb_mm),
            true_wear_rate_um_s=float(rate_um_s),
            true_rul_s=rul_s,
            true_chatter_hz=float(f_chatter if chatter_on > 0.15 else f_tooth),
            meta={
                "wear": wear_frac,
                "chatter": chatter_on,
                "tooth_freq_hz": f_tooth,
                "ra_spec_um": self.ra_spec_um,
                "vb_limit_mm": VB_LIMIT_MM,
                "mrr_cm3_min": mrr_cm3_min,
                "axial_depth_mm": 1.0,
            },
        )
        self._t += self.window_seconds
        self._n += 1
        return frame
