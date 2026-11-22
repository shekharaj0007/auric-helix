from __future__ import annotations

from dataclasses import dataclass

from src.processing.features import FeatureVector

REGIME_NAMES = {
    0: "Regime A — Stable cutting",
    1: "Regime B — Transitional",
    2: "Regime C — Unstable machining",
    3: "Regime D — Severe degradation",
}

REGIME_COLORS = {
    0: "#3D9A6A",
    1: "#C48A1A",
    2: "#D15A2A",
    3: "#C43A3A",
}


@dataclass
class RegimeResult:
    regime_id: int
    name: str
    confidence: float
    color: str


def assign_regime(feat: FeatureVector) -> RegimeResult:
    """Rule-assisted regime map.

    In the full research pipeline this is replaced by GMM/HDBSCAN/VAE
    clustering of unlabeled latent Z. The rules here are a transparent
    stand-in so the dashboard runs before a trained clusterer exists.
    They use the same features the unsupervised model would see.
    """
    chatter = feat.chatter_band_energy
    vib = feat.vib_rms
    force_fluct = feat.force_std

    score = 0.55 * vib + 2.2 * chatter + 0.004 * force_fluct + 0.8 * feat.physics_residual

    if score < 0.45:
        rid, conf = 0, min(0.93, 0.70 + (0.45 - score))
    elif score < 0.90:
        rid, conf = 1, 0.62 + 0.25 * (score - 0.45) / 0.45
    elif score < 1.55:
        rid, conf = 2, 0.68 + 0.20 * (score - 0.90) / 0.65
    else:
        rid, conf = 3, min(0.96, 0.75 + 0.1 * (score - 1.55))

    return RegimeResult(
        regime_id=rid,
        name=REGIME_NAMES[rid],
        confidence=float(min(conf, 0.97)),
        color=REGIME_COLORS[rid],
    )
