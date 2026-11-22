from __future__ import annotations

import time

import numpy as np

from .base import SensorFrame, SensorSource


class SerialArduinoSource(SensorSource):
    """Read CSV lines from an Arduino/ESP32 DAQ.

    Expected line format (115200 baud):

        millis,vibration,current_a,temperature_c[,force_n]

    Vibration is a single sample per line. The reader buffers samples until
    one analysis window is full, then returns a SensorFrame. Force is optional;
    if absent, a physics estimate from current and cutting speed is used.
    """

    name = "serial"

    def __init__(
        self,
        port: str = "COM3",
        baud: int = 115200,
        sample_rate_hz: float = 500,
        window_seconds: float = 0.25,
        cutting_speed_m_min: float = 94.2,
        feed_mm_tooth: float = 0.12,
        rpm: float = 3000,
    ) -> None:
        self.port = port
        self.baud = baud
        self.sample_rate_hz = sample_rate_hz
        self.window_seconds = window_seconds
        self.cutting_speed_m_min = cutting_speed_m_min
        self.feed_mm_tooth = feed_mm_tooth
        self.rpm = rpm
        self._ser = None
        self._t0 = None
        self.stopped = False

    def open(self) -> None:
        try:
            import serial  # type: ignore
        except ImportError as exc:
            raise RuntimeError("pyserial is required for the Arduino source") from exc

        self._ser = serial.Serial(self.port, self.baud, timeout=1)
        time.sleep(2.0)
        self._t0 = time.time()
        self.stopped = False

    def close(self) -> None:
        if self._ser is not None:
            self._ser.close()
            self._ser = None

    def _send(self, line: str) -> None:
        if self._ser is None:
            return
        self._ser.write((line.strip() + "\n").encode("utf-8"))

    def apply_overrides(self, *, feed_mm_tooth: float | None = None, rpm: float | None = None) -> None:
        if feed_mm_tooth is not None:
            self.feed_mm_tooth = float(feed_mm_tooth)
            self._send(f"CMD,FEED,{self.feed_mm_tooth:.4f}")
        if rpm is not None:
            self.rpm = float(rpm)
            self._send(f"CMD,RPM,{self.rpm:.0f}")

    def request_stop(self, reason: str = "") -> None:
        self.stopped = True
        self._send(f"CMD,STOP,{reason}")

    def _parse_line(self, line: str) -> tuple[float, float, float, float | None] | None:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 4:
            return None
        try:
            vib = float(parts[1])
            current = float(parts[2])
            temp = float(parts[3])
            force = float(parts[4]) if len(parts) >= 5 else None
        except ValueError:
            return None
        return vib, current, temp, force

    def read_frame(self) -> SensorFrame:
        if self.stopped:
            raise RuntimeError("Cycle stop requested on serial link")
        if self._ser is None:
            raise RuntimeError("Serial port is not open")

        n = max(int(self.sample_rate_hz * self.window_seconds), 32)
        vib: list[float] = []
        cur: list[float] = []
        tmp: list[float] = []
        frc: list[float] = []

        while len(vib) < n:
            raw = self._ser.readline().decode("utf-8", errors="ignore").strip()
            parsed = self._parse_line(raw)
            if parsed is None:
                continue
            v, c, t, f = parsed
            vib.append(v)
            cur.append(c)
            tmp.append(t)
            if f is not None:
                frc.append(f)

        vibration = np.asarray(vib, dtype=np.float32)
        current = float(np.mean(cur))
        temperature = float(np.mean(tmp))
        power = current * 220.0
        vc_m_s = self.cutting_speed_m_min / 60.0
        if frc:
            force = np.asarray(frc, dtype=np.float32)
        else:
            # If no dynamometer, invert P ≈ Fc * Vc as a soft estimate.
            fc_est = power / max(vc_m_s, 1e-3)
            force = np.full(len(vibration), fc_est, dtype=np.float32)

        t_now = time.time() - (self._t0 or time.time())
        return SensorFrame(
            time_s=float(t_now),
            vibration=vibration,
            force=force,
            temperature_c=temperature,
            spindle_power_w=float(power),
            spindle_current_a=current,
            cutting_speed_m_min=self.cutting_speed_m_min,
            feed_mm_tooth=self.feed_mm_tooth,
            rpm=self.rpm,
            sample_rate_hz=self.sample_rate_hz,
            source_name=f"serial:{self.port}",
            true_ra_um=None,
        )
