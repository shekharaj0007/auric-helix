"""Detailed concept / STAR / ML / market report for the machining integrity site."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "concept_figures"
OUT = ROOT / "docs" / "Project_Concept_and_Working_Report.pdf"
DOWNLOADS = Path.home() / "Downloads" / "Project_Concept_and_Working_Report.pdf"

NAVY = colors.HexColor("#0B1F3A")
GOLD = colors.HexColor("#C9A227")
INK = colors.HexColor("#1C242E")
RULE = colors.HexColor("#C5CDD6")
PALE = colors.HexColor("#F4F7FA")

for name, path in {
    "TNR": r"C:\Windows\Fonts\times.ttf",
    "TNR-B": r"C:\Windows\Fonts\timesbd.ttf",
    "TNR-I": r"C:\Windows\Fonts\timesi.ttf",
    "TNR-BI": r"C:\Windows\Fonts\timesbi.ttf",
}.items():
    if Path(path).exists():
        pdfmetrics.registerFont(TTFont(name, path))

BODY = "TNR" if "TNR" in pdfmetrics.getRegisteredFontNames() else "Times-Roman"
BOLD = "TNR-B" if "TNR-B" in pdfmetrics.getRegisteredFontNames() else "Times-Bold"
ITAL = "TNR-I" if "TNR-I" in pdfmetrics.getRegisteredFontNames() else "Times-Italic"
BI = "TNR-BI" if "TNR-BI" in pdfmetrics.getRegisteredFontNames() else "Times-BoldItalic"


def _styles():
    base = getSampleStyleSheet()
    return {
        "cover_kicker": ParagraphStyle("ck", fontName=ITAL, fontSize=11, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8),
        "cover": ParagraphStyle("cv", fontName=BOLD, fontSize=20, leading=26, textColor=NAVY, alignment=TA_CENTER, spaceAfter=10),
        "cover_sub": ParagraphStyle("cs", fontName=ITAL, fontSize=12, leading=16, textColor=INK, alignment=TA_CENTER, spaceAfter=6),
        "meta": ParagraphStyle("mt", fontName=BODY, fontSize=11, leading=16, alignment=TA_CENTER, textColor=INK, spaceAfter=4),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName=BOLD, fontSize=14, leading=18, textColor=NAVY, spaceBefore=14, spaceAfter=8, borderPadding=0),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName=BOLD, fontSize=12, leading=16, textColor=NAVY, spaceBefore=10, spaceAfter=6),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontName=BI, fontSize=11, leading=14, textColor=INK, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("bd", fontName=BODY, fontSize=10.5, leading=15, alignment=TA_JUSTIFY, textColor=INK, spaceAfter=7),
        "bullet": ParagraphStyle("bu", fontName=BODY, fontSize=10.5, leading=14.5, alignment=TA_LEFT, textColor=INK, leftIndent=4),
        "caption": ParagraphStyle("cap", fontName=ITAL, fontSize=9, leading=12, alignment=TA_CENTER, textColor=INK, spaceBefore=3, spaceAfter=10),
        "warn": ParagraphStyle("wn", fontName=ITAL, fontSize=9.5, leading=13, alignment=TA_JUSTIFY, textColor=colors.HexColor("#6B2A2A"), spaceAfter=8),
        "toc": ParagraphStyle("toc", fontName=BODY, fontSize=11, leading=18, textColor=INK),
        "footer": ParagraphStyle("ft", fontName=ITAL, fontSize=8, textColor=INK, alignment=TA_CENTER),
        "cell": ParagraphStyle("cl", fontName=BODY, fontSize=8.5, leading=11.5, textColor=INK),
        "cellb": ParagraphStyle("clb", fontName=BOLD, fontSize=8.5, leading=11.5, textColor=colors.white),
        "eq": ParagraphStyle("eq", fontName=ITAL, fontSize=10.5, leading=15, alignment=TA_CENTER, textColor=NAVY, spaceBefore=4, spaceAfter=8),
    }


S = _styles()


def P(text, style="body"):
    return Paragraph(text, S[style])


def H(text, level=1):
    return Paragraph(text, S[f"h{level}"])


def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(it, S["bullet"]), leftIndent=10, bulletColor=NAVY) for it in items],
        bulletType="bullet",
        leftIndent=16,
        spaceAfter=8,
    )


def _box(ax, x, y, w, h, text, fc="#0B1F3A", ec="#C9A227", tc="white", fs=8.2):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", linewidth=1.2, facecolor=fc, edgecolor=ec)
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc, fontsize=fs, wrap=True)


def make_figures():
    FIG.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "Times New Roman", "figure.facecolor": "white", "axes.facecolor": "white"})

    fig, ax = plt.subplots(figsize=(11.2, 4.4))
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    boxes = [
        (0.15, 1.5, 1.7, 1.5, "CNC / ForgeMill\nor Arduino DAQ\nor physics twin", "#0B1F3A"),
        (2.15, 1.5, 1.7, 1.5, "SensorFrame\n0.25 s window\nvib, force, P, T\nrpm, feed", "#163A5F"),
        (4.15, 1.5, 1.7, 1.5, "16-D features\nRMS, kurtosis\nFFT bands\nP≈Fc·Vc residual", "#1E4D73"),
        (6.15, 1.5, 1.7, 1.5, "ML stack\nGMM A–D\nHGB heads\nIsolation Forest", "#2A5F7A"),
        (8.15, 1.5, 2.7, 1.5, "Shop-floor site\nstatus, KPIs, plots\nsupervisor Hold\nstop-incident PDF", "#C9A227"),
    ]
    for x, y, w, h, t, c in boxes:
        _box(ax, x, y, w, h, t, fc=c, tc="white" if c != "#C9A227" else "#0B1F3A")
    for x in (1.85, 3.85, 5.85, 7.85):
        ax.annotate("", xy=(x + 0.28, 2.25), xytext=(x, 2.25), arrowprops=dict(arrowstyle="->", color="#0B1F3A", lw=1.6))
    ax.set_title("End-to-end working chain of the site", fontsize=12, color="#0B1F3A", pad=8)
    fig.tight_layout()
    fig.savefig(FIG / "pipeline.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11.2, 5.2))
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    _box(ax, 4.35, 2.15, 2.5, 1.0, "Cut mechanics\nVc, fz, ap, ae, MRR", "#0B1F3A")
    nodes = [
        (0.3, 3.9, "Spindle rpm N\n→ Vc, tooth Hz"),
        (4.35, 4.0, "Feed/tooth fz\n→ force, Ra, MRR"),
        (8.4, 3.9, "Depth / width\n→ MRR, force"),
        (0.3, 0.35, "Vibration / chatter\n→ Rz, Rt, form"),
        (4.35, 0.25, "Flank wear VB\n→ force, Ra, heat"),
        (8.4, 0.35, "Power / residual\n→ sensing health"),
        (0.3, 2.15, "Temperature\n→ Ra, wear rate"),
        (8.4, 2.15, "Surface Ra–Rt\nintegrity proxy"),
    ]
    for x, y, t in nodes:
        _box(ax, x, y, 2.5, 0.95, t, fc="#F4F7FA", ec="#0B1F3A", tc="#0B1F3A", fs=8)
    pairs = [
        ((5.6, 3.15), (5.6, 4.0)),
        ((4.35, 2.65), (2.8, 2.6)),
        ((6.85, 2.65), (8.4, 2.6)),
        ((5.6, 2.15), (5.6, 1.2)),
        ((4.35, 2.4), (2.8, 4.0)),
        ((6.85, 2.4), (8.4, 4.0)),
        ((2.8, 2.15), (2.8, 1.3)),
        ((8.4, 2.15), (8.4, 1.3)),
    ]
    for a, b in pairs:
        ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="<->", color="#C9A227", lw=1.2))
    ax.set_title("How the calculated quantities couple in the mill", fontsize=12, color="#0B1F3A")
    fig.tight_layout()
    fig.savefig(FIG / "coupling.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11.2, 3.6))
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 3.6)
    ax.axis("off")
    star = [
        (0.25, 0.7, "S  Situation", "Al 6061 end milling.\nRa is measured too late.\nScrap is already cut."),
        (3.0, 0.7, "T  Task", "Warn before Ra / VB\ncross spec. Discover\nlatent regimes live."),
        (5.75, 0.7, "A  Action", "SensorFrame → 16-D\nGMM + HGB + IF\nsupervisor + PDF."),
        (8.5, 0.7, "R  Result", "Shop-floor site.\nEarly risk, Hold pose,\nincident report."),
    ]
    cols = ["#0B1F3A", "#163A5F", "#1E4D73", "#C9A227"]
    tcs = ["white", "white", "white", "#0B1F3A"]
    for (x, y, h, b), c, tc in zip(star, cols, tcs):
        _box(ax, x, y + 1.7, 2.45, 0.7, h, fc=c, tc=tc, fs=10)
        _box(ax, x, y, 2.45, 1.65, b, fc="#F4F7FA", ec=c, tc="#0B1F3A", fs=8.4)
    ax.set_title("STAR working principle of this project", fontsize=12, color="#0B1F3A")
    fig.tight_layout()
    fig.savefig(FIG / "star.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    ax.axis("off")
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 4.8)
    layers = [
        (0.2, 3.55, "Site — Streamlit dashboard (status, KPIs, plots, limits, stop PDF)"),
        (0.2, 2.7, "Control — supervisor (desired max / hard stop) · JSONL log · incident PDF"),
        (0.2, 1.85, "ML — GMM regimes · 11 HGB heads · Isolation Forest · permutation importance"),
        (0.2, 1.0, "Features — 16-D vector + physics residual P ≈ Pidle + Fc·Vc · MRR · u"),
        (0.2, 0.15, "Sources — simulator twin · HTTP mill bridge :8766 · Arduino serial · SensorFrame contract"),
    ]
    fcs = ["#C9A227", "#2A5F7A", "#1E4D73", "#163A5F", "#0B1F3A"]
    tcs = ["#0B1F3A", "white", "white", "white", "white"]
    for (x, y, t), fc, tc in zip(layers, fcs, tcs):
        _box(ax, x, y, 10.8, 0.7, t, fc=fc, tc=tc, fs=10)
    ax.set_title("What the site is, layer by layer", fontsize=12, color="#0B1F3A")
    fig.tight_layout()
    fig.savefig(FIG / "layers.png", dpi=160)
    plt.close(fig)


def table(rows, widths):
    data = []
    for i, row in enumerate(rows):
        sty = S["cellb"] if i == 0 else S["cell"]
        data.append([Paragraph(str(c), sty) for c in row])
    t = Table(data, colWidths=widths, hAlign="CENTER")
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), PALE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PALE, colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.35, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def img(name, w=170 * mm):
    path = FIG / name
    im = Image(str(path), width=w, height=w * 0.42 if "pipeline" in name or "star" in name else w * 0.46)
    if "coupling" in name:
        im.drawHeight = w * 0.48
    if "layers" in name:
        im.drawHeight = w * 0.44
    return im


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 10 * mm, A4[0], 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, A4[1] - 10.6 * mm, A4[0], 0.6 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Times-Italic", 8)
    canvas.drawString(18 * mm, A4[1] - 7 * mm, "IIT Patna  ·  Department of Mechanical Engineering  ·  B.Tech Project")
    canvas.drawRightString(A4[0] - 18 * mm, A4[1] - 7 * mm, "Machining Integrity Monitor")
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, A4[0], 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, 10 * mm, A4[0], 0.5 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Times-Roman", 8)
    canvas.drawString(18 * mm, 4 * mm, "Software Hold is not a certified e-stop  ·  Simulated labels are not laboratory results")
    canvas.drawRightString(A4[0] - 18 * mm, 4 * mm, f"Page {doc.page}")
    canvas.restoreState()


def story():
    s = []
    s.append(Spacer(1, 18 * mm))
    s.append(P("Indian Institute of Technology Patna", "cover_kicker"))
    s.append(P("Department of Mechanical Engineering", "cover_kicker"))
    s.append(Spacer(1, 6 * mm))
    s.append(
        P(
            "Physics-Informed Multimodal Learning for Latent Regime Discovery "
            "and Early Surface-Integrity Degradation Prediction in CNC Milling of Aluminium Alloy (Al 6061)",
            "cover",
        )
    )
    s.append(
        P(
            "A detailed concept report of the live site: objectives, STAR working principle, "
            "mechanical theory, parameter coupling, calculations and their effects, complete machine-learning "
            "pipeline, algorithms used, work completed, and industrial / market impact.",
            "cover_sub",
        )
    )
    s.append(Spacer(1, 8 * mm))
    s.append(P("<b>Presented by</b>", "meta"))
    s.append(P("Rajshekhar  ·  Piyush Jatoliya", "meta"))
    s.append(P("<b>Supervisor</b>", "meta"))
    s.append(P("Dr. Mahavir Singh", "meta"))
    s.append(P("B.Tech Project  ·  November 2026", "meta"))
    s.append(Spacer(1, 10 * mm))
    s.append(
        P(
            "This document explains the shop-floor site itself. It is not a claim of XRD residual-stress "
            "integrity, not a certified Category-0/1 emergency stop, and not a laboratory profilometer campaign. "
            "The B.Tech surface-integrity proxy is D = 1 when predicted or measured Ra exceeds the specification "
            "(default 1.6 µm). Training numbers are physics-simulated.",
            "warn",
        )
    )
    s.append(PageBreak())

    s.append(H("Contents"))
    s.append(
        P(
            "1. What this site is and why it exists<br/>"
            "2. Objectives of the project<br/>"
            "3. Working principle in the STAR method<br/>"
            "4. How the work is actually done (architecture of the site)<br/>"
            "5. Every concept the operator sees on the site<br/>"
            "6. Mechanical theory and how it is applied here<br/>"
            "7. How the parameters are related to one another<br/>"
            "8. What we calculate, why these quantities only, and what effects they create<br/>"
            "9. Complete machine-learning pipeline and algorithms<br/>"
            "10. What has been built<br/>"
            "11. Market effect and why this class of system can change shop-floor quality<br/>"
            "12. Limits, honesty, and what would make the next step a laboratory thesis<br/>"
            "13. Closing statement",
            "toc",
        )
    )
    s.append(PageBreak())

    # 1
    s.append(H("1. What this site is and why it exists"))
    s.append(
        P(
            "The site is a Streamlit shop-floor monitor titled <i>Early surface-integrity warning</i>. "
            "It sits next to a CNC milling programme. Every 0.25 s it consumes a multimodal window of "
            "vibration, cutting force, spindle power, temperature, commanded rpm and feed. From that window "
            "it does three jobs that a conventional DRO or G-code player does not do: it names the latent "
            "cutting regime (A stable → D severe), it predicts whether the surface or the tool will be out "
            "of specification inside a short horizon (default 30 s), and it can Hold the interpolator when a "
            "typed physical limit is crossed. When the programme stops, it writes an incident PDF so the "
            "operator can see why it stopped, what was measured, and what can be done next."
        )
    )
    s.append(
        P(
            "The industrial problem is simple and expensive. Arithmetic roughness Ra and flank-wear land VB "
            "are the quantities that decide whether an aluminium face is acceptable and whether an end mill "
            "is still a tool. Both are usually measured after the pass — stylus for Ra, microscope for VB. "
            "By then the scrap is already on the table. Vibration, force and power, by contrast, are cheap "
            "to stream during the cut. The hypothesis of this B.Tech project is that a physics-informed "
            "multimodal model can turn those live signals into an early warning of surface-integrity "
            "degradation, using Ra ≥ 1.6 µm (and VB ≥ 0.30 mm in the demo) as the binary integrity event."
        )
    )
    s.append(img("layers.png"))
    s.append(P("Figure 1. The site is five layers: sources, features, ML, control, and the operator UI.", "caption"))
    s.append(
        P(
            "The mill the dashboard talks to in the current demo is a hooked ForgeMill page served locally "
            "at http://127.0.0.1:8766/ (LAN equivalent on the CNC laptop). The Vercel URL is the visual mill; "
            "it has no /telemetry API. A reverse proxy, scripts/cnc_bridge.py, is the machine link. Mixed "
            "content (HTTPS mill fetching HTTP localhost) is why the hooked HTTP mill is the working path. "
            "Software Hold freezes pose; it is not a certified e-stop. Dr. Mahavir Singh is the academic "
            "supervisor, not a certified CNC emergency-stop authority."
        )
    )

    # 2
    s.append(H("2. Objectives of the project"))
    s.append(H("2.1 Academic objectives", 2))
    s.append(
        bullets(
            [
                "State a B.Tech-legal surface-integrity proxy: D = 1 when Ra exceeds specification (default 1.6 µm), with VB = 0.30 mm as the ISO 8688-style tool-life ceiling in the demo. Do not claim residual stress unless an XRD campaign is booked.",
                "Show that unlabeled windows of milling signals occupy a small number of latent regimes, discovered by a Gaussian mixture on a 16-dimensional feature vector.",
                "Show that a short-horizon classifier can raise P(degradation in 30 s) before Ra itself is out of spec — that is the early-warning claim.",
                "Keep every recommendation inspectable: feature contributions, physics residual, and a written decision-support sentence. No black-box “AI said stop”.",
                "Keep the sensor contract (SensorFrame) independent of the mill, so a simulator, an Arduino, or an NI-DAQ can feed the same models.",
            ]
        )
    )
    s.append(H("2.2 Shop-floor objectives", 2))
    s.append(
        bullets(
            [
                "Give the operator one screen: machine status, DRO XYZ, texture family (Ra, Rq, Rz, Rt), tool health, wear rate, temperature, risk, anomaly, and live plots.",
                "Let the operator type desired maxima and hard-stop levels. Crossing a hard stop Holds the mill and logs the pose.",
                "When the programme stops, emit a downloadable incident PDF: problems, measured parameters, measures to take.",
                "Never pretend the software Hold is a Category-0/1 e-stop, and never treat simulated MAE as a profilometer result.",
            ]
        )
    )
    s.append(H("2.3 What is deliberately not an objective", 2))
    s.append(
        P(
            "This project does not aim to replace a licensed operator, to auto-optimise G-code on a production "
            "cell, to certify ISO 13849 safety, or to publish XRD residual-stress maps. Those are different "
            "theses. The objective here is a working, honest, physics-informed early-warning monitor for "
            "Al 6061 end milling, with a site an examiner can operate."
        )
    )

    # 3 STAR
    s.append(H("3. Working principle in the STAR method"))
    s.append(
        P(
            "STAR is Situation, Task, Action, Result. It is the cleanest way to say how this site works without "
            "drowning the reader in file names first. The same four boxes are how an examiner, an operator, "
            "or a recruiter should remember the project."
        )
    )
    s.append(img("star.png"))
    s.append(P("Figure 2. STAR working principle.", "caption"))

    s.append(H("3.1 Situation", 2))
    s.append(
        P(
            "A 10 mm, 4-flute end mill is finishing Al 6061. Typical demo window: 3000 r/min, 0.12 mm/tooth, "
            "1.0 mm axial depth. The drawing asks for Ra ≤ 1.6 µm. The tool is allowed to live until a flank "
            "land of about 0.30 mm (ISO 8688-style demo limit). During the cut the spindle hears tooth-passing "
            "frequency, possible chatter, rising force as the land grows, more power, more heat. None of that "
            "is Ra. Ra is a stylus number after the pass. If chatter or a dull edge has already printed a "
            "cloudy lay, the plate is scrap. Shops today either (a) cut and then sample, or (b) change tools "
            "on a conservative schedule and waste life. Adaptive OEM cycles exist on high-end controls; they "
            "are not a B.Tech multimodal integrity model, and they do not write an incident sheet in the "
            "language of Ra, VB and physics residual."
        )
    )
    s.append(H("3.2 Task", 2))
    s.append(
        P(
            "Detect that the cut has left the stable neighbourhood, and warn that Ra or VB will cross the "
            "typed limit inside the next 10–60 s (operator-chosen horizon), early enough that a Hold still "
            "saves the face. Name the latent regime so the operator is not staring at twenty raw traces. "
            "Keep the mill pose on screen. If a typed hard stop is crossed, freeze XYZ, do not send the "
            "tool home, and explain the event in a PDF."
        )
    )
    s.append(H("3.3 Action", 2))
    s.append(
        P(
            "Action is a closed pipeline. A SensorSource (simulator, HTTP mill, or Arduino serial) yields a "
            "SensorFrame. extract_features builds a 16-D vector: vibration RMS, kurtosis, crest, skewness; "
            "force RMS and fluctuation; tooth-band and chatter-band FFT energy and their ratio; peak frequency "
            "and spectral entropy; temperature, power; the physics residual of P ≈ P_idle + F_c V_c; MRR and "
            "specific cutting energy. A Gaussian mixture with four full-covariance components, ordered by "
            "severity, assigns Regime A–D. Histogram gradient-boosting heads predict Ra, Rq, Rz, Rt, chatter "
            "frequency, VB, wear rate, temperature, remaining useful life, and 30 s risk. An Isolation Forest "
            "trained on the more-stable half of the cloud scores anomaly. A supervisor compares each armed "
            "quantity with the operator’s desired max and hard stop. Feed or rpm may be reduced once or twice "
            "as decision support; a hard stop calls halt_run, which Holds the mill, writes data/stop_log.jsonl, "
            "and builds the incident PDF."
        )
    )
    s.append(H("3.4 Result", 2))
    s.append(
        P(
            "The result the user sees is the site: STABLE → WATCH → SURFACE RISK → STOPPED; DRO coordinates; "
            "texture family; tool health; contribution bars; live plots; a gold download panel when the "
            "programme has stopped. The result the examiner can audit is a physics-simulated dataset of 2880 "
            "windows (12 speed/feed conditions × 240 windows), held-out MAE Ra ≈ 0.035 µm, VB ≈ 0.002 mm, "
            "chatter ≈ 1.1 Hz, RUL ≈ 0.4 s, and a risk AUC of 1.0 on that simulator — expected because labels "
            "and features share the same physics, and therefore not a laboratory claim. The result the shop "
            "can file is the stop PDF: problems, numbers, measures."
        )
    )

    # 4 architecture
    s.append(H("4. How the work is actually done (architecture of the site)"))
    s.append(img("pipeline.png"))
    s.append(P("Figure 3. End-to-end working chain from mill or twin to the operator.", "caption"))
    s.append(
        P(
            "The code is deliberately split so the mill can change without retraining the story of the ML. "
            "config.yaml holds the process (Al 6061, 10 mm, 4 flutes, 3000 r/min, 0.12 mm/tooth, Ra 1.6 µm) "
            "and the acquisition source (simulator | serial | http). dashboard/app.py is the site. "
            "src/pipeline.py is the one-function inference path: frame → features → MONITOR.forecast → "
            "MonitorResult. src/acquisition/ owns SensorFrame and three sources. src/processing/features.py "
            "is the 16-D contract. src/ml/model.py is AdvancedMonitor v3. src/control/supervisor.py is the "
            "limit logic. src/control/stop_log.py and stop_report.py are the incident trail. "
            "scripts/cnc_bridge.py is the local mill reverse proxy on port 8766. scripts/train_monitor.py "
            "rebuilds models/advanced_monitor.pkl and data/simulated_milling_dataset.csv."
        )
    )
    s.append(
        table(
            [
                ["Layer", "What it does on the site", "File / place"],
                ["Process card", "Material, tool, rpm, feed, depth, Ra spec", "config.yaml + sidebar"],
                ["Source", "Who produces the 0.25 s window", "simulator / serial / HTTP"],
                ["SensorFrame", "Raw traces + optional true Ra/VB labels", "src/acquisition/base.py"],
                ["Features", "16 numbers a model can eat", "src/processing/features.py"],
                ["Regimes", "Unsupervised A–D neighbourhood", "GaussianMixture in model.py"],
                ["Heads", "Ra family, VB, rate, T, RUL, 30 s risk", "HistGradientBoosting*"],
                ["Anomaly", "Is this window unlike stable cutting?", "IsolationForest"],
                ["Supervisor", "Desired max vs hard stop vs Hold", "src/control/supervisor.py"],
                ["Site", "Status, KPIs, plots, download", "dashboard/app.py"],
                ["Incident", "Why / what / what to do", "stop_report.py + JSONL"],
            ],
            [32 * mm, 78 * mm, 60 * mm],
        )
    )
    s.append(P("Table 1. Architecture mapped onto the running site.", "caption"))
    s.append(H("4.1 The SensorFrame contract — why the site can change mills", 2))
    s.append(
        P(
            "Every source must emit vibration[], force[], temperature, spindle power, current, cutting speed, "
            "feed per tooth, rpm, and sample rate. Optional true_* fields exist because a profilometer and a "
            "microscope do not stream. The live Ra on the dashboard is a prediction unless the operator types "
            "a measured value in “My measured values”. That is how the site stays honest when the mill is real "
            "and Ra is still a lab instrument."
        )
    )
    s.append(H("4.2 Three ways the site gets data", 2))
    s.append(
        bullets(
            [
                "<b>Simulator.</b> A physics-inspired twin: Taylor-type VB growth, first-order thermal lag, tooth and chatter tones in vibration and force, power from F_c V_c plus idle, Ra from feed, wear, chatter and heat. Time is compressed so a wear curve fits a short demo. This is the training generator and the default live twin.",
                "<b>HTTP / mill bridge.</b> Cycle start on the hooked mill starts the twin in lock-step with the programme duration parsed from G-code. DRO X/Y/Z are read from the bridge. Hold freezes interpolator pose. Stop on the mill is not treated as Hold — that was a hang we removed.",
                "<b>Serial Arduino.</b> firmware/arduino_daq.ino streams millis, vibration, current, temperature, optional force. Cheapest lab path. Same SensorFrame, same models.",
            ]
        )
    )

    # 5 site concepts
    s.append(H("5. Every concept the operator sees on the site"))
    s.append(
        P(
            "This chapter is a walk through the page, left to right, because “explain each and every concept "
            "of this site” is the request. Nothing on the screen is decoration; each widget is a calculated "
            "or commanded quantity with a mechanical meaning."
        )
    )
    s.append(H("5.1 Sidebar — Page and machine link", 2))
    s.append(
        bullets(
            [
                "<b>Refresh.</b> Streamlit rerun. The monitor is a live loop; refresh forces an immediate redraw.",
                "<b>Data source = simulator | serial | http.</b> Who owns SensorFrame. http is the other laptop’s mill URL; the dashboard does not embed the 3D mill, it consumes pose and cycle state.",
                "<b>Serial port / baud.</b> Arduino path (COM3, 115200 by default).",
                "<b>Online CNC URL.</b> ForgeMill origin. The working hooked mill is the local :8766 reverse proxy, not a telemetry API on vercel.app.",
            ]
        )
    )
    s.append(H("5.2 Sidebar — Manual process settings", 2))
    s.append(
        bullets(
            [
                "<b>Material.</b> Displayed as Al6061. Cutting constants in the twin are aluminium-like, not steel.",
                "<b>Tool diameter and flutes.</b> Enter V_c = π D N / 1000 and tooth frequency f_t = N z / 60.",
                "<b>Depth of cut.</b> Used in MRR with a demo radial width ≈ 0.4 D.",
                "<b>Spindle speed and feed per tooth.</b> The two commanded process levers. The supervisor may reduce them when a desired max is exceeded (capped, not a free adaptive controller).",
                "<b>Warning horizon.</b> 10–60 s. This is Δt in P(D_{t+Δt}=1). It is not a hard stop.",
            ]
        )
    )
    s.append(H("5.3 Sidebar — Limits you type", 2))
    s.append(
        P(
            "Each of Ra, VB, wear rate, temperature, vibration RMS and force RMS has two numbers: "
            "<b>desired max</b> (keep the cut at or below) and <b>hard stop</b> (Hold). Degradation probability "
            "is displayed only; it does not trip the machine. That is a design choice: probability is a "
            "warning, not a certified trip. The supervisor maps Ra / vibration / force overshoot to a feed "
            "reduction (chip load and chatter), and VB / wear rate / temperature overshoot to an rpm reduction "
            "(Taylor and thermal response)."
        )
    )
    s.append(H("5.4 Sidebar — My measured values", 2))
    s.append(
        P(
            "When a stylus or a microscope number exists, the operator can override the live twin for stop "
            "and display. That is the laboratory insertion point. Until then, predicted Ra is labelled as "
            "predicted."
        )
    )
    s.append(H("5.5 Start / Stop / Cycle start", 2))
    s.append(
        P(
            "Start run opens the chosen source. Start simulator forces the twin. Stop is an operator Halt: "
            "freeze pose, log, PDF. On the HTTP path the intended ritual is: open the hooked mill, press "
            "Cycle start there, leave the dashboard alone; the site follows the cycle and stops at M30 / Hold. "
            "That is how a two-laptop demo is supposed to look like one cell."
        )
    )
    s.append(H("5.6 Red alert and STOPPED banner", 2))
    s.append(
        P(
            "Before a hard stop, the site estimates seconds-to-limit from the recent slope of each armed "
            "series (eta_seconds). At ≥ 85 % of the stop level, or within about 8 s, a red alert lists which "
            "parameter is approaching. After halt, the banner shows STOPPED, the reason, the held XYZ, and "
            "a pointer to the incident PDF. The mill is not sent home. Origin (0,0,0) is ignored if a real "
            "pose was already frozen, so a DRO glitch cannot wipe the stop coordinate."
        )
    )
    s.append(H("5.7 CNC tool position", 2))
    s.append(
        P(
            "X, Y, Z from the ForgeMill DRO via the bridge. This is the geometric answer to “where did it "
            "stop?”. Combined with the G-code feature that was in the air, it tells the operator which boss "
            "or pocket to inspect."
        )
    )
    s.append(H("5.8 Stop-incident PDF download", 2))
    s.append(
        P(
            "Generated in halt_run. Contents: stop reason; diagnosis of which physics broke; DRO pose; the "
            "full measured/predicted table; operator limits versus values (OK / NEAR / TRIPPED); feature "
            "contributions; the monitor’s last recommendation; a list of measures (reduce feed, change tool, "
            "check coolant, compare chatter Hz with tooth-passing frequency, etc.); and the two standing "
            "disclaimers. A copy is stored under data/stop_reports/."
        )
    )
    s.append(H("5.9 Predicted surface texture family", 2))
    s.append(
        P(
            "Ra (arithmetic mean roughness) is the B.Tech integrity proxy. Rq is RMS height. Rz is a ten-point "
            "peak family. Rt is total peak-to-valley. Chatter frequency is the dominant unstable line. Form / "
            "waviness is extra geometry attributed to chatter (the site estimates it from how much Rz exceeds "
            "the quiet-Al ratio ~ 5.1 Ra, plus the chatter-to-tooth energy ratio). Why four roughness numbers? "
            "Because a face can pass Ra and still fail a peak spec: chatter raises Rz and Rt first. Showing "
            "only Ra would hide the mechanism."
        )
    )
    s.append(H("5.10 Machine status and regime", 2))
    s.append(
        P(
            "Status is a discrete shop word: STABLE, WATCH, SURFACE RISK, STOPPED, derived from probability, "
            "whether Ra already exceeds spec, regime id, and whether a hard stop has fired. Regime is the "
            "GMM neighbourhood: A stable cutting, B transitional, C unstable / chatter neighbourhood, D severe "
            "degradation, with a confidence equal to the mixture responsibility of the chosen component. "
            "Regimes are unlabeled structure, not ISO grades. They exist so the operator can see the cut "
            "walk across a map instead of across twenty plots."
        )
    )
    s.append(H("5.11 Probability, VB, wear rate, temperature, tool health", 2))
    s.append(
        P(
            "P(degradation in horizon) is the early-warning head. VB is predicted flank land. Wear rate is "
            "dVB/dt. Temperature is lagged bulk / sensor temperature, not shear-zone temperature. Tool health "
            "is 100 % at VB = 0 and 0 % at VB = 0.30 mm. Remaining useful life is time to that 0.30 mm land "
            "at the current rate. Wear stage is a shop word: initial / steady / accelerated, from VB and rate "
            "thresholds. Anomaly score maps Isolation Forest’s decision function to 0 (like the stable cloud) "
            "to 1 (odd). Decision support is a sentence, not a G-code rewrite."
        )
    )
    s.append(H("5.12 Plots and contributions", 2))
    s.append(
        P(
            "Time series of probability, Ra, vibration, force, power, temperature, VB, wear rate, health, "
            "feed and rpm make the drift visible. Contribution bars answer “why is risk high?”: they are "
            "permutation-importance weights times the live feature magnitude, renormalised, top eight. They "
            "are a local explanation, not SHAP values from a laboratory study. Waveforms of the current "
            "window show tooth-passing sinusoid versus chatter. Physics residual is printed in the footer "
            "strip: when power disagrees with F_c V_c, the sensing chain or the chip load is lying."
        )
    )
    s.append(H("5.13 The sixteen live features, one by one", 2))
    s.append(
        P(
            "The model never sees the raw 1250-sample traces. It sees sixteen numbers. Each is a mechanical "
            "or statistical statement about the last 0.25 s."
        )
    )
    s.append(
        table(
            [
                ["Feature", "Definition on the window", "What a rise usually means on this mill"],
                ["Vibration RMS", "sqrt(mean(a²))", "More energy in the cut: wear, chatter, or a loose fixture"],
                ["Kurtosis", "m4 / m2² of centred accel.", "Impacts, chipped tooth, intermittent BUE"],
                ["Crest factor", "peak / RMS", "A single bang in an otherwise quiet window"],
                ["Vibration skewness", "m3 / m2^(3/2)", "Asymmetric impacts; one-sided rubbing"],
                ["Force RMS", "sqrt(mean(F²))", "Chip load up, or the land is dull"],
                ["Force fluctuation", "std(F)", "Uneven chips, runout, chatter beating"],
                ["Chatter-band energy", "FFT power in 1.2–1.8 f_t", "Regenerative instability, not tooth passing"],
                ["Tooth-band energy", "FFT power in f_t ± 15 Hz", "Healthy mesh; a drop with chatter rise is a regime walk"],
                ["Chatter / tooth ratio", "chatter_e / tooth_e", "The one number that says “energy left the tooth line”"],
                ["Peak frequency", "argmax |FFT|", "Should sit on f_t in Regime A; walks off in C/D"],
                ["Spectral entropy", "−Σ p log p on power spectrum", "A clean line is low entropy; a chatter forest is high"],
                ["Temperature", "window scalar, lagged bulk", "Heat from V_c and wear; BUE risk on Al 6061"],
                ["Spindle power", "electrical / estimated watts", "Motor spend; rises with F_c V_c and dulling"],
                ["Physics residual", "|P − (180+F_c V_c)| / P", "Sensors disagree, or the cut is no longer a simple cut"],
                ["MRR", "a_p a_e v_f", "How much aluminium is leaving per minute"],
                ["Specific cutting energy u", "P / MRR", "Joules per mm³; dull tool and jam both inflate u"],
            ],
            [40 * mm, 55 * mm, 75 * mm],
        )
    )
    s.append(P("Table 1b. The 16-D vector as the operator should memorise it.", "caption"))

    # 6 mechanical theory
    s.append(H("6. Mechanical theory and how it is applied here"))
    s.append(
        P(
            "Every number on the site is a machining-mechanics quantity or a statistical shadow of one. "
            "This chapter writes the theory in the form the mill actually uses."
        )
    )
    s.append(H("6.1 Kinematics of the end mill", 2))
    s.append(
        P(
            "Cutting speed V_c (m/min) is the peripheral speed of the tooth:"
        )
    )
    s.append(P("V_c = π D N / 1000", "eq"))
    s.append(
        P(
            "with D in mm and N in r/min. At the default 10 mm and 3000 r/min, V_c ≈ 94 m/min, a typical "
            "HSS/carbide starting point for Al 6061. Feed per tooth f_z is the chip load. Table feed is"
        )
    )
    s.append(P("v_f = f_z · z · N", "eq"))
    s.append(
        P(
            "Tooth-passing frequency, the first line the accelerometer should see in stable cutting, is"
        )
    )
    s.append(P("f_t = N z / 60   (Hz)", "eq"))
    s.append(
        P(
            "At 3000 r/min and 4 flutes, f_t = 200 Hz. Harmonics 2 f_t, 3 f_t appear from non-perfect runout. "
            "The site’s chatter band is defined as roughly 1.2 f_t to 1.8 f_t, and the simulator plants a "
            "chatter tone at 1.37 f_t once wear and chip load have crossed a sigmoid. That is regenerative "
            "chatter in a demo costume: a frequency away from tooth passing, growing with wear fraction and "
            "feed. The live model does not solve a full delay-differential stability lobe; it measures whether "
            "energy has moved into that band. That is the B.Tech-correct application: detect the symptom with "
            "FFT bands, do not pretend a full Altintas lobe diagram from one accelerometer."
        )
    )
    s.append(H("6.2 Material removal and specific energy", 2))
    s.append(
        P(
            "Material removal rate for milling is"
        )
    )
    s.append(P("MRR = a_p · a_e · v_f", "eq"))
    s.append(
        P(
            "The demo takes a_p = 1.0 mm and a_e ≈ 0.4 D (a side/slot compromise so the number is not zero "
            "on a visual mill). Specific cutting energy is"
        )
    )
    s.append(P("u = P / MRR    (J/mm³ after unit conversion)", "eq"))
    s.append(
        P(
            "u rises when the tool dulls or when chips jam: more power for the same volume. That is why u is "
            "a feature. It is not a calorimeter; it is a process-efficiency flag."
        )
    )
    s.append(H("6.3 Force, power, and the physics residual", 2))
    s.append(
        P(
            "Instantaneous cutting power is F_c · V_c (force in N, V_c in m/s). Spindle electrical power is "
            "larger by idle (bearings, windage, inverter). The site uses a one-line constitutive check:"
        )
    )
    s.append(P("P ≈ 180 W + F_c V_c ,    residual = |P − P_pred| / max(P, 1)", "eq"))
    s.append(
        P(
            "180 W is an idle offset in the twin, not a measured no-load test of a particular Fanuc spindle. "
            "A large residual means the force channel and the power channel disagree. Causes: sensor scale, "
            "chip packing, a current clamp on the wrong phase, or a cut that is no longer orthogonal to the "
            "simple F_c V_c story. The residual is both an ML feature and a diagnostic on the incident PDF. "
            "That is what “physics-informed” means in this project: a soft constraint inside the feature "
            "vector, not a PINN trained on Navier–Stokes."
        )
    )
    s.append(H("6.4 Tool wear (Taylor-type) and RUL", 2))
    s.append(
        P(
            "Classical Taylor tool life is V T^n = C. Differentiating a wear land with speed and feed gives "
            "the simulator’s rate law:"
        )
    )
    s.append(P("dVB/dt ∝ (V_c)^2.1 · (f_z)^1.3 · (1 + 1.8·chatter + 0.7·VB/VB_lim)", "eq"))
    s.append(
        P(
            "Exponents are demo-scaled so a full land grows in about a minute on screen, not in 40 minutes of "
            "real Al 6061. The shape is the theory: faster speed, fatter chip, chatter, and already-worn land "
            "all accelerate wear. Remaining useful life in the twin is the linear projection"
        )
    )
    s.append(P("RUL = (0.30 mm − VB) / (dVB/dt)", "eq"))
    s.append(
        P(
            "The HGB RUL head learns that mapping from features, so on the live site RUL is a model output, "
            "not a direct division, unless a measured VB is typed. Tool health = 100 (1 − VB/0.30). Stage "
            "names follow the usual wear curve: running-in, steady, accelerated."
        )
    )
    s.append(H("6.5 Temperature as a lagged bulk", 2))
    s.append(
        P(
            "Shear-zone temperature is not measured. A thermocouple or an LM35 sees a lagged bulk. The twin "
            "uses a first-order lag toward a steady state that rises with cutting power, wear fraction and "
            "chatter, with a time constant of 2.4 s. That is why temperature on the site trails the cut and "
            "why the supervisor reduces rpm, not feed first, when temperature is the tripped channel: V_c "
            "is the main heat lever."
        )
    )
    s.append(H("6.6 Surface texture as the integrity proxy", 2))
    s.append(
        P(
            "ISO 4287 arithmetic roughness Ra is the mean absolute deviation of the primary profile. For this "
            "B.Tech, surface integrity is declared degraded when Ra ≥ 1.6 µm. That is a drawing spec, not "
            "white-layer metallurgy. The twin writes Ra as"
        )
    )
    s.append(P("Ra ≈ 0.18 + 2.8 f_z + 1.05 wear + 0.95 chatter + 0.014 max(T−38, 0) + noise", "eq"))
    s.append(
        P(
            "so feed, dulling, chatter and heat each leave a mark. Rq, Rz, Rt are then laid on typical milled-"
            "aluminium ratios (Rq ~ 1.25 Ra, Rz ~ 5.1 Ra) with extra peak height from chatter. We calculate "
            "the family because a single Ra can hide a chatter-spiked Rt. We do not calculate residual stress, "
            "microhardness, or white layer: those need XRD, nanoindentation, and etch, which are not on this "
            "site and must not be claimed."
        )
    )
    s.append(H("6.7 Vibration statistics — why RMS, kurtosis, crest, skewness", 2))
    s.append(
        P(
            "RMS is energy. Kurtosis is tailedness: a healthy tooth mesh is almost Gaussian; spalls, chips "
            "and impacts raise kurtosis. Crest factor is peak / RMS: a single bang in a quiet cut. Skewness "
            "catches asymmetric impacts. Peak-to-peak is the envelope the operator already knows from an "
            "oscilloscope. Spectral centroid and entropy say whether energy is a clean line (tooth passing) "
            "or a noisy, spreading chatter forest. These are condition-monitoring classics; they are here "
            "because they are the right statistics on a 0.25 s accelerometer window, not because a paper "
            "needed more acronyms."
        )
    )
    s.append(H("6.8 Regenerative chatter, applied without a lobe diagram", 2))
    s.append(
        P(
            "Regenerative chatter is a delay-differential instability: the tooth cuts a surface left by the "
            "previous tooth, so chip thickness carries a delayed copy of vibration. When the phase of that "
            "delay pumps energy into a structural mode, amplitude grows at a frequency that is not f_t. Full "
            "stability lobes need a tool-tip FRF (tap test). This project does not tap the mill. It applies "
            "the theory as a detection rule: look beside f_t, not on it. The band 1.2 f_t–1.8 f_t, the ratio "
            "of those energies, the walk of peak frequency, and the extra Rz/Rt above 5.1 Ra are the "
            "operational form of chatter theory on this site. When those rise, the supervisor’s feed lever "
            "is the machining-dynamics lever: reducing f_z reduces the regeneration gain."
        )
    )
    s.append(H("6.9 A worked window at the default process card", 2))
    s.append(
        P(
            "Default card: D = 10 mm, z = 4, N = 3000 r/min, f_z = 0.12 mm/tooth, a_p = 1.0 mm. Then "
            "V_c = π×10×3000/1000 ≈ 94.2 m/min = 1.57 m/s. Table feed v_f = 0.12×4×3000 = 1440 mm/min. "
            "Tooth frequency f_t = 3000×4/60 = 200 Hz; chatter tone in the twin sits near 274 Hz. "
            "MRR ≈ 1.0 × (0.4×10) × 1440 / 1000 = 5.76 cm³/min. If mean |F_c| is 280 N, cutting power "
            "≈ 280 × 1.57 ≈ 440 W, electrical P ≈ 620 W with idle. Specific energy u ≈ 620 / (5.76×1000/60) "
            "≈ 6.5 J/mm³, plausible for a small end mill in aluminium once wear has started. If VB = 0.12 mm "
            "and dVB/dt = 8 µm/s (demo-accelerated), RUL = (0.30−0.12)/0.008 ≈ 22.5 s of twin-time and "
            "health = 60 %. If predicted Ra is 1.35 µm with P(degrade in 30 s) = 0.62, the site shows WATCH "
            "or SURFACE RISK while the face is still legally under 1.6 µm — that is the early-warning "
            "effect in one window. If Ra then hits 1.62 µm, D = 1, degraded = true, and a typed hard stop "
            "Holds at the current XYZ and writes the PDF."
        )
    )

    # 7 coupling
    s.append(H("7. How the parameters are related to one another"))
    s.append(img("coupling.png"))
    s.append(P("Figure 4. Coupling map used by the site. Arrows are causal in the twin and in shop practice.", "caption"))
    s.append(
        P(
            "Nothing is independent. Raising N raises V_c, tooth frequency, heat, Taylor wear, and the "
            "location of the chatter band. Raising f_z raises chip thickness, F_c, power, MRR, and Ra, and "
            "it makes regenerative chatter easier. Wear raises F_c and heat, which raise Ra, which raises "
            "risk. Chatter raises vibration RMS, chatter-band energy, Rz/Rt, form error, and the physics "
            "residual if force and power stop matching. Anomalous windows are those that leave the stable "
            "GMM blob: usually C and D. The supervisor’s two levers — reduce feed, reduce rpm — follow this "
            "map: feed for force/vibration/Ra, rpm for wear/temperature."
        )
    )
    s.append(
        table(
            [
                ["If this rises", "What else usually rises", "What the site does with it"],
                ["Feed/tooth f_z", "F_c, MRR, Ra, chatter risk", "Desired-max → reduce feed 10 %"],
                ["Spindle N", "V_c, heat, dVB/dt, f_t", "Desired-max on T/VB → reduce rpm 6 %"],
                ["Flank wear VB", "Force, power, Ra, heat, lower RUL", "Health %, stage, hard stop 0.30 mm"],
                ["Chatter energy", "RMS, Rz, Rt, form, residual", "Regime C/D, contribution bar, Hold if vib trips"],
                ["Temperature", "Ra (thermal softening / BUE on Al)", "Hard stop; rpm lever"],
                ["Physics residual", "Distrust of P or F_c", "Feature + PDF diagnostic, not a roughness number"],
                ["P(degrade in 30 s)", "Watch / SURFACE RISK status", "Display only; does not Hold"],
                ["Ra", "Integrity event D=1 at spec", "Proxy for SI; hard stop default 1.6 µm"],
            ],
            [38 * mm, 62 * mm, 70 * mm],
        )
    )
    s.append(P("Table 2. Directed relationships the operator can actually use.", "caption"))
    s.append(
        P(
            "A closed loop the examiner should be able to say out loud: dull edge → higher F_c → higher P "
            "and T → faster dVB/dt → still duller edge, while f_z prints a taller Ra. Chatter is the "
            "instability branch of the same loop: once energy sits between 1.2 f_t and 1.8 f_t, Rz/Rt and "
            "form error run ahead of Ra, which is why the texture family exists. The physics residual is the "
            "loop’s checksum: if P and F_c V_c diverge, the loop is being observed through a broken instrument "
            "or a jammed chip, and the model’s Ra cannot be trusted as blindly."
        )
    )

    # 8 calculations
    s.append(H("8. What we calculate, why these quantities only, and what effects they create"))
    s.append(
        P(
            "A project can compute anything. This one computes a closed set: enough to warn on surface "
            "integrity and tool life, not so much that the site becomes a finite-element thesis. The test "
            "for each quantity is: does it have a mechanical definition, a sensor path, an effect on scrap "
            "or tool cost, and a place on the operator screen?"
        )
    )
    s.append(
        table(
            [
                ["Quantity", "How it is calculated", "Effect / impact", "Why this and not something else"],
                [
                    "16-D feature vector",
                    "Time stats + Hanning FFT bands + P residual + MRR, u",
                    "Turns a 1250-sample window into a model row",
                    "Raw waveforms are too long for tabular HGB; spectra without bands hide tooth vs chatter",
                ],
                [
                    "Regimes A–D",
                    "4-component GMM on scaled X; components ordered by RMS+chatter",
                    "A shop language for “where is this cut?”",
                    "Not k-means (no density), not a VAE (too heavy for 0.25 s laptop loop)",
                ],
                [
                    "Ra, Rq, Rz, Rt",
                    "Separate HGB regressors",
                    "Integrity proxy + peak family so chatter cannot hide",
                    "Not residual stress (no XRD); not waviness from a 50 mm traverse",
                ],
                [
                    "Chatter Hz, form error",
                    "HGB + (Rz − 5.1 Ra) and chatter/tooth ratio",
                    "Tells the operator the mechanism, not only the height",
                    "Not a full lobe diagram (needs TAP tests)",
                ],
                [
                    "VB, wear rate, RUL, health",
                    "HGB + Taylor-type labels in the twin",
                    "Tool-change timing; 0.30 mm demo life",
                    "Not crater wear (needs a different view of the rake)",
                ],
                [
                    "Temperature (pred. + sensed)",
                    "Lagged bulk in twin; HGB head as cross-check",
                    "Thermal lever for rpm",
                    "Not shear-zone pyrometry",
                ],
                [
                    "30 s risk P",
                    "HGB classifier on future D = (Ra≥spec or VB≥0.30)",
                    "Early warning; status WATCH / SURFACE RISK",
                    "Not a hard stop (by design)",
                ],
                [
                    "Anomaly",
                    "Isolation Forest on stable half",
                    "Catches “never seen this window”",
                    "Complements GMM: novelty vs mixture responsibility",
                ],
                [
                    "Contributions",
                    "Permutation importance × |x_i|",
                    "Why the alarm fired",
                    "Inspectable; not a second black box",
                ],
                [
                    "ETA to limit",
                    "Slope of last ~10 points",
                    "Red-alert countdown",
                    "Simple, shop-readable, no extra model",
                ],
                [
                    "Hold pose + PDF",
                    "Bridge XYZ + diagnose()",
                    "Traceable incident; training artefact",
                    "Not an e-stop certificate",
                ],
            ],
            [32 * mm, 46 * mm, 46 * mm, 46 * mm],
        )
    )
    s.append(P("Table 3. The calculated set, the effect of each, and the reason it is in the set.", "caption"))
    s.append(H("8.1 Effects on the cut, the tool, the plate, and the operator", 2))
    s.append(
        bullets(
            [
                "<b>On the cut.</b> Feed and rpm overrides, when they fire, lower chip load or V_c. That reduces force, heat and Ra at the cost of cycle time. They are capped (two overrides) so the site cannot hunt.",
                "<b>On the tool.</b> Health %, RUL and VB give a reason to change the mill before a land of 0.30 mm polishes the face badly. Wear rate is the derivative: a healthy VB with a high rate is a tool that will not last the next pocket.",
                "<b>On the plate.</b> The integrity event is Ra. Saving a plate means Holding while Ra is still legal but P(degrade) and regime C are already up. That is the whole early-warning effect.",
                "<b>On the operator.</b> One screen instead of a scope, a power meter, a pyrometer and a notebook. After a stop, a PDF that can be stapled to a job card.",
                "<b>On the examiner.</b> A chain from mechanics → features → models → widgets that can be interrogated. Simulated MAE is reported as simulated.",
            ]
        )
    )
    s.append(H("8.2 Why we are not calculating “everything”", 2))
    s.append(
        P(
            "We do not calculate residual stress, because there is no XRD coupon chain on this site. We do "
            "not calculate chatter lobes, because there is no tap-test FRF. We do not calculate tool-tip "
            "temperature, because there is no two-colour pyrometer. We do not run an LSTM on raw 5 kHz "
            "traces, because a 0.25 s laptop loop with inspectable tabular features is the right B.Tech "
            "estimator and because permutation importance would disappear inside a sequence model we cannot "
            "explain on a shop floor. We do not auto-rewrite G-code. Those omissions are the project’s "
            "discipline, not its weakness. The impact of calculating only this set is that every output "
            "has a sensor, a formula, a widget, and a sentence in the stop PDF."
        )
    )

    # 9 ML
    s.append(H("9. Complete machine-learning pipeline and algorithms"))
    s.append(H("9.1 Data that trains the models", 2))
    s.append(
        P(
            "AdvancedMonitor.train() runs 12 physics-simulated conditions (rpm in {2400, 2700, 3000, 3300, "
            "3600}, feed in {0.08 … 0.18} mm/tooth, fixed 1.0 mm depth, Al 6061, 10 mm 4-flute). Each run "
            "yields 240 windows of 0.25 s at 2 kHz (training) — 2880 rows. Labels come from the twin: Ra, "
            "Rq, Rz, Rt, chatter Hz, VB, wear rate, RUL, and a future bit D = 1 if within 30 s (120 windows "
            "ahead, clipped at the end) Ra ≥ 1.6 µm or VB ≥ 0.30 mm. The CSV is written to "
            "data/simulated_milling_dataset.csv. A 80/20 split with random_state=7 is the only test. "
            "These numbers are not a public PHM archive and not a laboratory campaign."
        )
    )
    s.append(H("9.2 Pipeline, step by step", 2))
    s.append(
        bullets(
            [
                "<b>Window.</b> 0.25 s of vib and force (live dashboard 5 kHz; training 2 kHz).",
                "<b>Feature extraction.</b> Mean-centre, Hanning, rFFT. Kurtosis, crest, skewness, RMS, peak-to-peak. Tooth band ±15 Hz. Chatter band 1.2–1.8 f_t. Entropy of the power spectrum. Residual, MRR, u. Output: 16-D float32 vector. Names are listed in FEATURE_NAMES in model.py.",
                "<b>Scale for GMM.</b> StandardScaler, then GaussianMixture(n_components=4, covariance_type=full, n_init=3). Components are sorted by mean(vib RMS + 3 × chatter-band) so id 0 is the calmest blob. Live assignment: argmax of responsibilities, mapped through that order.",
                "<b>Scale for heads.</b> Each head is a sklearn Pipeline(StandardScaler → HistGradientBoosting*).",
                "<b>Eleven supervised heads.</b> Nine regressors (Ra, Rq, Rz, Rt, chatter Hz, VB, wear rate, temperature, RUL) and one classifier (risk). Shared HGB hyperparameters: max_depth=4, max_iter=140, learning_rate=0.08, l2_regularization=0.1, random_state=7. Depth 4 is a regulariser: the twin is smooth; a deep tree would memorise noise and look better on the simulator than it deserves.",
                "<b>Isolation Forest.</b> 160 trees, contamination=0.08, fit on windows with D=0. Live score: clip(0.5 − decision_function, 0, 1).",
                "<b>Permutation importance.</b> On the risk head, 6 repeats, ROC-AUC, used as contribution weights.",
                "<b>Clip and shop language.</b> Predictions are clipped to physical ranges. Recommendation text is thresholded on probability and regime. Wear stage from VB and rate.",
                "<b>Persist.</b> pickle models/advanced_monitor.pkl, version 3 (must contain rq heads).",
                "<b>Live infer.</b> pipeline.infer: extract_features → MONITOR.forecast → degraded if Ra≥spec or VB≥0.30.",
                "<b>Supervisor.</b> Not ML. Thresholds the operator typed. May reduce feed/rpm or Halt.",
                "<b>Incident PDF.</b> Not ML. Rule-based diagnose() on the stop record.",
            ]
        )
    )
    s.append(H("9.3 Algorithms used, and why each one", 2))
    s.append(
        table(
            [
                ["Algorithm", "Role", "Why this algorithm here"],
                [
                    "Gaussian mixture (full covariance, 4 components)",
                    "Latent regime discovery",
                    "Unlabeled density on a small tabular vector. Soft responsibilities become confidence. Four components match A–D shop language. HDBSCAN would not give a probability on a new point as cleanly; a VAE is unnecessary at 16-D.",
                ],
                [
                    "StandardScaler",
                    "Equalise units before GMM and HGB",
                    "RMS in g and power in W cannot share a Euclidean mixture without scaling.",
                ],
                [
                    "HistGradientBoostingRegressor",
                    "Ra family, VB, rate, T, RUL, chatter Hz",
                    "Fast on CPU, handles collinear process features, shallow trees stay inspectable. Not LSTM: 0.25 s windows, laptop training, permutation importance.",
                ],
                [
                    "HistGradientBoostingClassifier",
                    "P(D=1 inside horizon)",
                    "Same reasons; predict_proba is the early-warning number.",
                ],
                [
                    "Isolation Forest",
                    "Novelty / anomaly",
                    "Unsupervised complement to GMM. GMM says which blob; IF says “not like the stable half”.",
                ],
                [
                    "Permutation importance",
                    "Global feature weights for contributions",
                    "Model-agnostic, matches the risk head the operator actually sees.",
                ],
                [
                    "Train/test split 80/20",
                    "Simulated MAE / AUC",
                    "Honesty box: report a number, label it simulated. AUC=1.0 is expected on this twin.",
                ],
                [
                    "Hanning + rFFT band energy",
                    "Tooth vs chatter",
                    "Classical machining-dynamics feature. Cheaper and more interpretable than a learned spectrogram CNN.",
                ],
                [
                    "Soft physics residual",
                    "P vs F_c V_c",
                    "The “informed” in physics-informed. Not a PINN.",
                ],
                [
                    "Linear ETA",
                    "Seconds to hard stop",
                    "Operators understand slope. A second ML head would not add trust.",
                ],
                [
                    "Rule supervisor",
                    "Feed / rpm / Hold",
                    "Safety-shaped logic must not be a neural net. Typed limits, typed actions.",
                ],
                [
                    "Logistic stand-in (predictor.py)",
                    "Legacy closed-form warning",
                    "Still in the repo as a transparent formula; the live site uses AdvancedMonitor HGB.",
                ],
            ],
            [42 * mm, 38 * mm, 90 * mm],
        )
    )
    s.append(P("Table 4. Algorithm inventory of the running site.", "caption"))
    s.append(H("9.4 Held-out simulated metrics (not lab)", 2))
    s.append(
        P(
            "On 576 held-out simulated windows: MAE Ra 0.035 µm, Rq 0.047 µm, Rz 0.19 µm, Rt 0.24 µm, "
            "chatter 1.10 Hz, VB 0.002 mm, wear rate 0.36 µm/s, RUL 0.42 s; risk AUC 1.00. Read these as "
            "“the heads recovered the twin”, not “the heads recovered a Mitutoyo and a toolmaker’s microscope”. "
            "When a lab campaign exists, the same pipeline is retrained on the same CSV schema with measured "
            "label_ra_um and label_vb_mm. That swap is the point of the SensorFrame and the CSV contract."
        )
    )
    s.append(H("9.5 What “physics-informed multimodal learning” means in one paragraph", 2))
    s.append(
        P(
            "<b>Multimodal:</b> vibration, force, power, temperature, and commanded kinematics in one window. "
            "<b>Learning:</b> GMM structure + HGB function approximation + Isolation Forest novelty. "
            "<b>Physics-informed:</b> features that are mechanics (f_t bands, MRR, u, P−F_c V_c), labels that "
            "are mechanics (Ra, VB, Taylor-type rate), and a supervisor whose levers (feed, rpm) are the "
            "levers machining theory says to touch. It is not a PINN, not a digital twin of the whole machine "
            "tool, and not a claim that the loss function contains the wave equation."
        )
    )
    s.append(H("9.6 How the three core algorithms work (B.Tech level)", 2))
    s.append(
        P(
            "<b>Gaussian mixture.</b> Assume the 16-D cloud is a sum of four Gaussians. Expectation–Maximisation "
            "alternates: (E) compute the responsibility of each component for each window; (M) update means, "
            "full covariance matrices, and mixture weights. After fit, a new window gets four probabilities "
            "that sum to one. We sort components by how “violent” their mean is (RMS + chatter) so the "
            "calmest Gaussian is always Regime A. Confidence on the site is the winning responsibility. "
            "That is unsupervised latent-regime discovery: nobody labelled A–D in the CSV."
        )
    )
    s.append(
        P(
            "<b>Histogram gradient boosting.</b> A forest of shallow trees (depth 4) is grown sequentially. "
            "Each tree fits the residual of the previous ensemble. Inputs are first binned (the “histogram”), "
            "which makes splits fast on 2304 training rows. A regressor head outputs a real number (Ra in µm, "
            "VB in mm). The classifier head outputs a logit that softmax/sigmoid turns into P(D=1). "
            "L2 regularisation 0.1 and learning rate 0.08 stop the ensemble from memorising the twin’s noise. "
            "We use HGB rather than a deep net because the features are already mechanics, the loop is 0.25 s "
            "on a laptop, and permutation importance needs a model we can shuffle."
        )
    )
    s.append(
        P(
            "<b>Isolation Forest.</b> Random partitions isolate a point; odd points need fewer cuts. The "
            "decision function is high for normal, low for odd. We fit only on windows that did not degrade "
            "inside the horizon, so “normal” means “looks like stable/early cutting”, not “looks like the "
            "whole dataset including failures”. The site maps that to 0–1. GMM and IF answer different "
            "questions: GMM — which neighbourhood?; IF — is this neighbourhood even familiar?"
        )
    )
    s.append(
        P(
            "<b>Permutation importance.</b> Shuffle one feature on the test set, measure the drop in ROC-AUC "
            "of the risk head, repeat six times, clip negatives to zero. That weight times the live |x_i| "
            "is the contribution bar. If chatter-band energy is both important globally and large right now, "
            "it dominates the bar — which is what the operator needs to see, not a research SHAP beeswarm."
        )
    )

    # 10 what we built
    s.append(H("10. What has been built"))
    s.append(
        bullets(
            [
                "A running Streamlit monitor (dashboard/app.py) with process card, sources, limits, manual lab override, live KPIs, plots, contributions, DRO XYZ, and stop PDF download.",
                "A physics-inspired milling twin with Taylor-type wear, thermal lag, tooth/chatter synthesis, Ra family, MRR and RUL (simulator.py).",
                "A 16-D feature contract including physics residual (features.py).",
                "AdvancedMonitor v3: GMM, 11 HGB heads, Isolation Forest, permutation importance, pickle + CSV + metrics (model.py, train_monitor.py).",
                "A typed-limit supervisor with feed/rpm suggestions and hard-stop Halt (supervisor.py).",
                "Mill reverse proxy and cycle-follow (cnc_bridge.py, cycle_signal, gcode_playback) so Cycle start on the hooked mill starts the twin and M30/Hold stops it.",
                "Stop log JSONL and a full incident PDF (stop_log.py, stop_report.py) covering diagnosis, measurements, limits, contributions and measures.",
                "Arduino firmware path for a future bench DAQ.",
                "B.Tech report and 20-slide IIT Patna talk artefacts in docs/, with the same honesty rules as this document.",
                "config.yaml defaults for Al 6061, 10 mm, 4 flutes, 3000 r/min, 0.12 mm/tooth, Ra 1.6 µm, HTTP source.",
            ]
        )
    )
    s.append(
        P(
            "What has not been built, on purpose: a certified e-stop, an XRD residual-stress module, a "
            "production MTConnect historian, an LSTM on raw traces, and a laboratory MAE table. Those are "
            "the next campaign, not missing decorations on this site."
        )
    )

    # 11 market
    s.append(H("11. Market effect and why this class of system can change shop-floor quality"))
    s.append(
        P(
            "This chapter is written as industrial consequence, not as a start-up pitch. A B.Tech monitor "
            "running on a laptop next to a teaching mill does not “own” a market. The class of system it "
            "belongs to — in-process multimodal integrity warning with inspectable physics — is what can "
            "move money if it is later validated on coupons and then on a cell."
        )
    )
    s.append(H("11.1 Where the money currently leaks", 2))
    s.append(
        P(
            "CNC milling of aluminium is a backbone process in automotive fixtures, aerospace brackets, "
            "electronics heat-sinks, and job-shop plates. Scrap is rarely the billet cost; it is the hours "
            "already spent, the downstream assembly that now has no part, and the rush overtime to recut. "
            "Two leak paths dominate finishing: (1) a face that fails Ra or a peak spec after the stylus "
            "is dragged, and (2) a tool that either dies in the cut (marks the next parts) or is thrown away "
            "with half its land unused. Classical SPC samples too late. Classical tool-life tables are "
            "conservative because they cannot see this morning’s chatter or this batch’s coolant. High-end "
            "OEM adaptive control (constant-power, chatter-avoidance options on some Heidenhain/Siemens/"
            "Fanuc cycles) already exists in the premium tier; it is closed, expensive, and rarely explains "
            "itself as Ra, VB and a physics residual a mechanical student can defend. India’s installed base "
            "is mostly VMCs without those options. A laptop, an accelerometer and a current clamp is a "
            "different cost structure from a control-option licence. That is the market gap this architecture "
            "is aimed at — after, not before, a laboratory calibration."
        )
    )
    s.append(H("11.2 What a site like this changes if it is believed", 2))
    s.append(
        bullets(
            [
                "<b>Quality moves from after to during.</b> The integrity event is predicted, not discovered on a CMM the next shift. That is a different factory clock.",
                "<b>Tool change becomes a condition decision.</b> RUL and wear rate replace “change every 40 minutes because last month one tool died”. Inserts and end mills are a visible consumable line; even a 10–20 % life recovery is plant money, but that recovery is a claim we do not make until a lab campaign measures it.",
                "<b>Scrap becomes an incident with a pose.</b> XYZ + PDF + contributions is a quality record, not a shrug. Automotive IATF and aerospace AS9100 live on records.",
                "<b>Skill is amplified, not replaced.</b> The operator still owns Hold and e-stop. The site speaks shop language (regime, health %, measures). That is how a small Indian job shop can use it without a data-science cell.",
                "<b>Sensors stay cheap.</b> Accelerometer, current clamp, optional thermocouple — Arduino-class. The market that matters in India is not only a ₹4 crore machining centre; it is also a VMC that cannot buy Siemens Analyze MyWorkpiece.",
            ]
        )
    )
    s.append(H("11.3 Why this can be called a “revolution” only in a careful sense", 2))
    s.append(
        P(
            "A revolution in this market is not a new chatbot. It is a change in <i>when</i> a factory knows "
            "a surface is dying. For a century, roughness has been a post-process number. In-process "
            "metrology (laser, white-light, on-machine probes) exists but is slow or fragile in flood coolant. "
            "Using the energy the cut already radiates — vibration, force, power — as a proxy, constrained "
            "by P ≈ F_c V_c, and converting that into a 30 s warning plus a Hold at a known XYZ, is a "
            "change of kind if and only if the proxy is calibrated on real Ra. That “if” is why this report "
            "does not say the revolution has already happened. It says the architecture of the revolution "
            "is visible on this site: multimodal, physics-checked, regime-named, horizon-warned, limit-typed, "
            "incident-written."
        )
    )
    s.append(
        P(
            "If a later laboratory campaign shows that P(degrade in 30 s) rises while stylus Ra is still "
            "legal, and that Holding then saves faces that would have failed, then the effect on the market "
            "is: fewer recuts, fewer surprise tool breaks, a quality record that a customer can audit, and "
            "a software layer that can sit on mills that will never see a full OEM adaptive package. That "
            "is a disruptive pattern (cheap sensors + inspectable ML + shop UI) against a premium pattern "
            "(closed CNC option). Calling it a revolution is fair as a direction; calling this B.Tech a "
            "shipped product is not."
        )
    )
    s.append(H("11.4 Who would feel it", 2))
    s.append(
        table(
            [
                ["Actor", "Effect if the method is lab-true", "What this site already demonstrates"],
                ["Job-shop owner", "Less scrap on Al finishing; tool stock used harder", "A laptop UI and a PDF job-card trail"],
                ["Operator", "A warning before the face clouds; XYZ of the event", "Regimes, countdown, Hold pose"],
                ["Quality / IATF", "In-process evidence pack", "JSONL + incident PDF fields"],
                ["Tooling vendor", "Wear curves tied to this cell’s rpm/feed, not a catalogue", "VB, rate, RUL heads"],
                ["OEM CNC vendor", "Pressure to explain adaptive options in SI language", "Ra family + residual, not only amperes"],
                ["Teaching lab (IITP)", "A mill experiment that is not only a surface-finish lab after the cut", "The site as it stands"],
            ],
            [38 * mm, 66 * mm, 66 * mm],
        )
    )
    s.append(P("Table 5. Market / institutional impact map — directional, not a revenue model.", "caption"))
    s.append(H("11.5 What would block the impact", 2))
    s.append(
        P(
            "If the model stays on the twin, the market effect is zero. If Hold is confused with e-stop, a "
            "safety auditor correctly kills the project. If Ra is sold as residual stress, a metallurgy "
            "examiner correctly kills the claim. If the mill link is only a Vercel animation without DRO, "
            "the shop cannot find the feature that failed. Those blockers are why the site is built the way "
            "it is: honesty banners, hooked mill, pose freeze, PDF, SensorFrame ready for Arduino."
        )
    )

    # 12 limits
    s.append(H("12. Limits, honesty, and the next laboratory step"))
    s.append(
        bullets(
            [
                "Training and live demo labels are physics-simulated. MAE and AUC in data/training_metrics.txt are not profilometer / microscope results.",
                "Software Hold is not ISO 13849 Category-0/1. A licensed operator owns the real mushroom button.",
                "The academic supervisor is not a certified CNC e-stop authority.",
                "D = 1 at Ra spec is a B.Tech surface-integrity proxy, not a full SI suite (stress, hardness, microstructure).",
                "Idle power 180 W, a_e ≈ 0.4 D, chatter at 1.37 f_t, and Taylor exponents are demo constitutive choices.",
                "Risk does not trip the mill. That is intentional.",
                "AUC = 1.0 on the twin is a warning about the twin, not a trophy.",
            ]
        )
    )
    s.append(
        P(
            "The laboratory step is well-defined: instrument a vice with an accelerometer, a spindle with a "
            "current clamp, log rpm/feed from the control or by hand, cut Al 6061 coupons at the 12-condition "
            "grid, measure Ra on a stylus, photograph VB, replace label_* columns, retrain, and only then "
            "quote MAE as a thesis result. The site does not need to be redesigned for that step. That is "
            "the point of the contract."
        )
    )

    # 13 close
    s.append(H("13. Closing statement"))
    s.append(
        P(
            "The site is a closed argument. Situation: aluminium is milled, Ra is known too late. Task: "
            "name the regime and warn before spec. Action: a SensorFrame, a 16-D mechanics-aware vector, "
            "a Gaussian mixture, histogram gradient boosting, an Isolation Forest, a typed supervisor, a "
            "Hold that keeps XYZ, and a PDF that tells the truth about the stop. Result: a shop-floor page "
            "an operator can run and an examiner can interrogate. The calculations are the ones machining "
            "theory says control scrap and tool life — V_c, f_z, f_t, MRR, u, F_c, P, residual, VB, dVB/dt, "
            "RUL, T, Ra–Rt, chatter. Their effects are coupled, which is why the supervisor has two levers "
            "and the texture family has four heights. Their impact, if later measured on metal, is to move "
            "quality leftward in time. That is the only revolution this project claims a right to point at: "
            "not a market already overturned, but a mill that can speak before it spoils the face."
        )
    )
    s.append(Spacer(1, 8 * mm))
    s.append(
        P(
            "Rajshekhar  ·  Piyush Jatoliya  ·  Supervisor: Dr. Mahavir Singh  ·  "
            "Department of Mechanical Engineering  ·  Indian Institute of Technology Patna",
            "cover_sub",
        )
    )
    return s


def main():
    make_figures()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="Concept and working report — Machining Integrity Monitor",
        author="Rajshekhar, Piyush Jatoliya",
        subject="IIT Patna B.Tech project concept report",
    )
    doc.build(story(), onFirstPage=header_footer, onLaterPages=header_footer)
    DOWNLOADS.write_bytes(OUT.read_bytes())
    print(OUT)
    print(DOWNLOADS)
    print("pages_est_bytes", OUT.stat().st_size)


if __name__ == "__main__":
    main()
