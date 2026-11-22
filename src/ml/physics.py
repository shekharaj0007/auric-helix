from __future__ import annotations


def physics_power_consistency(force_n: float, cutting_speed_m_min: float, measured_power_w: float) -> float:
    """Soft constraint residual for P ≈ Fc · Vc.

    Idle power is treated as a constant offset. A large residual means the
    sensors disagree with cutting mechanics — useful both as an ML feature
    and as a dashboard diagnostic.
    """
    vc_m_s = cutting_speed_m_min / 60.0
    predicted = 180.0 + abs(force_n) * vc_m_s
    return abs(measured_power_w - predicted) / max(measured_power_w, 1.0)
