from __future__ import annotations

from dataclasses import dataclass

from src.pipeline import MonitorResult


@dataclass
class ParameterLimit:
    key: str
    label: str
    value: float
    setpoint: float
    stop_limit: float
    unit: str
    enabled: bool
    stop_if_exceeded: bool
    action: str  # reduce_feed | reduce_rpm | stop_only


@dataclass
class ControlDecision:
    mode: str
    action: str  # none | reduce_feed | reduce_rpm | stop
    reason: str
    breaches: list[str]
    hard_stops: list[str]
    feed_mm_tooth: float
    rpm: float
    applied: bool
    message: str
    eta_s: float | None = None
    alert: bool = False


def limits_from_result(
    result: MonitorResult,
    *,
    ra_set: float,
    ra_stop: float,
    ra_on: bool,
    ra_estop: bool,
    vb_set: float,
    vb_stop: float,
    vb_on: bool,
    vb_estop: bool,
    rate_set: float,
    rate_stop: float,
    rate_on: bool,
    rate_estop: bool,
    temp_set: float,
    temp_stop: float,
    temp_on: bool,
    temp_estop: bool,
    vib_set: float,
    vib_stop: float,
    vib_on: bool,
    vib_estop: bool,
    force_set: float,
    force_stop: float,
    force_on: bool,
    force_estop: bool,
    risk_set: float,
    risk_stop: float,
    risk_on: bool,
    risk_estop: bool,
) -> list[ParameterLimit]:
    tool = result.forecast.tool
    ra = result.frame.true_ra_um if result.frame.true_ra_um is not None else result.forecast.predicted_ra_um
    return [
        ParameterLimit("ra", "Roughness Ra", ra, ra_set, ra_stop, "μm", ra_on, ra_estop, "reduce_feed"),
        ParameterLimit("vb", "Flank wear VB", tool.vb_mm, vb_set, vb_stop, "mm", vb_on, vb_estop, "reduce_rpm"),
        ParameterLimit("rate", "Wear rate", tool.wear_rate_um_s, rate_set, rate_stop, "μm/s", rate_on, rate_estop, "reduce_rpm"),
        ParameterLimit("temp", "Temperature", tool.temperature_c, temp_set, temp_stop, "°C", temp_on, temp_estop, "reduce_rpm"),
        ParameterLimit("vib", "Vibration RMS", result.features.vib_rms, vib_set, vib_stop, "g", vib_on, vib_estop, "reduce_feed"),
        ParameterLimit("force", "Force RMS", result.features.force_rms, force_set, force_stop, "N", force_on, force_estop, "reduce_feed"),
        ParameterLimit("risk", "Degradation probability", 100.0 * result.forecast.probability, risk_set, risk_stop, "%", risk_on, risk_estop, "stop_only"),
    ]


def decide(
    limits: list[ParameterLimit],
    *,
    mode: str = "auto",
    feed: float,
    rpm: float,
    min_feed: float = 0.04,
    min_rpm: float = 1800.0,
    feed_step: float = 0.10,
    rpm_step: float = 0.06,
) -> ControlDecision:
    """Keep each armed parameter at or below its desired setpoint.

    One supervisor does everything: watch values, explain the action,
    reduce feed/rpm when above the desired max, and hard-stop when a
    stop level is crossed.
    """
    breaches = [lim.label for lim in limits if lim.enabled and lim.value > lim.setpoint]
    hard = [lim.label for lim in limits if lim.enabled and lim.value >= lim.stop_limit]

    new_feed, new_rpm = feed, rpm
    action = "none"
    reason = "All armed parameters are inside desired limits."

    if hard:
        action = "stop"
        reason = "Hard stop: " + ", ".join(hard) + " reached the stop level. Machine halted automatically."
    elif breaches:
        feed_hits = [lim for lim in limits if lim.enabled and lim.value > lim.setpoint and lim.action == "reduce_feed"]
        rpm_hits = [lim for lim in limits if lim.enabled and lim.value > lim.setpoint and lim.action == "reduce_rpm"]
        stop_hits = [lim for lim in limits if lim.enabled and lim.value > lim.setpoint and lim.action == "stop_only"]
        if stop_hits and not feed_hits and not rpm_hits:
            action = "stop"
            reason = "Risk limit exceeded: " + ", ".join(x.label for x in stop_hits)
        elif feed_hits:
            action = "reduce_feed"
            new_feed = max(min_feed, feed * (1.0 - feed_step))
            reason = (
                "Above desired: "
                + ", ".join(x.label for x in feed_hits)
                + f". Reduce feed {feed_step:.0%} to keep the cut below the setpoint."
            )
        elif rpm_hits:
            action = "reduce_rpm"
            new_rpm = max(min_rpm, rpm * (1.0 - rpm_step))
            reason = (
                "Above desired: "
                + ", ".join(x.label for x in rpm_hits)
                + f". Reduce spindle {rpm_step:.0%} (Taylor/thermal response)."
            )

    applied = action != "none"
    if action == "stop":
        message = "HARD STOP: " + reason
    elif action == "none":
        message = "Monitoring. " + reason
    else:
        message = "Applied: " + reason

    return ControlDecision(
        mode="auto",
        action=action,
        reason=reason,
        breaches=breaches,
        hard_stops=hard,
        feed_mm_tooth=new_feed,
        rpm=new_rpm,
        applied=applied,
        message=message,
    )


def eta_seconds(times: list[float], values: list[float], limit: float) -> float | None:
    """Seconds until `values` would hit `limit` at the recent slope. None if not approaching."""
    if len(times) < 4 or len(values) < 4:
        return None
    t = [float(x) for x in times[-10:]]
    v = [float(x) for x in values[-10:]]
    dt = t[-1] - t[0]
    if dt < 0.4:
        return None
    slope = (v[-1] - v[0]) / dt
    if slope <= 1e-5:
        return None
    remaining = (limit - v[-1]) / slope
    if remaining < 0:
        return 0.0
    if remaining > 600:
        return None
    return float(remaining)
