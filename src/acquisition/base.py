from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np


@dataclass
class SensorFrame:
    """One analysis window from the machine.

    Live sensors (vibration, force, current, temperature) arrive from DAQ
    hardware. Surface roughness Ra is usually measured offline with a
    profilometer and is therefore optional / delayed ground truth, not a
    live stream.
    """

    time_s: float
    vibration: np.ndarray
    force: np.ndarray
    temperature_c: float
    spindle_power_w: float
    spindle_current_a: float
    cutting_speed_m_min: float
    feed_mm_tooth: float
    rpm: float
    sample_rate_hz: float
    source_name: str
    true_ra_um: float | None = None
    true_rq_um: float | None = None
    true_rz_um: float | None = None
    true_rt_um: float | None = None
    true_vb_mm: float | None = None
    true_wear_rate_um_s: float | None = None
    true_rul_s: float | None = None
    true_chatter_hz: float | None = None
    meta: dict = field(default_factory=dict)


class SensorSource(ABC):
    """Swap simulator → Arduino serial → NI-DAQ without changing the ML."""

    name: str

    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def read_frame(self) -> SensorFrame: ...

    @abstractmethod
    def close(self) -> None: ...

    def __enter__(self) -> SensorSource:
        self.open()
        return self

    def apply_overrides(self, *, feed_mm_tooth: float | None = None, rpm: float | None = None) -> None:
        """Optional CNC override. Simulator changes cutting conditions; serial emits CMD lines."""
        return

    def request_stop(self, reason: str = "") -> None:
        """Optional feed-hold / cycle-stop. Simulator flags stopped; serial emits CMD,STOP."""
        return
