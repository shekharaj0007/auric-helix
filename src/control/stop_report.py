"""Build a downloadable incident PDF when the mill / monitor stops."""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    ListFlowable,
    ListItem,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "stop_reports"

NAVY = colors.HexColor("#0B1F3A")
GOLD = colors.HexColor("#C9A227")
RED = colors.HexColor("#9B2C2C")
INK = colors.HexColor("#1C242E")


def _f(v, fmt="{:.3g}", dash="—"):
    if v is None:
        return dash
    try:
        return fmt.format(float(v))
    except (TypeError, ValueError):
        return str(v)


def diagnose(record: dict) -> tuple[list[str], list[str]]:
    """Problems that caused / accompanied the stop, and actions to take."""
    reason = str(record.get("reason") or "")
    problems: list[str] = []
    actions: list[str] = []
    low = reason.lower()

    if "machining complete" in low or "m30" in low or "cycle" in low:
        problems.append(
            "The CNC programme ended (Cycle stop / M30 / Hold). This is a normal programme end, "
            "not necessarily a surface-integrity failure."
        )
        actions.append("Inspect the last pass visually. If Regime C or D was showing, measure Ra on a profilometer.")
    if "hard stop" in low or "halted automatically" in low:
        problems.append("A typed physical hard-stop limit was crossed. The supervisor requested software Hold.")
    if "roughness" in low or " ra" in low:
        problems.append("Predicted / used roughness Ra reached the operator hard-stop (default 1.6 µm). The surface is treated as degraded for this B.Tech proxy.")
        actions.extend(
            [
                "Do not continue finishing on this face without inspection.",
                "Measure Ra with a stylus if a coupon is available.",
                "Reduce feed per tooth by about 8–10 % on the next pass, or change the end mill if VB is also high.",
                "Check for built-up edge and cloudy lay on the aluminium.",
            ]
        )
    if "flank wear" in low or " vb" in low:
        problems.append("Flank wear VB reached the demo ISO 8688-style limit (0.30 mm) or the operator stop.")
        actions.extend(
            [
                "Change the tool. Do not keep milling with a worn land.",
                "Photograph the flank if this is a lab campaign.",
                "Reduce cutting speed if wear rate was also high (Taylor-type response).",
            ]
        )
    if "wear rate" in low:
        problems.append("Tool wear rate (µm/s) crossed the operator hard-stop. The land is growing too fast for this window.")
        actions.extend(
            [
                "Reduce spindle speed and/or feed. Wear rate rises with Vc and chip load.",
                "Check coolant / air blast on Al 6061 (built-up edge accelerates wear).",
                "Inspect the edge under a microscope or loupe before the next coupon.",
            ]
        )
    if "temperature" in low:
        problems.append("Bulk / sensor temperature crossed the typed thermal stop.")
        actions.extend(
            [
                "Reduce rpm (cutting speed drives heat).",
                "Check coolant flow and chip evacuation.",
                "Allow a short dwell; temperature in this monitor is lagged bulk, not shear-zone temperature.",
            ]
        )
    if "vibration" in low:
        problems.append("Vibration RMS crossed the typed stop — possible chatter or a loose fixture.")
        actions.extend(
            [
                "Reduce axial depth or feed. Chatter often lives away from the tooth-passing frequency.",
                "Check vice clamp, tool stick-out and spindle bearings.",
                "Do not increase rpm blindly; first look at the chatter-frequency reading.",
            ]
        )
    if "force" in low:
        problems.append("Cutting-force RMS crossed the typed stop — chip load or dulling is high.")
        actions.extend(
            [
                "Reduce feed per tooth.",
                "Inspect the tool for chipping or BUE.",
            ]
        )
    if "risk" in low or "probability" in low:
        problems.append("Degradation probability was high. In the delivered design this is a warning, not a certified trip.")
        actions.append("Treat probability as decision support. Confirm with Ra/VB/vibration before scrapping a plate.")

    ra = record.get("ra_um")
    vb = record.get("vb_mm")
    risk = record.get("risk")
    regime = str(record.get("regime") or "")
    residual = record.get("physics_residual")
    chatter = record.get("chatter_hz")
    form_e = record.get("form_error_um")

    if ra is not None and float(ra) >= 1.55:
        problems.append(f"Predicted Ra is {float(ra):.2f} µm, at or near the 1.6 µm specification.")
    if vb is not None and float(vb) >= 0.22:
        problems.append(f"Predicted flank wear VB is {float(vb):.3f} mm (demo 100 % life = 0.30 mm).")
    if risk is not None and float(risk) >= 0.70:
        problems.append(f"Short-horizon degradation probability is {100*float(risk):.0f} %. Current Ra may still be legal — this is the early-warning window.")
    if "Regime C" in regime or "Regime D" in regime or "Unstable" in regime or "Severe" in regime:
        problems.append(f"Latent regime at stop: {regime}. The cut has left the stable neighbourhood.")
        actions.append("Finish only if the drawing allows; otherwise Hold, inspect chips and surface, then change the tool.")
    if residual is not None and float(residual) >= 0.25:
        problems.append(f"Physics residual is {float(residual):.2f} — measured power disagrees with Fc · Vc. Check sensors or chip jamming.")
        actions.append("Verify current clamp / force channel. A large residual is a sensing-chain or process-fault flag, not a roughness number.")
    if form_e is not None and float(form_e) >= 0.4:
        problems.append(f"Chatter-driven form/waviness estimate is {float(form_e):.2f} µm. Rz/Rt will look worse than Ra.")
        actions.append("If Rz is out of spec even when Ra is close to 1.6 µm, treat chatter, not only average roughness.")
    if chatter is not None and float(chatter) > 0:
        actions.append(f"Dominant frequency at stop ≈ {float(chatter):.0f} Hz. Compare with tooth-passing frequency (rpm × flutes / 60).")

    if not problems:
        problems.append("Stop was recorded. No single hard-limit keyword was parsed; see the measured table and the reason line.")
    if not actions:
        actions.extend(
            [
                "Inspect the tool and the last milled face before restarting.",
                "If this was a demo, restart with Start run / Cycle start. Do not treat software Hold as an emergency stop.",
                "For a laboratory campaign: log this PDF with the job card, then measure Ra and photograph VB.",
            ]
        )
    actions.append("Software Hold is not a certified Category-0/1 e-stop. A licensed operator owns the real machine.")
    actions.append("Numbers from the physics simulator are not profilometer / microscope laboratory results until labels are measured.")
    # de-duplicate while keeping order
    def _uniq(items: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for it in items:
            if it not in seen:
                seen.add(it)
                out.append(it)
        return out

    return _uniq(problems), _uniq(actions)


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle("t", parent=base["Title"], fontName="Times-Bold", fontSize=16, textColor=NAVY, spaceAfter=4, alignment=TA_CENTER),
        "sub": ParagraphStyle("s", parent=base["Normal"], fontName="Times-Italic", fontSize=10, textColor=INK, alignment=TA_CENTER, spaceAfter=10),
        "h": ParagraphStyle("h", parent=base["Heading2"], fontName="Times-Bold", fontSize=12, textColor=NAVY, spaceBefore=10, spaceAfter=6),
        "body": ParagraphStyle("b", parent=base["Normal"], fontName="Times-Roman", fontSize=10, leading=14, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6),
        "warn": ParagraphStyle("w", parent=base["Normal"], fontName="Times-Bold", fontSize=10, textColor=RED, alignment=TA_LEFT, spaceAfter=8),
        "small": ParagraphStyle("sm", parent=base["Normal"], fontName="Times-Italic", fontSize=8, textColor=INK, alignment=TA_CENTER, spaceBefore=12),
        "cell": ParagraphStyle("c", parent=base["Normal"], fontName="Times-Roman", fontSize=9, leading=12, textColor=INK),
    }
    return styles


def _table(rows: list[list[str]], col_w=None):
    data = [[Paragraph(str(c), ParagraphStyle("x", fontName="Times-Bold" if i == 0 else "Times-Roman", fontSize=9, textColor=colors.white if i == 0 else INK, leading=12)) for c in row] for i, row in enumerate(rows)]
    t = Table(data, colWidths=col_w, hAlign="CENTER")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F4F7FA")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F4F7FA"), colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C5CDD6")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def build_stop_pdf(record: dict, extra: dict | None = None) -> bytes:
    extra = extra or {}
    problems, actions = diagnose(record)
    styles = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="CNC stop incident report",
        author="IIT Patna B.Tech machining integrity monitor",
    )
    story = []
    story.append(Paragraph("Department of Mechanical Engineering · Indian Institute of Technology Patna", styles["sub"]))
    story.append(Paragraph("CNC Milling Stop / Hold Incident Report", styles["title"]))
    story.append(Paragraph("Physics-informed multimodal integrity monitor · Al 6061 end milling", styles["sub"]))
    story.append(Paragraph(f"<b>Stop reason:</b> {record.get('reason') or '—'}", styles["warn"]))
    story.append(
        Paragraph(
            f"Time (UTC): {record.get('timestamp_utc') or datetime.now(timezone.utc).isoformat(timespec='seconds')} "
            f"· Cut time: {_f(record.get('time_s'), '{:.1f}')} s "
            f"· Regime: {record.get('regime') or '—'}",
            styles["body"],
        )
    )

    story.append(Paragraph("1. Where the machine stopped", styles["h"]))
    story.append(
        Paragraph(
            "These coordinates are the DRO pose at Hold / hard-stop. They are not a return-to-origin. "
            "Use them to find the feature on the plate that was being cut when the warning fired.",
            styles["body"],
        )
    )
    story.append(
        _table(
            [
                ["Axis", "Position"],
                ["X", f"{_f(record.get('x_mm'), '{:.3f}')} mm"],
                ["Y", f"{_f(record.get('y_mm'), '{:.3f}')} mm"],
                ["Z", f"{_f(record.get('z_mm'), '{:.3f}')} mm"],
                ["Spindle", f"{_f(record.get('rpm'), '{:.0f}')} r/min"],
                ["Feed", f"{_f(record.get('feed_mm_tooth'), '{:.3f}')} mm/tooth"],
            ],
            [90 * mm, 80 * mm],
        )
    )

    story.append(Paragraph("2. What went wrong (diagnosis)", styles["h"]))
    story.append(
        ListFlowable(
            [ListItem(Paragraph(p, styles["body"]), leftIndent=8) for p in problems],
            bulletType="bullet",
        )
    )

    story.append(Paragraph("3. Measured / predicted parameters at stop", styles["h"]))
    story.append(
        Paragraph(
            "Live Ra on the dashboard is a <b>prediction</b> unless a profilometer value was typed. "
            "VB is a model of flank wear, not a microscope photograph, until a lab campaign is logged.",
            styles["body"],
        )
    )
    story.append(
        _table(
            [
                ["Quantity", "Value at stop", "What it means"],
                ["Ra (mean roughness)", f"{_f(record.get('ra_um'), '{:.2f}')} µm", "B.Tech surface-integrity proxy"],
                ["Rq (RMS roughness)", f"{_f(record.get('rq_um'), '{:.2f}')} µm", "ISO RMS height"],
                ["Rz (ten-point)", f"{_f(record.get('rz_um'), '{:.2f}')} µm", "Peak-to-valley family"],
                ["Rt (total)", f"{_f(record.get('rt_um'), '{:.2f}')} µm", "Max peak to max valley"],
                ["Form / waviness", f"{_f(record.get('form_error_um'), '{:.2f}')} µm", "Chatter-driven extra geometry"],
                ["Chatter frequency", f"{_f(record.get('chatter_hz'), '{:.0f}')} Hz", "Dominant unstable line"],
                ["Flank wear VB", f"{_f(record.get('vb_mm'), '{:.3f}')} mm", "Demo limit 0.30 mm"],
                ["Wear rate", f"{_f(record.get('wear_rate_um_s'), '{:.2f}')} µm/s", "How fast the land is growing"],
                ["Remaining useful life", f"{_f(record.get('rul_s'), '{:.0f}')} s", "Time to VB = 0.30 mm (model)"],
                ["Temperature", f"{_f(record.get('temperature_c'), '{:.1f}')} °C", "Lagged bulk / sensor"],
                ["Degradation risk (30 s)", f"{_f((record.get('risk') or 0)*100, '{:.0f}')} %", "Warning, not e-stop"],
                ["Vibration RMS", f"{_f(record.get('vib_rms'), '{:.3f}')} g", "Energy of the cut"],
                ["Force RMS", f"{_f(record.get('force_rms'), '{:.1f}')} N", "Cutting load"],
                ["Spindle power", f"{_f(record.get('power_w'), '{:.0f}')} W", "Motor spend"],
                ["Physics residual", f"{_f(record.get('physics_residual'), '{:.3f}')}", "P vs Fc·Vc disagreement"],
                ["MRR", f"{_f(record.get('mrr_cm3_min'), '{:.2f}')} cm³/min", "ap · ae · vf"],
                ["Specific energy", f"{_f(record.get('specific_energy_j_mm3'), '{:.3f}')} J/mm³", "P / MRR"],
                ["Anomaly score", f"{_f(record.get('anomaly_score'), '{:.2f}')}", "0 normal · 1 odd"],
                ["Tool health", f"{_f(record.get('tool_health_pct'), '{:.0f}')} %", "100 % new · 0 % at VB 0.30"],
            ],
            [55 * mm, 40 * mm, 75 * mm],
        )
    )

    limits = extra.get("limits") or record.get("limits")
    if limits:
        story.append(Paragraph("4. Operator limits versus values at stop", styles["h"]))
        rows = [["Parameter", "Now", "Desired max", "Hard stop", "State"]]
        for lim in limits:
            rows.append([str(x) for x in lim])
        story.append(_table(rows, [38 * mm, 32 * mm, 32 * mm, 32 * mm, 28 * mm]))

    contrib = extra.get("contributions") or record.get("contributions")
    if contrib:
        story.append(Paragraph("5. Why the model was worried (feature contributions)", styles["h"]))
        crows = [["Feature", "Relative contribution (%)"]]
        for k, v in list(contrib.items())[:8]:
            crows.append([str(k), f"{float(v):.1f}"])
        story.append(_table(crows, [110 * mm, 60 * mm]))

    rec_txt = extra.get("recommendation") or record.get("recommendation")
    if rec_txt:
        story.append(Paragraph("6. Monitor recommendation at the instant of stop", styles["h"]))
        story.append(Paragraph(str(rec_txt), styles["body"]))

    story.append(Paragraph("7. Measures that can be taken", styles["h"]))
    story.append(
        ListFlowable(
            [ListItem(Paragraph(a, styles["body"]), leftIndent=8) for a in actions],
            bulletType="bullet",
        )
    )

    story.append(Paragraph("8. How to read this report", styles["h"]))
    story.append(
        Paragraph(
            "This PDF is an incident sheet for the operator and the examiner. It records the DRO pose, "
            "the predicted texture family (Ra, Rq, Rz, Rt), tool state, and the physics residual. "
            "It does not certify a Fanuc/Siemens e-stop, and it does not replace a stylus roughness "
            "measurement or a flank-wear photograph. If a laboratory campaign is booked, staple this "
            "sheet to the job card together with the measured Ra and the VB photo.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "IIT Patna  ·  B.Tech project  ·  Rajshekhar & Piyush Jatoliya  ·  Guide: Dr. Mahavir Singh  ·  "
            "Software Hold ≠ certified e-stop  ·  Simulated labels ≠ laboratory results",
            styles["small"],
        )
    )
    doc.build(story)
    return buf.getvalue()


def save_stop_pdf(record: dict, extra: dict | None = None) -> tuple[Path, bytes]:
    pdf = build_stop_pdf(record, extra)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUT_DIR / f"stop_report_{stamp}.pdf"
    path.write_bytes(pdf)
    return path, pdf
