from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.ml.regimes import RegimeResult
from src.processing.features import FeatureVector


@dataclass
class DegradationForecast:
    probability: float
    time_to_degradation_s: float | None
    predicted_ra_um: float
    horizon_s: float
    contributions: dict[str, float]
    recommendation: str


def _sigmoid(x: float) -> float:
    return float(1.0 / (1.0 + np.exp(-x)))


def forecast_degradation(
    feat: FeatureVector,
    regime: RegimeResult,
    ra_spec_um: float = 1.6,
    horizon_s: float = 30.0,
) -> DegradationForecast:
    """Early-warning head: P(D_{t+Δt}=1 | recent features).

    Replace this logistic with a trained LSTM/TCN once labelled runs exist.
    Contributions are a local linear explanation (same idea as SHAP, but
    closed-form) so the dashboard can show *why* the alarm fired.
    """
    weights = {
        "Vibration RMS": 1.15 * feat.vib_rms,
        "Chatter-band energy": 3.4 * feat.chatter_band_energy,
        "Force fluctuation": 0.006 * feat.force_std,
        "Temperature": 0.025 * max(feat.temperature_c - 32.0, 0.0),
        "Spindle power": 0.0009 * max(feat.spindle_power_w - 250.0, 0.0),
        "Physics residual": 1.1 * feat.physics_residual,
        "Regime severity": 0.55 * regime.regime_id,
    }
    logit = -2.4 + sum(weights.values())
    probability = float(np.clip(_sigmoid(logit), 0.02, 0.98))

    predicted_ra = 0.50 + 0.85 * feat.vib_rms + 1.6 * feat.chatter_band_energy
    predicted_ra = float(np.clip(predicted_ra, 0.3, 4.0))

    if probability < 0.18:
        ttf: float | None = None
    else:
        # Higher probability → shorter remaining time inside the horizon.
        ttf = float(np.clip(horizon_s * (1.15 - probability), 2.0, horizon_s + 25.0))

    raw = {k: max(v, 0.0) for k, v in weights.items()}
    total = sum(raw.values()) + 1e-9
    contributions = {k: 100.0 * v / total for k, v in raw.items()}

    if probability < 0.25 and regime.regime_id == 0:
        rec = "Continue cutting. Signals are consistent with stable milling."
    elif probability < 0.55:
        rec = "Decision support: inspect chip colour and tool edge at the next safe stop. Do not change feed automatically."
    elif probability < 0.80:
        rec = "Decision support: consider reducing feed 8–10% or stopping to inspect the tool. Validate on the machine before acting."
    else:
        rec = "High surface-integrity risk. Stop at a programmed safe point and inspect tool and workpiece. Recommendation is advisory only."

    return DegradationForecast(
        probability=probability,
        time_to_degradation_s=ttf,
        predicted_ra_um=predicted_ra,
        horizon_s=horizon_s,
        contributions=contributions,
        recommendation=rec,
    )
