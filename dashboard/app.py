from __future__ import annotations

import os
import sys
import socket
import time
import urllib.request
from collections import deque
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import infer, load_config, make_source
from src.ml.model import MONITOR
from src.control.supervisor import decide, eta_seconds, limits_from_result
from src.control.stop_log import record_from_result, write_stop_record
from src.control.stop_report import save_stop_pdf
from src.acquisition.cycle_signal import read_cycle_signal
from src.acquisition.bridge_client import bridge_event, bridge_status
from src.acquisition.gcode_playback import compile_program, extract_gcode

st.set_page_config(
    page_title="Machining Integrity Monitor",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

PLOT_BG = "#101216"
PAPER = "#101216"
GRID = "#2A2F38"
FONT = "#D6DCE6"
FORGE_URL = "https://temporary-speedy-azure-d4iojfc.vercel.app"


def _on_cloud() -> bool:
    return bool(
        os.environ.get("AURICHELIX_CLOUD")
        or os.environ.get("SPACE_ID")
        or os.environ.get("SPACE_HF_DOMAIN")
        or Path("/mount/src").exists()
        or Path("/home/appuser").exists()
    )


def _lan_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        return "127.0.0.1"

CUSTOM_CSS = """
<style>
    .stApp { background: #0B0D10; }
    [data-testid="stHeader"] { background: #0B0D10; }
    [data-testid="stSidebar"] { background: #12151A; }
    .block-container { padding-top: 1.1rem; padding-bottom: 2rem; }
    h1, h2, h3 { font-weight: 600; letter-spacing: 0.01em; }
    div[data-testid="stMetric"] {
        background: #161A20;
        border: 1px solid #2A3038;
        padding: 12px 14px;
        border-radius: 8px;
    }
    .status-ok { color: #3D9A6A; font-weight: 700; font-size: 1.35rem; }
    .status-warn { color: #C48A1A; font-weight: 700; font-size: 1.35rem; }
    .status-stop { color: #C43A3A; font-weight: 700; font-size: 1.35rem; }
    .status-bad { color: #C43A3A; font-weight: 700; font-size: 1.35rem; }
    .alert-red {
        background: #3A1212;
        border: 1px solid #C43A3A;
        color: #F2CACA;
        border-radius: 8px;
        padding: 14px 16px;
        margin: 8px 0 14px 0;
        font-weight: 650;
        font-size: 1.05rem;
    }
    .alert-timer {
        font-size: 1.55rem;
        color: #FF6B6B;
        font-weight: 800;
        letter-spacing: 0.02em;
    }
    .muted { color: #8B93A1; font-size: 0.86rem; }
    .panel {
        background: #161A20;
        border: 1px solid #2A3038;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 8px;
    }
    .pdf-box {
        background: #1A1810;
        border: 1px solid #C9A227;
        color: #F3E6B8;
        border-radius: 8px;
        padding: 14px 16px;
        margin: 8px 0 14px 0;
    }
</style>
"""


def _fig_layout(fig: go.Figure, ylabel: str) -> go.Figure:
    fig.update_layout(
        margin=dict(l=40, r=12, t=28, b=36),
        paper_bgcolor=PAPER,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT, size=12),
        height=220,
        showlegend=False,
        xaxis=dict(gridcolor=GRID, zeroline=False, title="time (s)"),
        yaxis=dict(gridcolor=GRID, zeroline=False, title=ylabel),
    )
    return fig


def waveform_fig(y: np.ndarray, fs: float, title: str, color: str, ylabel: str) -> go.Figure:
    t = np.arange(len(y)) / max(fs, 1.0)
    fig = go.Figure(go.Scatter(x=t, y=y, mode="lines", line=dict(color=color, width=1.4)))
    fig.update_layout(title=dict(text=title, font=dict(size=13)))
    return _fig_layout(fig, ylabel)


def history_fig(times: list[float], values: list[float], title: str, color: str, ylabel: str, hline=None) -> go.Figure:
    fig = go.Figure(go.Scatter(x=times, y=values, mode="lines", line=dict(color=color, width=2)))
    if hline is not None:
        fig.add_hline(y=hline, line_dash="dot", line_color="#C43A3A", annotation_text="spec")
    fig.update_layout(title=dict(text=title, font=dict(size=13)))
    return _fig_layout(fig, ylabel)


def contrib_fig(contrib: dict[str, float]) -> go.Figure:
    names = list(contrib.keys())
    vals = [contrib[n] for n in names]
    fig = go.Figure(
        go.Bar(
            x=vals,
            y=names,
            orientation="h",
            marker_color=["#6EA8FF", "#C48A1A", "#7A8CA8", "#3D9A6A", "#A78BFA", "#D15A2A", "#8B93A1"][: len(names)],
        )
    )
    fig.update_layout(
        margin=dict(l=10, r=12, t=28, b=24),
        paper_bgcolor=PAPER,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT, size=12),
        height=280,
        title=dict(text="Why the model fired (% contribution)", font=dict(size=13)),
        xaxis=dict(gridcolor=GRID, title="contribution (%)"),
        yaxis=dict(autorange="reversed"),
    )
    return fig


def machine_status(
    probability: float,
    degraded: bool,
    regime_id: int,
    stopped: bool = False,
    approaching: bool = False,
) -> tuple[str, str]:
    if stopped:
        return "STOPPED", "status-stop"
    if approaching:
        return "RED ALERT", "status-stop"
    if degraded or regime_id == 3 or probability >= 0.80:
        return "SURFACE RISK", "status-bad"
    if regime_id >= 1 or probability >= 0.35:
        return "WATCH", "status-warn"
    return "STABLE", "status-ok"


def _begin_run(cfg: dict, *, force_simulator: bool = False) -> None:
    source_name = "simulator"
    try:
        if force_simulator:
            cfg = {**cfg, "acquisition": {**cfg["acquisition"], "source": "simulator"}}
        source_name = cfg["acquisition"].get("source", "simulator")
        if st.session_state.source is not None:
            try:
                st.session_state.source.close()
            except Exception:
                pass
            st.session_state.source = None
        st.session_state.source = make_source(cfg)
        st.session_state.source.open()
        for key in st.session_state.history:
            st.session_state.history[key].clear()
        st.session_state.latest = None
        st.session_state.error = None
        st.session_state.control = None
        st.session_state.last_override_t = -999.0
        st.session_state.stopped = False
        st.session_state.ra_eta_s = None
        st.session_state.ra_alert = False
        st.session_state.alerts = []
        st.session_state.soonest_eta_s = None
        st.session_state.stop_reason = ""
        st.session_state.override_count = 0
        st.session_state.cycle_started = False
        st.session_state.running = True
    except Exception as exc:  # noqa: BLE001
        st.session_state.running = False
        st.session_state.source = None
        st.session_state.error = f"Could not start ({source_name}): {exc}"


def _refresh_button(key: str) -> None:
    if st.button("Refresh", width="stretch", key=key):
        st.rerun()


def _apply_manual_readings(
    result,
    *,
    use_manual: bool,
    ra: float | None,
    vb: float | None,
    rate: float | None,
    temp: float | None,
    vib: float | None,
    force: float | None,
    ra_spec_um: float,
):
    if not use_manual:
        return result
    frame = result.frame
    tool = result.forecast.tool
    feat = result.features
    if ra is not None:
        frame.true_ra_um = ra
    if vb is not None:
        frame.true_vb_mm = vb
        tool.vb_mm = vb
        tool.tool_health_pct = float(max(0.0, min(100.0, 100.0 * (1.0 - vb / 0.30))))
        if vb < 0.15:
            tool.stage = "early"
        elif vb < 0.25:
            tool.stage = "mid-life"
        else:
            tool.stage = "worn"
    if rate is not None:
        frame.true_wear_rate_um_s = rate
        tool.wear_rate_um_s = rate
        tool.wear_rate_um_min = rate * 60.0
    if temp is not None:
        frame.temperature_c = temp
        tool.temperature_c = temp
        feat.temperature_c = temp
    if vib is not None:
        feat.vib_rms = vib
    if force is not None:
        feat.force_rms = force
    ra_now = frame.true_ra_um if frame.true_ra_um is not None else result.forecast.predicted_ra_um
    result.degraded = ra_now >= ra_spec_um or tool.vb_mm >= 0.30
    return result


def _fmt_axis(value) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.3f} mm"
    except (TypeError, ValueError):
        return "—"


def _looks_origin(xyz: dict) -> bool:
    try:
        x = float(xyz.get("x"))
        y = float(xyz.get("y"))
        z = float(xyz.get("z") or 0)
    except (TypeError, ValueError):
        return False
    return abs(x) < 0.05 and abs(y) < 0.05 and z >= 0


def _update_mill_xyz() -> dict:
    pose = bridge_status()
    xyz = {"x": pose.get("x"), "y": pose.get("y"), "z": pose.get("z"), "frozen": bool(pose.get("frozen"))}
    status = str(pose.get("status") or "").upper()
    if xyz["x"] is not None or xyz["y"] is not None or xyz["z"] is not None:
        if not (st.session_state.get("stopped") and _looks_origin(xyz) and st.session_state.get("stop_xyz")):
            st.session_state.mill_xyz = xyz
        held = xyz.get("frozen") or status in {"HOLD", "FEED HOLD"}
        if held and not _looks_origin(xyz):
            st.session_state.stop_xyz = dict(xyz)
    return xyz


def _show_mill_xyz() -> None:
    live = _update_mill_xyz()
    held = st.session_state.get("stop_xyz") if st.session_state.get("stopped") else None
    src = held or live or st.session_state.get("mill_xyz") or {}
    c1, c2, c3 = st.columns(3)
    c1.metric("CNC X", _fmt_axis(src.get("x")), "from ForgeMill DRO")
    c2.metric("CNC Y", _fmt_axis(src.get("y")), "from ForgeMill DRO")
    c3.metric("CNC Z", _fmt_axis(src.get("z")), "from ForgeMill DRO")
    if st.session_state.get("stopped"):
        rec = st.session_state.get("stop_record") or {}
        st.caption(
            "Tool held at this coordinate (not sent home). "
            f"Logged to data/stop_log.jsonl · {rec.get('reason', '')}"
        )
    else:
        st.caption("Live tool position from the CNC DRO. On Hold/hard-stop this pose is frozen and logged.")


def _show_texture(result) -> None:
    tex = getattr(result.forecast, "texture", None)
    if tex is None:
        return
    st.markdown("**Predicted surface texture (more than Ra)**")
    a, b, c, d, e, f = st.columns(6)
    a.metric("Ra (mean)", f"{tex.ra_um:.2f} μm", "integrity proxy")
    b.metric("Rq (RMS)", f"{tex.rq_um:.2f} μm", "ISO RMS roughness")
    c.metric("Rz (peaks)", f"{tex.rz_um:.2f} μm", "ten-point height")
    d.metric("Rt (total)", f"{tex.rt_um:.2f} μm", "max peak-to-valley")
    e.metric("Chatter freq.", f"{tex.chatter_hz:.0f} Hz", "dominant unstable line")
    f.metric("Form / waviness", f"{tex.form_error_um:.2f} μm", "chatter-driven extra")


def _limits_rows_for_pdf(limits) -> list[list[str]]:
    rows: list[list[str]] = []
    for lim in limits or []:
        if not getattr(lim, "enabled", True):
            continue
        value = float(lim.value)
        stop = float(lim.stop_limit)
        if value >= stop:
            state = "TRIPPED"
        elif stop > 0 and value >= 0.85 * stop:
            state = "NEAR"
        else:
            state = "OK"
        rows.append(
            [
                f"{lim.label} ({lim.unit})",
                f"{value:.3g}",
                f"{float(lim.setpoint):.3g}",
                f"{stop:.3g}",
                state,
            ]
        )
    return rows


def _write_stop_pdf(record: dict | None) -> None:
    rec = dict(record or {})
    if not rec.get("reason"):
        rec["reason"] = st.session_state.get("stop_reason") or "programme stopped"
    extra = {
        "limits": rec.get("limits") or [],
        "contributions": rec.get("contributions") or {},
        "recommendation": rec.get("recommendation"),
    }
    try:
        path, pdf = save_stop_pdf(rec, extra)
        st.session_state.stop_pdf_bytes = pdf
        st.session_state.stop_pdf_name = path.name
        st.session_state.stop_pdf_path = str(path)
    except Exception:
        st.session_state.stop_pdf_bytes = None
        st.session_state.stop_pdf_name = None
        st.session_state.stop_pdf_path = None


def _show_stop_record() -> None:
    rec = st.session_state.get("stop_record")
    if not rec:
        return
    if not st.session_state.get("stop_pdf_bytes"):
        _write_stop_pdf(rec)
    pdf_bytes = st.session_state.get("stop_pdf_bytes")
    pdf_name = st.session_state.get("stop_pdf_name") or "stop_report.pdf"
    st.markdown(
        "<div class='pdf-box'><b>Stop-incident PDF is ready</b><br>"
        "Download it for the problems that stopped the programme, the measured parameters at that instant, "
        "and the measures that can be taken. A copy is also saved under data/stop_reports/.</div>",
        unsafe_allow_html=True,
    )
    if pdf_bytes:
        st.download_button(
            "Download stop-incident PDF",
            data=pdf_bytes,
            file_name=pdf_name,
            mime="application/pdf",
            width="stretch",
            key="dl_stop_pdf",
        )
        path = st.session_state.get("stop_pdf_path")
        if path:
            st.caption(f"Also written to `{path}`")
    else:
        st.warning("The stop PDF could not be built. The table below is still the logged snapshot.")
    st.markdown("**Stop coordinate record**")
    st.table(
        {
            "Quantity": [
                "X", "Y", "Z", "Cut time", "Spindle", "Feed", "Regime",
                "Ra", "Rq", "Rz", "Rt", "VB", "Wear rate", "Temperature", "Risk",
            ],
            "Value": [
                _fmt_axis(rec.get("x_mm")),
                _fmt_axis(rec.get("y_mm")),
                _fmt_axis(rec.get("z_mm")),
                f"{rec.get('time_s') or 0:.1f} s",
                f"{rec.get('rpm') or 0:.0f} r/min",
                f"{rec.get('feed_mm_tooth') or 0:.3f} mm/tooth",
                rec.get("regime") or "—",
                f"{rec.get('ra_um') or 0:.2f} μm",
                f"{rec.get('rq_um') or 0:.2f} μm",
                f"{rec.get('rz_um') or 0:.2f} μm",
                f"{rec.get('rt_um') or 0:.2f} μm",
                f"{rec.get('vb_mm') or 0:.3f} mm",
                f"{rec.get('wear_rate_um_s') or 0:.2f} μm/s",
                f"{rec.get('temperature_c') or 0:.1f} °C",
                f"{100.0 * (rec.get('risk') or 0):.0f} %",
            ],
        }
    )


def _fmt_eta(eta_s: float | None) -> str:
    if eta_s is None:
        return "—"
    if eta_s <= 0:
        return "now"
    if eta_s < 10:
        return f"{eta_s:.1f} s"
    return f"{eta_s:.0f} s"


def halt_run(reason: str, *, freeze_mill: bool = True) -> None:
    live = st.session_state.get("mill_xyz") or {}
    pose = bridge_status()
    xyz = {
        "x": pose.get("x") if pose.get("x") is not None else live.get("x"),
        "y": pose.get("y") if pose.get("y") is not None else live.get("y"),
        "z": pose.get("z") if pose.get("z") is not None else live.get("z"),
    }
    st.session_state.mill_xyz = xyz
    if xyz.get("x") is not None or xyz.get("y") is not None or xyz.get("z") is not None:
        if not _looks_origin(xyz) or not st.session_state.get("stop_xyz"):
            st.session_state.stop_xyz = dict(xyz)
    latest = st.session_state.get("latest")
    rec = {"reason": reason, "x_mm": xyz.get("x"), "y_mm": xyz.get("y"), "z_mm": xyz.get("z")}
    if latest is not None:
        try:
            rec = record_from_result(latest, xyz, reason)
        except Exception:
            rec = {"reason": reason, "x_mm": xyz.get("x"), "y_mm": xyz.get("y"), "z_mm": xyz.get("z")}
    control = st.session_state.get("control") or {}
    limits = control.get("limits") if isinstance(control, dict) else None
    if limits:
        rec["limits"] = _limits_rows_for_pdf(limits)
    try:
        rec = write_stop_record(rec)
    except Exception:
        pass
    st.session_state.stop_record = rec
    _write_stop_pdf(rec)
    if st.session_state.source is not None:
        try:
            st.session_state.source.request_stop(reason)
        except Exception:
            pass
        try:
            st.session_state.source.close()
        except Exception:
            pass
        st.session_state.source = None
    if freeze_mill:
        try:
            bridge_event("want_hold")
        except Exception:
            pass
    st.session_state.running = False
    st.session_state.stopped = True
    st.session_state.stop_reason = reason


def _mill_cycle_seconds() -> float:
    for url in (f"http://127.0.0.1:8766/", FORGE_URL):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "BTP-monitor/1.0"})
            html = urllib.request.urlopen(req, timeout=6).read().decode("utf-8", "replace")
            program = extract_gcode(html)
            if program:
                return max(sum(seg.duration_s for seg in compile_program(program)), 8.0)
        except Exception:
            continue
    return 35.0


def _follow_cycle_start(cfg: dict, source_choice: str) -> None:
    """Start/stop the local simulator with Cycle start / program end on the CNC laptop."""
    if source_choice == "serial":
        return
    sig = read_cycle_signal(str(cfg["acquisition"].get("http_url") or FORGE_URL))
    now = bool(sig.get("ok") and sig.get("running"))
    prev = bool(st.session_state.get("cycle_sig_running"))
    if now and not prev and not st.session_state.running:
        _begin_run(cfg, force_simulator=True)
        st.session_state.cycle_started = True
        st.session_state.stopped = False
        st.session_state.cycle_t0 = time.time()
        st.session_state.cycle_limit_s = _mill_cycle_seconds()
        st.session_state.stop_xyz = None
    elif st.session_state.get("cycle_started") and st.session_state.running:
        timed_out = False
        t0 = st.session_state.get("cycle_t0")
        limit = st.session_state.get("cycle_limit_s")
        if t0 and limit:
            timed_out = (time.time() - t0) >= (float(limit) + 1.2)
        if (not now) or timed_out:
            halt_run("Machining complete on CNC", freeze_mill=False)
            st.session_state.cycle_started = False
    st.session_state.cycle_sig_running = now


def init_state() -> None:
    defaults = {
        "running": False,
        "source": None,
        "history": {
            "t": deque(maxlen=180),
            "p": deque(maxlen=180),
            "ra": deque(maxlen=180),
            "vib": deque(maxlen=180),
            "force": deque(maxlen=180),
            "power": deque(maxlen=180),
            "temp": deque(maxlen=180),
            "vb": deque(maxlen=180),
            "rate": deque(maxlen=180),
            "health": deque(maxlen=180),
            "feed": deque(maxlen=180),
            "rpm": deque(maxlen=180),
        },
        "latest": None,
        "error": None,
        "control": None,
        "last_override_t": -999.0,
        "stopped": False,
        "ra_eta_s": None,
        "ra_alert": False,
        "alerts": [],
        "soonest_eta_s": None,
        "stop_reason": "",
        "override_count": 0,
        "cycle_started": False,
        "cycle_sig_running": False,
        "mill_xyz": {"x": None, "y": None, "z": None},
        "stop_xyz": None,
        "stop_record": None,
        "stop_pdf_bytes": None,
        "stop_pdf_name": None,
        "stop_pdf_path": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    init_state()
    cfg = load_config(str(ROOT / "config.yaml"))
    if not MONITOR.is_ready():
        with st.spinner("Training GMM + wear/temperature models on simulated milling runs..."):
            MONITOR.ensure_trained(
                ra_spec_um=float(cfg["process"]["ra_spec_um"]),
                horizon_s=float(cfg["dashboard"]["horizon_seconds"]),
            )

    st.sidebar.markdown("### Page")
    _refresh_button("refresh_sidebar")
    st.sidebar.caption("Reloads this monitor immediately.")

    st.sidebar.markdown("### Machine link")
    source_options = ["simulator", "serial", "http"]
    default_source = cfg["acquisition"].get("source", "simulator")
    if _on_cloud():
        default_source = "simulator"
    source_choice = st.sidebar.selectbox(
        "Data source",
        source_options,
        index=source_options.index(default_source) if default_source in source_options else 0,
        key="data_source_restore",
        help="http = other laptop's ForgeMill (Vercel URL). simulator = built-in twin. serial = Arduino.",
    )
    if _on_cloud() and source_choice == "http":
        st.sidebar.caption("Cloud host has no local mill bridge — using the physics twin unless you keep simulator.")
    com_port = st.sidebar.text_input("Serial port", cfg["acquisition"].get("serial_port", "COM3"))
    baud = st.sidebar.number_input("Baud rate", value=int(cfg["acquisition"].get("serial_baud", 115200)), step=100)
    http_url = st.sidebar.text_input(
        "Online CNC URL",
        cfg["acquisition"].get("http_url", FORGE_URL),
        key="cnc_url_restore",
        help="ForgeMill on the other laptop. This dashboard does not display that mill.",
    )

    st.sidebar.markdown("### Manual settings")
    st.sidebar.caption("Type the process values and the limits you want. All of these are used — there is no extra “use this limit” switch.")
    cfg["process"]["material"] = st.sidebar.text_input("Material", str(cfg["process"].get("material", "Al6061")))
    cfg["process"]["tool_diameter_mm"] = st.sidebar.number_input(
        "Tool diameter (mm)", value=float(cfg["process"].get("tool_diameter_mm", 10)), format="%.2f"
    )
    cfg["process"]["teeth"] = int(
        st.sidebar.number_input("Flutes / teeth", value=int(cfg["process"].get("teeth", 4)), min_value=1, step=1)
    )
    cfg["process"]["depth_of_cut_mm"] = st.sidebar.number_input(
        "Depth of cut (mm)", value=float(cfg["process"].get("depth_of_cut_mm", 1.0)), format="%.2f"
    )
    cfg["process"]["spindle_rpm"] = st.sidebar.number_input(
        "Spindle speed (rpm)", value=float(cfg["process"]["spindle_rpm"])
    )
    cfg["process"]["feed_mm_per_tooth"] = st.sidebar.number_input(
        "Feed (mm/tooth)", value=float(cfg["process"]["feed_mm_per_tooth"]), format="%.3f"
    )
    horizon = st.sidebar.slider("Warning horizon (s)", 10, 60, int(cfg["dashboard"]["horizon_seconds"]))

    st.sidebar.markdown("#### Limits you type")
    st.sidebar.caption(
        "Desired max = keep the cut below this. Hard stop = machine stops at this value. "
        "Degradation probability is shown on the dashboard only — it does not stop the run."
    )

    def _manual_limit(label: str, key: str, desired: float, hard: float, fmt: str) -> tuple[float, float]:
        st.sidebar.markdown(f"**{label}**")
        c1, c2 = st.sidebar.columns(2)
        with c1:
            setpoint = st.number_input("Desired max", value=desired, format=fmt, key=f"{key}_set")
        with c2:
            stop_lim = st.number_input("Hard stop", value=hard, format=fmt, key=f"{key}_hard")
        return float(setpoint), float(stop_lim)

    ra_spec_default = float(cfg["process"]["ra_spec_um"])
    ra_set, ra_hard = _manual_limit("Roughness Ra (μm)", "ra", ra_spec_default, ra_spec_default, "%.2f")
    vb_set, vb_hard = _manual_limit("Flank wear VB (mm)", "vb", 0.25, 0.30, "%.3f")
    rate_set, rate_hard = _manual_limit("Wear rate (μm/s)", "rate", 14.0, 22.0, "%.1f")
    temp_set, temp_hard = _manual_limit("Temperature (°C)", "temp", 48.0, 58.0, "%.1f")
    vib_set, vib_hard = _manual_limit("Vibration RMS (g)", "vib", 0.9, 1.6, "%.2f")
    force_set, force_hard = _manual_limit("Force RMS (N)", "force", 320.0, 420.0, "%.0f")
    ra_on = vb_on = rate_on = temp_on = vib_on = force_on = True
    ra_estop = vb_estop = rate_estop = temp_estop = vib_estop = force_estop = True
    risk_on = False
    risk_estop = False
    risk_set, risk_hard = 70.0, 90.0
    ra_spec = ra_set

    st.sidebar.markdown("#### My measured values")
    st.sidebar.caption("Turn this on to type lab / manual readings. Those numbers replace the live simulator for stop and display.")
    use_manual_readings = st.sidebar.checkbox("Use my measured values", value=False, key="use_manual_readings")
    ra_manual = vb_manual = rate_manual = temp_manual = vib_manual = force_manual = None
    if use_manual_readings:
        ra_manual = float(st.sidebar.number_input("Measured Ra (μm)", value=1.20, format="%.2f", key="manual_ra"))
        vb_manual = float(st.sidebar.number_input("Measured VB (mm)", value=0.12, format="%.3f", key="manual_vb"))
        rate_manual = float(st.sidebar.number_input("Measured wear rate (μm/s)", value=8.0, format="%.2f", key="manual_rate"))
        temp_manual = float(st.sidebar.number_input("Measured temperature (°C)", value=36.0, format="%.1f", key="manual_temp"))
        vib_manual = float(st.sidebar.number_input("Measured vibration RMS (g)", value=0.40, format="%.2f", key="manual_vib"))
        force_manual = float(st.sidebar.number_input("Measured force RMS (N)", value=220.0, format="%.0f", key="manual_force"))

    cfg["acquisition"]["source"] = source_choice
    cfg["acquisition"]["serial_port"] = com_port
    cfg["acquisition"]["serial_baud"] = int(baud)
    cfg["acquisition"]["http_url"] = http_url
    cfg["process"]["ra_spec_um"] = ra_spec

    cols = st.sidebar.columns(2)
    if cols[0].button("Start run", type="primary", width="stretch"):
        _begin_run(cfg)
    if cols[1].button("Stop", width="stretch"):
        halt_run("operator stop")

    shown_source = (
        "simulator (Cycle start)"
        if st.session_state.get("cycle_started") or (
            st.session_state.running
            and st.session_state.source is not None
            and getattr(st.session_state.source, "name", "") == "simulator"
        )
        else source_choice
    )
    st.markdown(
        f"<div class='muted'>CNC milling integrity monitor · {cfg['process']['material']} · "
        f"{cfg['process']['operation'].replace('_', ' ')} · source: <b>{shown_source}</b></div>",
        unsafe_allow_html=True,
    )
    title_l, title_r = st.columns([2.6, 1.4])
    with title_l:
        st.title("Early surface-integrity warning")
    with title_r:
        st.write("")
        _refresh_button("refresh_main")
        if not st.session_state.running:
            if st.button("▶ Start run", width="stretch", key="main_start"):
                _begin_run(cfg)
            if st.button("Start simulator", width="stretch", key="main_sim_start"):
                _begin_run(cfg, force_simulator=True)
        else:
            if st.button("■ Stop", width="stretch", key="main_stop"):
                halt_run("operator stop")

    if source_choice != "serial" and not _on_cloud():
        st.caption(
            "Press **Cycle start** on the CNC laptop. This page auto-starts the milling simulator "
            "and shows Ra, wear, temperature, vibration and hard-stop status live. "
            "It stops when you press Hold/Stop or the cycle ends. Do not press Start run."
        )
    elif _on_cloud():
        st.caption(
            "Cloud demo: press **Start simulator**. Ra, wear, temperature, vibration and hard-stop "
            "run on the physics twin. Software Hold is not a certified e-stop. Simulated labels are not laboratory results."
        )

    if st.session_state.error:
        st.error(st.session_state.error)

    if not _on_cloud():
        _follow_cycle_start(cfg, source_choice)

    if st.session_state.running and st.session_state.source is not None:
        try:
            frame = st.session_state.source.read_frame()
            result = infer(frame, ra_spec_um=ra_spec, horizon_s=float(horizon))
            result = _apply_manual_readings(
                result,
                use_manual=use_manual_readings,
                ra=ra_manual,
                vb=vb_manual,
                rate=rate_manual,
                temp=temp_manual,
                vib=vib_manual,
                force=force_manual,
                ra_spec_um=ra_spec,
            )
            st.session_state.latest = result
            hist = st.session_state.history
            hist["t"].append(result.frame.time_s)
            hist["p"].append(result.forecast.probability)
            hist["ra"].append(
                result.frame.true_ra_um
                if result.frame.true_ra_um is not None
                else result.forecast.predicted_ra_um
            )
            hist["vib"].append(result.features.vib_rms)
            hist["force"].append(result.features.force_rms)
            hist["power"].append(result.features.spindle_power_w)
            hist["temp"].append(result.forecast.tool.temperature_c)
            hist["vb"].append(result.forecast.tool.vb_mm)
            hist["rate"].append(result.forecast.tool.wear_rate_um_s)
            hist["health"].append(result.forecast.tool.tool_health_pct)
            hist["feed"].append(result.frame.feed_mm_tooth)
            hist["rpm"].append(result.frame.rpm)

            limits = limits_from_result(
                result,
                ra_set=ra_set, ra_stop=ra_hard, ra_on=ra_on, ra_estop=ra_estop,
                vb_set=vb_set, vb_stop=vb_hard, vb_on=vb_on, vb_estop=vb_estop,
                rate_set=rate_set, rate_stop=rate_hard, rate_on=rate_on, rate_estop=rate_estop,
                temp_set=temp_set, temp_stop=temp_hard, temp_on=temp_on, temp_estop=temp_estop,
                vib_set=vib_set, vib_stop=vib_hard, vib_on=vib_on, vib_estop=vib_estop,
                force_set=force_set, force_stop=force_hard, force_on=force_on, force_estop=force_estop,
                risk_set=risk_set, risk_stop=risk_hard, risk_on=risk_on, risk_estop=risk_estop,
            )
            decision = decide(
                limits,
                feed=result.frame.feed_mm_tooth,
                rpm=result.frame.rpm,
                min_feed=0.09,
            )
            cooldown_ok = result.frame.time_s - st.session_state.last_override_t >= 2.0
            ra_now = (
                result.frame.true_ra_um
                if result.frame.true_ra_um is not None
                else result.forecast.predicted_ra_um
            )
            hist_keys = {
                "ra": "ra", "vb": "vb", "rate": "rate", "temp": "temp",
                "vib": "vib", "force": "force", "risk": "p",
            }
            t_hist = list(hist["t"])
            alerts: list[dict] = []
            soonest_eta: float | None = None
            ra_eta: float | None = None
            for lim in limits:
                if not lim.enabled:
                    continue
                series = list(hist[hist_keys[lim.key]])
                if lim.key == "risk":
                    series = [100.0 * v for v in series]
                eta = eta_seconds(t_hist, series, lim.stop_limit)
                if lim.key == "ra":
                    ra_eta = eta
                frac = (lim.value / lim.stop_limit) if lim.stop_limit > 0 else 0.0
                approaching = frac >= 0.85 or (eta is not None and eta <= 8.0)
                if approaching and lim.value < lim.stop_limit:
                    alerts.append(
                        {"label": lim.label, "eta_s": eta, "value": lim.value, "stop": lim.stop_limit, "frac": frac}
                    )
                    if eta is not None and (soonest_eta is None or eta < soonest_eta):
                        soonest_eta = eta
            st.session_state.alerts = alerts
            st.session_state.soonest_eta_s = soonest_eta
            st.session_state.ra_eta_s = ra_eta

            crossed = [
                lim for lim in limits
                if lim.enabled and lim.key != "risk" and lim.value >= lim.stop_limit
            ]
            if ra_on and ra_now >= ra_hard and not any(lim.key == "ra" for lim in crossed):
                crossed.extend(lim for lim in limits if lim.key == "ra")
            if crossed or decision.action == "stop":
                hits = crossed or [lim for lim in limits if lim.label in decision.hard_stops]
                why = "Automatic hard stop: " + "; ".join(
                    f"{lim.label} {lim.value:.3g} {lim.unit} reached hard-stop {lim.stop_limit:.3g} {lim.unit}"
                    for lim in hits
                ) if hits else (decision.reason or "Automatic hard stop")
                halt_run(why)
                decision.applied = True
                decision.action = "stop"
                decision.message = why + ". Machine halted automatically."
                st.session_state.control = {"decision": decision, "limits": limits}
            elif decision.action in {"reduce_feed", "reduce_rpm"} and cooldown_ok:
                if st.session_state.get("override_count", 0) < 2:
                    if decision.action == "reduce_feed":
                        st.session_state.source.apply_overrides(feed_mm_tooth=decision.feed_mm_tooth)
                    else:
                        st.session_state.source.apply_overrides(rpm=decision.rpm)
                    st.session_state.last_override_t = result.frame.time_s
                    st.session_state.override_count = st.session_state.get("override_count", 0) + 1
                st.session_state.control = {"decision": decision, "limits": limits}
            else:
                st.session_state.control = {"decision": decision, "limits": limits}
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            if msg.startswith("Cycle stop"):
                halt_run(msg)
            else:
                st.session_state.running = False
                st.session_state.error = f"Data link failed: {exc}"

    result = st.session_state.latest
    if result is None:
        if st.session_state.get("stopped"):
            st.markdown(
                "<div class='alert-red'><b>STOPPED</b><br>"
                f"{st.session_state.get('stop_reason') or 'Programme stopped.'}<br>"
                "Download the stop-incident PDF below.</div>",
                unsafe_allow_html=True,
            )
            _show_mill_xyz()
            _show_stop_record()
            return
        if source_choice == "http":
            mill = f"http://{_lan_ip()}:8766/"
            st.info(
                f"Waiting for **Cycle start**. On the CNC laptop open **{mill}**. "
                "Leave this page open. When you press Cycle start, the simulator starts here "
                "and you will see live readings, plots and hard-stop results until the cycle ends."
            )
            _show_mill_xyz()
            time.sleep(max(cfg["dashboard"]["refresh_ms"] / 1000.0, 0.35))
            st.rerun()
        st.info(
            "Click **▶ Start run**, or **Start simulator** for a local twin with no CNC."
        )
        with st.expander("How this dashboard connects to the machine", expanded=True):
            st.markdown(_ARCHITECTURE_MD)
        return

    fc = result.forecast
    alerts = st.session_state.get("alerts") or []
    soonest_eta = st.session_state.get("soonest_eta_s")
    ra_eta = st.session_state.get("ra_eta_s")
    approaching = bool(alerts) and not st.session_state.get("stopped", False)
    status, status_cls = machine_status(
        fc.probability,
        result.degraded,
        result.regime.regime_id,
        st.session_state.get("stopped", False),
        approaching=approaching,
    )
    tool = fc.tool
    ra_true = result.frame.true_ra_um
    vb_true = result.frame.true_vb_mm

    if alerts or st.session_state.get("stopped"):
        lines = []
        for a in alerts:
            lines.append(
                f"{a['label']} is at {a['value']:.3g} "
                f"({a['frac']:.0%} of hard stop {a['stop']:.3g}) · hard stop in {_fmt_eta(a['eta_s'])}"
            )
        stop_reason = st.session_state.get("stop_reason") or ""
        if st.session_state.get("stopped"):
            lines = [stop_reason] if stop_reason else ["Monitor halted."]
            held = st.session_state.get("stop_xyz") or st.session_state.get("mill_xyz") or {}
            lines.append(
                "CNC held at "
                f"X {_fmt_axis(held.get('x'))} · "
                f"Y {_fmt_axis(held.get('y'))} · "
                f"Z {_fmt_axis(held.get('z'))}"
            )
            lines.append("Download the stop-incident PDF below — why it stopped, values at stop, and measures to take.")
        timer = _fmt_eta(soonest_eta if soonest_eta is not None else ra_eta)
        headline = (
            "STOPPED"
            if st.session_state.get("stopped")
            else f"RED ALERT — hard stop in <span class='alert-timer'>{timer}</span>"
        )
        st.markdown(
            f"<div class='alert-red'><b>{headline}</b><br>" + "<br>".join(lines) + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("**CNC tool position**")
    _show_mill_xyz()
    if st.session_state.get("stopped"):
        _show_stop_record()
    _show_texture(result)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.markdown(f"<div class='{status_cls}'>{status}</div><div class='muted'>machine status</div>", unsafe_allow_html=True)
    k2.metric("Current regime", result.regime.name.split("—")[0].strip(), f"{result.regime.confidence:.0%} confidence")
    k3.metric(f"P(degradation in {horizon:.0f} s)", f"{fc.probability:.1%}")
    k4.metric("Flank wear VB", f"{tool.vb_mm:.3f} mm", tool.stage)
    k5.metric("Wear rate", f"{tool.wear_rate_um_s:.2f} μm/s", f"{tool.wear_rate_um_min:.0f} μm/min")
    k6.metric("Temperature", f"{tool.temperature_c:.1f} °C", f"model {tool.predicted_temperature_c:.1f} °C")

    control_ra = ra_true if ra_true is not None else fc.predicted_ra_um
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Tool health", f"{tool.tool_health_pct:.0f}%", "100% = new, 0% = VB 0.30 mm")
    m2.metric("Ra used for stop/control", f"{control_ra:.2f} μm", f"desired {ra_set:.2f} · hard stop {ra_hard:.2f}")
    m3.metric("Timer to Ra hard stop", _fmt_eta(ra_eta), "also stops at M30 when the CNC program ends")
    m4.metric("ML predicted Ra", f"{fc.predicted_ra_um:.2f} μm", "not used for the stop if true Ra exists")

    a1, a2, a3, a4 = st.columns(4)
    rul = getattr(tool, "remaining_life_s", None)
    a1.metric("Remaining useful life", _fmt_eta(rul) if rul is not None else "—", "time to VB 0.30 mm (model)")
    a2.metric("Anomaly score", f"{getattr(tool, 'anomaly_score', 0.0):.2f}", "Isolation Forest · 0 normal, 1 odd")
    a3.metric("Material removal rate", f"{getattr(tool, 'mrr_cm3_min', 0.0):.2f} cm³/min", "ap · ae · vf")
    a4.metric("Specific cutting energy", f"{getattr(tool, 'specific_energy_j_mm3', 0.0):.3f} J/mm³", "P / MRR")

    truth_bits = []
    if ra_true is not None:
        truth_bits.append(f"true Ra = {ra_true:.2f} μm")
    if vb_true is not None:
        truth_bits.append(f"true VB = {vb_true:.3f} mm")
    truth = f" ({'; '.join(truth_bits)})." if truth_bits else "."
    st.markdown(
        f"<div class='panel'><b>Decision support</b> — {fc.recommendation}<br>"
        f"<span class='muted'>Model: {fc.trained_on}. Lab Ra and VB are still required "
        f"before you treat numbers as experimental results{truth}</span></div>",
        unsafe_allow_html=True,
    )

    ctrl = st.session_state.get("control")
    if ctrl is not None:
        decision = ctrl["decision"]
        limits = ctrl["limits"]
        st.markdown(
            f"<div class='panel'><b>Auto supervisor</b> — {decision.message}<br>"
            f"<span class='muted'>Feed {result.frame.feed_mm_tooth:.3f} mm/tooth · "
            f"spindle {result.frame.rpm:.0f} rpm"
            + (f" · next feed {decision.feed_mm_tooth:.3f}" if decision.action == "reduce_feed" else "")
            + (f" · next rpm {decision.rpm:.0f}" if decision.action == "reduce_rpm" else "")
            + "</span></div>",
            unsafe_allow_html=True,
        )
        st.table(
            {
                "Parameter": [lim.label for lim in limits],
                "Now": [f"{lim.value:.3g} {lim.unit}" for lim in limits],
                "Desired max": [f"{lim.setpoint:.3g} {lim.unit}" for lim in limits],
                "Hard stop": [f"{lim.stop_limit:.3g} {lim.unit}" for lim in limits],
                "State": [
                    "STOP" if lim.enabled and lim.value >= lim.stop_limit
                    else "ALERT" if lim.enabled and lim.stop_limit > 0 and lim.value >= 0.85 * lim.stop_limit
                    else "HIGH" if lim.enabled and lim.value > lim.setpoint
                    else "OK"
                    for lim in limits
                ],
            }
        )

    left, right = st.columns((1.35, 1.0))
    times = list(st.session_state.history["t"])
    with left:
        st.plotly_chart(
            waveform_fig(result.frame.vibration, result.frame.sample_rate_hz, "Vibration window", "#6EA8FF", "g"),
            width="stretch",
        )
        st.plotly_chart(
            waveform_fig(result.frame.force, result.frame.sample_rate_hz, "Cutting force window", "#D15A2A", "N"),
            width="stretch",
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Vibration RMS", f"{result.features.vib_rms:.3f}")
        c2.metric("Force RMS", f"{result.features.force_rms:.1f} N")
        c3.metric("Spindle power", f"{result.features.spindle_power_w:.0f} W")
        c4.metric("Temp vs model", f"{tool.temperature_c - tool.predicted_temperature_c:+.1f} °C")
        st.plotly_chart(
            history_fig(times, list(st.session_state.history["ra"]), "Ra used for control / stop", "#C48A1A", "μm", hline=ra_hard),
            width="stretch",
        )
        st.plotly_chart(contrib_fig(fc.contributions), width="stretch")

    with right:
        st.plotly_chart(
            history_fig(times, list(st.session_state.history["p"]), "Degradation probability", "#C43A3A", "P(D=1)"),
            width="stretch",
        )
        st.plotly_chart(
            history_fig(times, list(st.session_state.history["vb"]), "Flank wear VB", "#A78BFA", "mm", hline=0.30),
            width="stretch",
        )
        st.plotly_chart(
            history_fig(times, list(st.session_state.history["temp"]), "Cutting temperature", "#D15A2A", "°C"),
            width="stretch",
        )
        st.plotly_chart(
            history_fig(times, list(st.session_state.history["rate"]), "Tool wear rate", "#6EA8FF", "μm/s"),
            width="stretch",
        )
        if st.session_state.history["feed"]:
            st.plotly_chart(
                history_fig(times, list(st.session_state.history["feed"]), "Commanded feed", "#3D9A6A", "mm/tooth"),
                width="stretch",
            )

    st.caption(
        f"Source {result.frame.source_name} · t = {result.frame.time_s:.1f} s · "
        f"Vc = {result.frame.cutting_speed_m_min:.1f} m/min · "
        f"physics residual = {result.features.physics_residual:.3f} · "
        f"regime: {result.regime.name}"
    )

    with st.expander("How this dashboard connects to the machine"):
        st.markdown(_ARCHITECTURE_MD)

    if st.session_state.running:
        time.sleep(max(cfg["dashboard"]["refresh_ms"] / 1000.0, 0.05))
        st.rerun()


_ARCHITECTURE_MD = """
This page is the **integrity monitor only**. The CNC mill stays on the other laptop.

ForgeMill on Vercel has no Cycle-start API (it is only a browser page). This project
injects the hook itself by serving the same mill at **http://THIS-PC:8766/**.

**Then**  
Other laptop (same Wi‑Fi): open that hooked mill URL. Press **Cycle start**.  
This page auto-starts the **simulator** (no Start run) so you see live readings here.  
During the cut it checks Ra / VB / temp / vibration against hard-stop.  
It stops when the cycle stops (Hold, Stop) or when a hard-stop is exceeded.

Do not treat software STOP as a certified CNC e-stop.
"""


if __name__ == "__main__":
    main()
