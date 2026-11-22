from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
    IsolationForest,
)
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.acquisition.simulator import SimulatedMillingSource, VB_LIMIT_MM
from src.ml.regimes import REGIME_COLORS, REGIME_NAMES, RegimeResult
from src.processing.features import FeatureVector, extract_features

FEATURE_NAMES = [
    "Vibration RMS",
    "Kurtosis",
    "Crest factor",
    "Force RMS",
    "Force fluctuation",
    "Chatter-band energy",
    "Spectral entropy",
    "Temperature",
    "Spindle power",
    "Physics residual",
    "Vibration skewness",
    "Peak frequency",
    "Chatter / tooth ratio",
    "MRR",
    "Specific cutting energy",
    "Tooth-band energy",
]

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "advanced_monitor.npz"
DATASET_PATH = ROOT / "data" / "simulated_milling_dataset.csv"
METRICS_PATH = ROOT / "data" / "training_metrics.txt"

# Factorial process window: rpm × feed × replicate. Physics-simulated, not lab.
TRAIN_CONDITIONS = [
    {"spindle_rpm": 2400, "feed_mm_tooth": 0.08, "seed": 11},
    {"spindle_rpm": 2400, "feed_mm_tooth": 0.12, "seed": 12},
    {"spindle_rpm": 2400, "feed_mm_tooth": 0.16, "seed": 13},
    {"spindle_rpm": 3000, "feed_mm_tooth": 0.08, "seed": 21},
    {"spindle_rpm": 3000, "feed_mm_tooth": 0.12, "seed": 22},
    {"spindle_rpm": 3000, "feed_mm_tooth": 0.16, "seed": 23},
    {"spindle_rpm": 3600, "feed_mm_tooth": 0.08, "seed": 31},
    {"spindle_rpm": 3600, "feed_mm_tooth": 0.12, "seed": 32},
    {"spindle_rpm": 3600, "feed_mm_tooth": 0.16, "seed": 33},
    {"spindle_rpm": 2700, "feed_mm_tooth": 0.14, "seed": 41},
    {"spindle_rpm": 3300, "feed_mm_tooth": 0.10, "seed": 42},
    {"spindle_rpm": 3300, "feed_mm_tooth": 0.18, "seed": 43},
]


@dataclass
class ToolState:
    vb_mm: float
    wear_rate_um_s: float
    wear_rate_um_min: float
    tool_health_pct: float
    stage: str
    temperature_c: float
    predicted_temperature_c: float
    remaining_life_s: float | None = None
    anomaly_score: float = 0.0
    mrr_cm3_min: float = 0.0
    specific_energy_j_mm3: float = 0.0


@dataclass
class SurfaceTexture:
    """ISO-style texture family. Ra is the B.Tech integrity proxy; others are extra heads."""

    ra_um: float
    rq_um: float
    rz_um: float
    rt_um: float
    chatter_hz: float
    form_error_um: float


@dataclass
class DegradationForecast:
    probability: float
    time_to_degradation_s: float | None
    predicted_ra_um: float
    horizon_s: float
    contributions: dict[str, float]
    recommendation: str
    tool: ToolState
    trained_on: str
    texture: SurfaceTexture | None = None


class AdvancedMonitor:
    """GMM regimes + HGB heads + isolation-forest anomaly + RUL.

    Trained on a physics-simulated multimodal milling dataset. Replace the CSV
    with measured Ra / microscope VB for laboratory results.
    """

    def __init__(self) -> None:
        self.gmm: GaussianMixture | None = None
        self.component_order: np.ndarray | None = None
        self.wear_model: Pipeline | None = None
        self.rate_model: Pipeline | None = None
        self.ra_model: Pipeline | None = None
        self.temp_model: Pipeline | None = None
        self.risk_model: Pipeline | None = None
        self.rul_model: Pipeline | None = None
        self.rq_model: Pipeline | None = None
        self.rz_model: Pipeline | None = None
        self.rt_model: Pipeline | None = None
        self.chatter_model: Pipeline | None = None
        self.anomaly: IsolationForest | None = None
        self.risk_importance: np.ndarray | None = None
        self.metrics: dict[str, float] = {}
        self.n_samples = 0
        self.trained_on = "untrained"
        self._gmm_scaler: StandardScaler | None = None

    def is_ready(self) -> bool:
        return self.gmm is not None and self.wear_model is not None and self.rul_model is not None and self.rq_model is not None

    def train(self, ra_spec_um: float = 1.6, horizon_s: float = 30.0) -> None:
        rows: list[dict] = []
        x_list: list[np.ndarray] = []
        vb_list: list[float] = []
        rate_list: list[float] = []
        ra_list: list[float] = []
        rq_list: list[float] = []
        rz_list: list[float] = []
        rt_list: list[float] = []
        chatter_list: list[float] = []
        temp_list: list[float] = []
        rul_list: list[float] = []
        future_d: list[int] = []
        look_ahead = int(horizon_s / 0.25)

        for cond in TRAIN_CONDITIONS:
            src = SimulatedMillingSource(
                sample_rate_hz=2000,
                window_seconds=0.25,
                spindle_rpm=float(cond["spindle_rpm"]),
                feed_mm_tooth=float(cond["feed_mm_tooth"]),
                ra_spec_um=ra_spec_um,
                seed=int(cond["seed"]),
            )
            src.open()
            feats: list[np.ndarray] = []
            ras: list[float] = []
            rqs: list[float] = []
            rzs: list[float] = []
            rts: list[float] = []
            chatters: list[float] = []
            vbs: list[float] = []
            rates: list[float] = []
            temps: list[float] = []
            ruls: list[float] = []
            feat_dicts: list[dict] = []
            for _ in range(240):
                frame = src.read_frame()
                feat = extract_features(frame)
                feats.append(feat.as_array())
                ras.append(float(frame.true_ra_um or 0.5))
                rqs.append(float(frame.true_rq_um or 1.25 * ras[-1]))
                rzs.append(float(frame.true_rz_um or 5.1 * ras[-1]))
                rts.append(float(frame.true_rt_um or 1.15 * rzs[-1]))
                chatters.append(float(frame.true_chatter_hz or feat.peak_freq_hz))
                vbs.append(float(frame.true_vb_mm or 0.02))
                rates.append(float(frame.true_wear_rate_um_s or 0.0))
                temps.append(frame.temperature_c)
                ruls.append(float(frame.true_rul_s or 0.0))
                feat_dicts.append(feat.to_dict())
            src.close()
            n = len(feats)
            for i in range(n):
                j = min(i + look_ahead, n - 1)
                x_list.append(feats[i])
                vb_list.append(vbs[i])
                rate_list.append(rates[i])
                ra_list.append(ras[i])
                rq_list.append(rqs[i])
                rz_list.append(rzs[i])
                rt_list.append(rts[i])
                chatter_list.append(chatters[i])
                temp_list.append(temps[i])
                rul_list.append(ruls[i])
                degraded = int(ras[j] >= ra_spec_um or vbs[j] >= VB_LIMIT_MM)
                future_d.append(degraded)
                row = {
                    "run_id": cond["seed"],
                    "spindle_rpm": cond["spindle_rpm"],
                    "feed_mm_tooth": cond["feed_mm_tooth"],
                    "window_index": i,
                    **feat_dicts[i],
                    "label_ra_um": ras[i],
                    "label_rq_um": rqs[i],
                    "label_rz_um": rzs[i],
                    "label_rt_um": rts[i],
                    "label_chatter_hz": chatters[i],
                    "label_vb_mm": vbs[i],
                    "label_wear_rate_um_s": rates[i],
                    "label_rul_s": ruls[i],
                    "label_degrade_in_horizon": degraded,
                }
                rows.append(row)

        x = np.vstack(x_list)
        y_vb = np.asarray(vb_list)
        y_rate = np.asarray(rate_list)
        y_ra = np.asarray(ra_list)
        y_rq = np.asarray(rq_list)
        y_rz = np.asarray(rz_list)
        y_rt = np.asarray(rt_list)
        y_ch = np.asarray(chatter_list)
        y_temp = np.asarray(temp_list)
        y_rul = np.asarray(rul_list)
        y_risk = np.asarray(future_d)
        self.n_samples = len(x)

        self._export_dataset(rows)

        scaler_gmm = StandardScaler()
        xs = scaler_gmm.fit_transform(x)
        self.gmm = GaussianMixture(n_components=4, covariance_type="full", random_state=7, n_init=3)
        labels = self.gmm.fit_predict(xs)
        severity = []
        for k in range(4):
            mask = labels == k
            col = x[mask][:, [0, 5]].mean(axis=0) if np.any(mask) else np.zeros(2)
            severity.append(float(col[0] + 3.0 * col[1]))
        self.component_order = np.argsort(np.asarray(severity))
        self._gmm_scaler = scaler_gmm

        def _reg() -> Pipeline:
            return Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "hgb",
                        HistGradientBoostingRegressor(
                            max_depth=4,
                            max_iter=140,
                            learning_rate=0.08,
                            l2_regularization=0.1,
                            random_state=7,
                        ),
                    ),
                ]
            )

        (
            x_tr, x_te, vb_tr, vb_te, ra_tr, ra_te, rq_tr, rq_te, rz_tr, rz_te,
            rt_tr, rt_te, ch_tr, ch_te, rate_tr, rate_te, t_tr, t_te, rul_tr, rul_te, d_tr, d_te,
        ) = train_test_split(
            x, y_vb, y_ra, y_rq, y_rz, y_rt, y_ch, y_rate, y_temp, y_rul, y_risk,
            test_size=0.2, random_state=7,
        )

        self.wear_model = _reg()
        self.wear_model.fit(x_tr, vb_tr)
        self.rate_model = _reg()
        self.rate_model.fit(x_tr, rate_tr)
        self.ra_model = _reg()
        self.ra_model.fit(x_tr, ra_tr)
        self.rq_model = _reg()
        self.rq_model.fit(x_tr, rq_tr)
        self.rz_model = _reg()
        self.rz_model.fit(x_tr, rz_tr)
        self.rt_model = _reg()
        self.rt_model.fit(x_tr, rt_tr)
        self.chatter_model = _reg()
        self.chatter_model.fit(x_tr, ch_tr)
        self.temp_model = _reg()
        self.temp_model.fit(x_tr, t_tr)
        self.rul_model = _reg()
        self.rul_model.fit(x_tr, rul_tr)
        self.risk_model = Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "hgb",
                    HistGradientBoostingClassifier(
                        max_depth=4,
                        max_iter=140,
                        learning_rate=0.08,
                        l2_regularization=0.1,
                        random_state=7,
                    ),
                ),
            ]
        )
        self.risk_model.fit(x_tr, d_tr)

        # Anomaly model is fit on the more-stable half of the cloud.
        stable = x[y_risk == 0] if np.any(y_risk == 0) else x
        self.anomaly = IsolationForest(n_estimators=160, contamination=0.08, random_state=7)
        self.anomaly.fit(stable)

        imp = permutation_importance(self.risk_model, x_te, d_te, n_repeats=6, random_state=7, scoring="roc_auc")
        self.risk_importance = np.clip(imp.importances_mean, 0.0, None)

        self.metrics = {
            "mae_ra_um": float(mean_absolute_error(ra_te, self.ra_model.predict(x_te))),
            "mae_rq_um": float(mean_absolute_error(rq_te, self.rq_model.predict(x_te))),
            "mae_rz_um": float(mean_absolute_error(rz_te, self.rz_model.predict(x_te))),
            "mae_rt_um": float(mean_absolute_error(rt_te, self.rt_model.predict(x_te))),
            "mae_chatter_hz": float(mean_absolute_error(ch_te, self.chatter_model.predict(x_te))),
            "mae_vb_mm": float(mean_absolute_error(vb_te, self.wear_model.predict(x_te))),
            "mae_rate_um_s": float(mean_absolute_error(rate_te, self.rate_model.predict(x_te))),
            "mae_rul_s": float(mean_absolute_error(rul_te, self.rul_model.predict(x_te))),
            "auc_risk": float(roc_auc_score(d_te, self.risk_model.predict_proba(x_te)[:, 1])),
            "n_train": float(len(x_tr)),
            "n_test": float(len(x_te)),
        }
        self.trained_on = (
            f"{self.n_samples} windows · {len(TRAIN_CONDITIONS)} Al 6061 speed/feed runs · "
            f"physics-simulated multimodal dataset (not lab) · "
            f"test MAE Ra {self.metrics['mae_ra_um']:.3f} µm · AUC {self.metrics['auc_risk']:.3f}"
        )
        self._write_metrics()
        self._save()

    def _export_dataset(self, rows: list[dict]) -> None:
        import csv

        DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
        keys = list(rows[0].keys())
        with DATASET_PATH.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

    def _write_metrics(self) -> None:
        METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "Training metrics on a held-out 20% of the simulated milling dataset.",
            "These numbers are NOT laboratory profilometer / microscope results.",
            "",
        ]
        for k, v in self.metrics.items():
            lines.append(f"{k} = {v:.4f}")
        METRICS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _save(self) -> None:
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        import pickle

        payload = {
            "version": 3,
            "gmm": self.gmm,
            "gmm_scaler": self._gmm_scaler,
            "component_order": self.component_order,
            "wear": self.wear_model,
            "rate": self.rate_model,
            "ra": self.ra_model,
            "rq": self.rq_model,
            "rz": self.rz_model,
            "rt": self.rt_model,
            "chatter": self.chatter_model,
            "temp": self.temp_model,
            "risk": self.risk_model,
            "rul": self.rul_model,
            "anomaly": self.anomaly,
            "risk_importance": self.risk_importance,
            "n_samples": self.n_samples,
            "trained_on": self.trained_on,
            "metrics": self.metrics,
        }
        with (MODEL_PATH.parent / "advanced_monitor.pkl").open("wb") as handle:
            pickle.dump(payload, handle)

    def load(self) -> bool:
        path = MODEL_PATH.parent / "advanced_monitor.pkl"
        if not path.exists():
            return False
        import pickle

        with path.open("rb") as handle:
            payload = pickle.load(handle)
        if payload.get("version", 1) < 3 or "rq" not in payload:
            return False
        self.gmm = payload["gmm"]
        self._gmm_scaler = payload["gmm_scaler"]
        self.component_order = payload["component_order"]
        self.wear_model = payload["wear"]
        self.rate_model = payload["rate"]
        self.ra_model = payload["ra"]
        self.rq_model = payload["rq"]
        self.rz_model = payload["rz"]
        self.rt_model = payload["rt"]
        self.chatter_model = payload["chatter"]
        self.temp_model = payload["temp"]
        self.risk_model = payload["risk"]
        self.rul_model = payload["rul"]
        self.anomaly = payload.get("anomaly")
        self.risk_importance = payload.get("risk_importance")
        self.n_samples = payload["n_samples"]
        self.trained_on = payload["trained_on"]
        self.metrics = payload.get("metrics", {})
        return True

    def ensure_trained(self, ra_spec_um: float = 1.6, horizon_s: float = 30.0) -> None:
        if self.is_ready():
            return
        if self.load():
            return
        self.train(ra_spec_um=ra_spec_um, horizon_s=horizon_s)

    def _regime(self, x: np.ndarray) -> RegimeResult:
        assert self.gmm is not None and self.component_order is not None
        xs = self._gmm_scaler.transform(x.reshape(1, -1))
        proba = self.gmm.predict_proba(xs)[0]
        raw = int(np.argmax(proba))
        rid = int(np.where(self.component_order == raw)[0][0])
        return RegimeResult(
            regime_id=rid,
            name=REGIME_NAMES[rid],
            confidence=float(proba[raw]),
            color=REGIME_COLORS[rid],
        )

    def _contributions(self, feat: FeatureVector) -> dict[str, float]:
        x = feat.as_array()
        if self.risk_importance is not None and len(self.risk_importance) == len(x):
            raw = {FEATURE_NAMES[i]: float(abs(x[i]) * (self.risk_importance[i] + 1e-6)) for i in range(len(x))}
        else:
            raw = {
                "Vibration RMS": 1.2 * feat.vib_rms,
                "Chatter-band energy": 3.2 * feat.chatter_band_energy,
                "Force fluctuation": 0.006 * feat.force_std,
                "Temperature": 0.035 * max(feat.temperature_c - 32.0, 0.0),
                "Spindle power": 0.0008 * max(feat.spindle_power_w - 250.0, 0.0),
                "Physics residual": 1.0 * feat.physics_residual,
                "Specific cutting energy": 0.15 * feat.specific_energy_j_mm3,
                "Chatter / tooth ratio": 0.8 * feat.chatter_to_tooth_ratio,
            }
        total = sum(max(v, 0.0) for v in raw.values()) + 1e-9
        ranked = sorted(((k, 100.0 * max(v, 0.0) / total) for k, v in raw.items()), key=lambda kv: -kv[1])
        return dict(ranked[:8])

    def forecast(self, feat: FeatureVector, ra_spec_um: float, horizon_s: float) -> tuple[RegimeResult, DegradationForecast]:
        self.ensure_trained(ra_spec_um, horizon_s)
        x = feat.as_array()
        xx = x.reshape(1, -1)
        regime = self._regime(x)
        vb = float(np.clip(self.wear_model.predict(xx)[0], 0.01, 0.55))
        rate = float(max(self.rate_model.predict(xx)[0], 0.0))
        ra = float(np.clip(self.ra_model.predict(xx)[0], 0.25, 4.0))
        rq = float(np.clip(self.rq_model.predict(xx)[0], 0.25, 6.0))
        rz = float(np.clip(self.rz_model.predict(xx)[0], 0.8, 20.0))
        rt = float(np.clip(self.rt_model.predict(xx)[0], rz, 24.0))
        chatter_hz = float(max(self.chatter_model.predict(xx)[0], 0.0))
        form_err = float(max(0.35 * (rz - 5.1 * ra) + 0.8 * feat.chatter_to_tooth_ratio, 0.0))
        t_hat = float(self.temp_model.predict(xx)[0])
        rul = float(max(self.rul_model.predict(xx)[0], 0.0))
        proba = float(self.risk_model.predict_proba(xx)[0, 1])
        proba = float(np.clip(proba, 0.02, 0.98))
        if self.anomaly is not None:
            # decision_function: higher = more normal. Map to 0–1 anomaly.
            raw_if = float(self.anomaly.decision_function(xx)[0])
            anomaly = float(np.clip(0.5 - raw_if, 0.0, 1.0))
        else:
            anomaly = 0.0
        health = float(np.clip(100.0 * (1.0 - vb / VB_LIMIT_MM), 0.0, 100.0))
        if rate < 4.0 and vb < 0.12:
            stage = "Initial wear"
        elif rate < 10.0 and vb < 0.22:
            stage = "Steady wear"
        else:
            stage = "Accelerated wear"

        ttf = None if proba < 0.18 else float(np.clip(horizon_s * (1.15 - proba), 2.0, horizon_s + 25.0))

        if proba < 0.25 and regime.regime_id == 0:
            rec = "Continue cutting. Wear rate and temperature are consistent with stable milling."
        elif proba < 0.55:
            rec = (
                f"Decision support: flank wear ~{vb:.2f} mm, wear rate {rate:.1f} μm/s, "
                f"RUL ~{rul:.0f} s. Inspect the edge at the next safe stop."
            )
        elif proba < 0.80:
            rec = (
                "Decision support: wear is accelerating and surface risk is rising. "
                "Consider reducing feed 8–10% or changing the tool. Advisory only."
            )
        else:
            rec = (
                "High surface-integrity risk. Stop at a programmed safe point; inspect tool VB and the workpiece. "
                "Do not auto-change feed."
            )

        tool = ToolState(
            vb_mm=vb,
            wear_rate_um_s=rate,
            wear_rate_um_min=rate * 60.0,
            tool_health_pct=health,
            stage=stage,
            temperature_c=feat.temperature_c,
            predicted_temperature_c=t_hat,
            remaining_life_s=rul,
            anomaly_score=anomaly,
            mrr_cm3_min=feat.mrr_cm3_min,
            specific_energy_j_mm3=feat.specific_energy_j_mm3,
        )
        forecast = DegradationForecast(
            probability=proba,
            time_to_degradation_s=ttf,
            predicted_ra_um=ra,
            horizon_s=horizon_s,
            contributions=self._contributions(feat),
            recommendation=rec,
            tool=tool,
            trained_on=self.trained_on,
            texture=SurfaceTexture(
                ra_um=ra,
                rq_um=rq,
                rz_um=rz,
                rt_um=rt,
                chatter_hz=chatter_hz,
                form_error_um=form_err,
            ),
        )
        return regime, forecast


MONITOR = AdvancedMonitor()
