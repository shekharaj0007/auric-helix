"""Append a JSONL record of where the mill was held and what the monitor saw."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "data" / "stop_log.jsonl"


def write_stop_record(record: dict) -> dict:
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **record,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")
    return payload


def _num(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


def record_from_result(result, xyz: dict, reason: str) -> dict:
    fc = result.forecast
    tool = fc.tool
    tex = getattr(fc, "texture", None)
    feat = result.features
    ra_used = getattr(result.frame, "true_ra_um", None)
    if ra_used is None:
        ra_used = fc.predicted_ra_um
    contrib = {str(k): float(v) for k, v in (getattr(fc, "contributions", None) or {}).items()}
    return {
        "reason": reason,
        "x_mm": _num(xyz.get("x")),
        "y_mm": _num(xyz.get("y")),
        "z_mm": _num(xyz.get("z")),
        "time_s": _num(getattr(result.frame, "time_s", None)),
        "rpm": _num(getattr(result.frame, "rpm", None)),
        "feed_mm_tooth": _num(getattr(result.frame, "feed_mm_tooth", None)),
        "regime": result.regime.name,
        "ra_um": _num(ra_used),
        "rq_um": _num(getattr(tex, "rq_um", None)),
        "rz_um": _num(getattr(tex, "rz_um", None)),
        "rt_um": _num(getattr(tex, "rt_um", None)),
        "form_error_um": _num(getattr(tex, "form_error_um", None)),
        "chatter_hz": _num(getattr(tex, "chatter_hz", None)),
        "vb_mm": _num(tool.vb_mm),
        "wear_rate_um_s": _num(tool.wear_rate_um_s),
        "temperature_c": _num(tool.temperature_c),
        "risk": _num(fc.probability),
        "rul_s": _num(getattr(tool, "remaining_life_s", None)),
        "power_w": _num(feat.spindle_power_w),
        "vib_rms": _num(feat.vib_rms),
        "force_rms": _num(feat.force_rms),
        "mrr_cm3_min": _num(getattr(tool, "mrr_cm3_min", None)),
        "specific_energy_j_mm3": _num(getattr(tool, "specific_energy_j_mm3", None)),
        "physics_residual": _num(getattr(feat, "physics_residual", None)),
        "anomaly_score": _num(getattr(tool, "anomaly_score", None)),
        "tool_health_pct": _num(getattr(tool, "tool_health_pct", None)),
        "recommendation": getattr(fc, "recommendation", None),
        "contributions": contrib,
    }
