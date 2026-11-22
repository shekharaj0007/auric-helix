from __future__ import annotations

from dataclasses import dataclass

import yaml

from src.acquisition.base import SensorFrame, SensorSource
from src.acquisition.http_cnc import HttpCncSource
from src.acquisition.simulator import SimulatedMillingSource
from src.ml.model import MONITOR, DegradationForecast
from src.ml.regimes import RegimeResult
from src.processing.features import FeatureVector, extract_features
@dataclass
class MonitorResult:
    frame: SensorFrame
    features: FeatureVector
    regime: RegimeResult
    forecast: DegradationForecast
    degraded: bool


def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def make_source(cfg: dict) -> SensorSource:
    acq = cfg["acquisition"]
    proc = cfg["process"]
    source = acq.get("source", "simulator")
    if source == "serial":
        from src.acquisition.serial_arduino import SerialArduinoSource

        return SerialArduinoSource(
            port=acq.get("serial_port", "COM3"),
            baud=int(acq.get("serial_baud", 115200)),
            sample_rate_hz=float(acq.get("sample_rate_hz", 500)),
            window_seconds=float(acq.get("window_seconds", 0.25)),
            cutting_speed_m_min=3.1416 * proc["tool_diameter_mm"] * proc["spindle_rpm"] / 1000.0,
            feed_mm_tooth=float(proc["feed_mm_per_tooth"]),
            rpm=float(proc["spindle_rpm"]),
        )
    if source == "http":
        return HttpCncSource(
            base_url=str(acq.get("http_url", "http://127.0.0.1:8765")),
            window_seconds=float(acq.get("window_seconds", 0.25)),
            sample_rate_hz=min(float(acq.get("sample_rate_hz", 2000)), 2000),
        )
    return SimulatedMillingSource(
        sample_rate_hz=float(acq["sample_rate_hz"]),
        window_seconds=float(acq["window_seconds"]),
        spindle_rpm=float(proc["spindle_rpm"]),
        teeth=int(proc["teeth"]),
        tool_diameter_mm=float(proc["tool_diameter_mm"]),
        feed_mm_tooth=float(proc["feed_mm_per_tooth"]),
        ra_spec_um=float(proc["ra_spec_um"]),
    )


def infer(frame: SensorFrame, ra_spec_um: float, horizon_s: float) -> MonitorResult:
    features = extract_features(frame)
    regime, forecast = MONITOR.forecast(features, ra_spec_um=ra_spec_um, horizon_s=horizon_s)
    ra = frame.true_ra_um if frame.true_ra_um is not None else forecast.predicted_ra_um
    return MonitorResult(
        frame=frame,
        features=features,
        regime=regime,
        forecast=forecast,
        degraded=ra >= ra_spec_um or forecast.tool.vb_mm >= 0.30,
    )
