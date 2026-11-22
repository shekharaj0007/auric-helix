from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from src.acquisition.base import SensorFrame


@dataclass
class FeatureVector:
    time_s: float
    vib_rms: float
    vib_kurtosis: float
    vib_crest: float
    vib_skewness: float
    vib_peak_to_peak: float
    force_rms: float
    force_std: float
    spectral_centroid_hz: float
    peak_freq_hz: float
    tooth_band_energy: float
    chatter_band_energy: float
    chatter_to_tooth_ratio: float
    spectral_entropy: float
    temperature_c: float
    spindle_power_w: float
    spindle_current_a: float
    physics_residual: float
    cutting_speed_m_min: float
    feed_mm_tooth: float
    mrr_cm3_min: float
    specific_energy_j_mm3: float

    def as_array(self) -> np.ndarray:
        return np.array(
            [
                self.vib_rms,
                self.vib_kurtosis,
                self.vib_crest,
                self.force_rms,
                self.force_std,
                self.chatter_band_energy,
                self.spectral_entropy,
                self.temperature_c,
                self.spindle_power_w,
                self.physics_residual,
                self.vib_skewness,
                self.peak_freq_hz,
                self.chatter_to_tooth_ratio,
                self.mrr_cm3_min,
                self.specific_energy_j_mm3,
                self.tooth_band_energy,
            ],
            dtype=np.float32,
        )

    def to_dict(self) -> dict:
        return asdict(self)


def _kurtosis(x: np.ndarray) -> float:
    x = x - np.mean(x)
    m2 = np.mean(x**2) + 1e-12
    m4 = np.mean(x**4)
    return float(m4 / (m2**2))


def _skewness(x: np.ndarray) -> float:
    x = x - np.mean(x)
    m2 = np.mean(x**2) + 1e-12
    m3 = np.mean(x**3)
    return float(m3 / (m2**1.5))


def _crest(x: np.ndarray) -> float:
    rms = float(np.sqrt(np.mean(x**2)) + 1e-12)
    return float(np.max(np.abs(x)) / rms)


def _spectrum(x: np.ndarray, fs: float) -> tuple[np.ndarray, np.ndarray]:
    x = x - np.mean(x)
    n = len(x)
    window = np.hanning(n)
    spec = np.abs(np.fft.rfft(x * window)) / n
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    return freqs, spec


def _band_energy(freqs: np.ndarray, spec: np.ndarray, lo: float, hi: float) -> float:
    mask = (freqs >= lo) & (freqs < hi)
    if not np.any(mask):
        return 0.0
    return float(np.sum(spec[mask] ** 2))


def extract_features(frame: SensorFrame) -> FeatureVector:
    vib = np.asarray(frame.vibration, dtype=np.float64)
    force = np.asarray(frame.force, dtype=np.float64)
    fs = frame.sample_rate_hz

    freqs, spec = _spectrum(vib, fs)
    power_spec = spec**2 + 1e-15
    centroid = float(np.sum(freqs * power_spec) / np.sum(power_spec))
    p = power_spec / np.sum(power_spec)
    entropy = float(-np.sum(p * np.log(p)))
    peak_hz = float(freqs[int(np.argmax(spec))]) if len(spec) else 0.0

    tooth = float(frame.meta.get("tooth_freq_hz", frame.rpm / 60.0 * 4.0))
    tooth_e = _band_energy(freqs, spec, max(tooth - 15, 0), tooth + 15)
    chatter_e = _band_energy(freqs, spec, tooth * 1.2, tooth * 1.8)
    ratio = chatter_e / (tooth_e + 1e-12)

    fc = float(np.mean(np.abs(force)))
    vc_m_s = frame.cutting_speed_m_min / 60.0
    residual = abs(frame.spindle_power_w - (180.0 + fc * vc_m_s)) / max(frame.spindle_power_w, 1.0)

    mrr = float(frame.meta.get("mrr_cm3_min", 0.0))
    if mrr <= 0.0:
        vf_mm_min = frame.feed_mm_tooth * 4.0 * frame.rpm
        mrr = float(1.0 * (0.4 * 10.0) * vf_mm_min / 1000.0)
    # specific cutting energy u = P / (MRR); convert cm3/min → mm3/s
    mrr_mm3_s = mrr * 1000.0 / 60.0
    u_j_mm3 = float(frame.spindle_power_w / max(mrr_mm3_s, 1e-6))

    return FeatureVector(
        time_s=frame.time_s,
        vib_rms=float(np.sqrt(np.mean(vib**2))),
        vib_kurtosis=_kurtosis(vib),
        vib_crest=_crest(vib),
        vib_skewness=_skewness(vib),
        vib_peak_to_peak=float(np.ptp(vib)),
        force_rms=float(np.sqrt(np.mean(force**2))),
        force_std=float(np.std(force)),
        spectral_centroid_hz=centroid,
        peak_freq_hz=peak_hz,
        tooth_band_energy=tooth_e,
        chatter_band_energy=chatter_e,
        chatter_to_tooth_ratio=float(ratio),
        spectral_entropy=entropy,
        temperature_c=frame.temperature_c,
        spindle_power_w=frame.spindle_power_w,
        spindle_current_a=frame.spindle_current_a,
        physics_residual=float(residual),
        cutting_speed_m_min=frame.cutting_speed_m_min,
        feed_mm_tooth=frame.feed_mm_tooth,
        mrr_cm3_min=mrr,
        specific_energy_j_mm3=u_j_mm3,
    )
