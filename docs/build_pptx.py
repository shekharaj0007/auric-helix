"""IIT Patna 10-minute BTP talk — visual slides + speaker notes + Part II."""
from __future__ import annotations

from pathlib import Path

import qrcode
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
ASSETS = ROOT / "slides_assets"
LOGO = ROOT / "template_assets" / "image1.png"
OUT = ROOT / "BTP_IITP_20slide_Presentation.pptx"

SITE = "https://temporary-speedy-azure-d4iojfc.vercel.app"
ASK = (
    "mailto:?subject=Question%20-%20IIT%20Patna%20BTP%20Machining%20Integrity%20Monitor"
    "&body=Your%20question%3A%0A%0A"
)

NAVY = RGBColor(0x0B, 0x1F, 0x3A)
NAVY2 = RGBColor(0x14, 0x3D, 0x66)
GOLD = RGBColor(0xC9, 0xA2, 0x27)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
OFF = RGBColor(0xF4, 0xF7, 0xFA)
INK = RGBColor(0x1C, 0x24, 0x2E)
MUTED = RGBColor(0x5A, 0x66, 0x73)
GREEN = RGBColor(0x1F, 0x6B, 0x4A)
RED = RGBColor(0x9B, 0x2C, 0x2C)
LINE = RGBColor(0xD5, 0xDC, 0xE4)

W = Inches(13.333)
H = Inches(7.5)


def fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def rect(slide, l, t, w, h, color, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    fill(s, color)
    if line:
        s.line.color.rgb = line
        s.line.width = Pt(1.15)
    return s


def rrect(slide, l, t, w, h, color, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    fill(s, color)
    if line:
        s.line.color.rgb = line
        s.line.width = Pt(1.2)
    try:
        s.adjustments[0] = 0.07
    except Exception:
        pass
    return s


def tb(slide, l, t, w, h, text, *, size=18, bold=False, color=INK, align="left", italic=False):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[align]
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = "Calibri"
    return box


def notes(slide, text):
    ns = slide.notes_slide
    ns.notes_text_frame.text = text.strip()


def header(slide, kicker, title, n, total=20):
    rect(slide, 0, 0, W, Inches(1.02), NAVY)
    rect(slide, 0, Inches(1.02), W, Inches(0.07), GOLD)
    if LOGO.exists():
        slide.shapes.add_picture(str(LOGO), Inches(0.22), Inches(0.16), Inches(0.70), Inches(0.70))
    tb(slide, Inches(1.08), Inches(0.12), Inches(10.2), Inches(0.28), kicker.upper(), size=11, bold=True, color=GOLD)
    tb(slide, Inches(1.08), Inches(0.40), Inches(10.4), Inches(0.52), title, size=24, bold=True, color=WHITE)
    tb(slide, Inches(11.65), Inches(0.34), Inches(1.45), Inches(0.36), f"{n:02d} / {total:02d}", size=12, color=GOLD, align="right")
    rect(slide, 0, Inches(7.18), W, Inches(0.32), NAVY)
    tb(slide, Inches(0.28), Inches(7.20), Inches(9.6), Inches(0.26),
       "Department of Mechanical Engineering  ·  IIT Patna  ·  B.Tech Project  ·  Theory + method + live site",
       size=11, color=WHITE)
    tb(slide, Inches(10.2), Inches(7.20), Inches(2.85), Inches(0.26), "Dr. Mahavir Singh", size=11, color=GOLD, align="right")


def speak_card(slide, l, t, w, h, title, body, accent=GOLD):
    rrect(slide, l, t, w, h, WHITE, line=LINE)
    rect(slide, l, t, Inches(0.09), h, accent)
    tb(slide, l + Inches(0.22), t + Inches(0.10), w - Inches(0.34), Inches(0.34), title, size=15, bold=True, color=NAVY)
    tb(slide, l + Inches(0.22), t + Inches(0.46), w - Inches(0.34), h - Inches(0.56), body, size=15, color=INK)


def blank():
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, W, H, OFF)
    return s


def make_qrs():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name, url in (("qr_site.png", SITE), ("qr_ask.png", ASK)):
        qr = qrcode.QRCode(version=2, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        qr.make_image(fill_color="#0B1F3A", back_color="white").save(ASSETS / name)


def pic(slide, path, l, t, w, h=None):
    p = Path(path)
    if not p.exists():
        return
    if h:
        slide.shapes.add_picture(str(p), l, t, w, h)
    else:
        slide.shapes.add_picture(str(p), l, t, w)


# ---------------------------------------------------------------------------
# Theory slides — speakable text, not only diagrams
# ---------------------------------------------------------------------------

def t_about():
    s = blank()
    header(s, "Theory  ·  speak this", "What is this project mainly about?", 2)
    rrect(s, Inches(0.35), Inches(1.18), Inches(12.6), Inches(1.35), NAVY)
    tb(s, Inches(0.55), Inches(1.32), Inches(12.2), Inches(1.10),
       "This project is an early-warning system for surface degradation during CNC end milling of Aluminium 6061. It does not wait for a profilometer after the pass. It watches the cut while it happens.",
       size=18, bold=True, color=WHITE)
    speak_card(s, Inches(0.35), Inches(2.70), Inches(6.25), Inches(2.05), "The question the system answers",
               "Is the machining process still healthy, and is the surface likely to become unacceptable in the near future? That is the whole project in one sentence.")
    speak_card(s, Inches(6.80), Inches(2.70), Inches(6.15), Inches(2.05), "What “surface integrity” means here",
               "For this B.Tech, surface integrity is proxied by Ra — arithmetic mean roughness. Residual stress and XRD are not claimed. If Ra exceeds 1.6 µm, the surface is treated as degraded.")
    speak_card(s, Inches(0.35), Inches(4.90), Inches(6.25), Inches(2.05), "What we built",
               "A runnable monitor: multimodal signals → physics residual → GMM regimes A–D → gradient-boosting forecasts of Ra, VB, wear rate, temperature and 30-second risk → a shop dashboard.")
    speak_card(s, Inches(6.80), Inches(4.90), Inches(6.15), Inches(2.05), "What we are not doing",
               "We are not replacing the operator. We are not a certified emergency stop. We are not a residual-stress twin. We give an earlier, explainable warning the operator can act on.")
    notes(s, """
This project is mainly an early-warning system for surface degradation in CNC milling of Al 6061.

Normally we discover a bad surface after the cut. We want to know during the cut whether the process is still healthy and whether Ra is likely to leave specification soon.

Surface integrity in this B.Tech work means Ra, not residual stress.

We built a complete monitor: signals, physics, regimes, predictions, and a dashboard.

We are not replacing the operator and we are not an emergency stop.
""")


def t_aim():
    s = blank()
    header(s, "Theory  ·  speak this", "Aim of the project", 3)
    rrect(s, Inches(0.35), Inches(1.18), Inches(12.6), Inches(1.55), NAVY)
    tb(s, Inches(0.55), Inches(1.32), Inches(12.2), Inches(1.30),
       "Aim: design, implement and demonstrate a physics-informed multimodal learning system for latent regime discovery and early surface-integrity degradation prediction in CNC milling of Al 6061, packaged as a usable shop-floor dashboard.",
       size=18, bold=True, color=WHITE)
    aims = [
        ("Move the moment of truth", "From post-process Ra measurement to a short-horizon forecast while the tool is still in the cut."),
        ("Name the state of the cut", "Discover latent regimes A–D so a mechanic can say “stable / watch / risk / severe” without reading a neural embedding."),
        ("Keep engineering in the model", "A cutting-power residual so force and power cannot silently disagree. Physics constrains the learner."),
        ("Give the operator a decision, not a score", "STABLE / WATCH / SURFACE RISK, typed physical limits, and a Hold request that is not an e-stop."),
    ]
    for i, (t, b) in enumerate(aims):
        x = Inches(0.35) + (i % 2) * Inches(6.45)
        y = Inches(2.90) + (i // 2) * Inches(2.00)
        speak_card(s, x, y, Inches(6.25), Inches(1.88), t, b)
    notes(s, """
The aim is to design, implement and demonstrate a physics-informed multimodal system for latent regime discovery and early surface-integrity prediction in Al 6061 milling, as a shop-floor dashboard.

We want to move the moment of truth from after the pass to during the pass.

We want named regimes, a physics residual, and an operator-facing decision — not a hidden score.

We do not aim to replace the operator or to certify an emergency stop.
""")


def t_ideation():
    s = blank()
    header(s, "Theory  ·  speak this", "Ideation — how the idea was formed", 4)
    speak_card(s, Inches(0.35), Inches(1.18), Inches(12.6), Inches(1.55), "The first observation",
               "Every machining student has seen this: the part looks acceptable under workshop lights and fails a roughness check later. The operator already felt the spindle note change, but that knowledge was not written down, not shared with the next shift, and not attached to the job card.")
    rejected = [
        ("Rejected: live stylus on the spindle", "Ra is not a live sensor. A stylus on a rotating tool is not how roughness is measured."),
        ("Rejected: residual stress from vibration", "Dishonest without XRD booked. We refuse to print “integrity” and mean residual stress."),
        ("Rejected: a huge deep network", "No labelled campaign yet. Uninterpretable in a MED viva. Would overfit the simulator."),
        ("Rejected: probability as e-stop", "Risk rose while the cut was still useful. Tripping on it trains the operator to switch the system off."),
    ]
    for i, (t, b) in enumerate(rejected):
        x = Inches(0.35) + (i % 2) * Inches(6.45)
        y = Inches(2.90) + (i // 2) * Inches(2.00)
        speak_card(s, x, y, Inches(6.25), Inches(1.88), t, b, accent=RED)
    notes(s, """
The idea started from a shop fact: roughness is discovered late, while the operator already heard the cut changing.

We rejected a live stylus, fake residual stress, a huge deep net, and using probability as an emergency stop.

The idea that survived is: multimodal signals, a physics residual, unnamed clusters that we later call A–D, short-horizon Ra and wear, and a dashboard a shop can read.
""")


def t_why():
    s = blank()
    header(s, "Theory  ·  speak this", "Why we are making this project", 5)
    speak_card(s, Inches(0.35), Inches(1.18), Inches(6.25), Inches(2.75), "Academic reason",
               "A mechanical B.Tech must connect cutting science to data. Industry 4.0 is often a poster. This project forces a SensorFrame, a limit, and a Hold request — and forces us to say what we did not measure.")
    speak_card(s, Inches(6.80), Inches(1.18), Inches(6.15), Inches(2.75), "Industrial reason",
               "Machining is dynamic. Tool wear, chatter, force, power and temperature all move during one programme. Post-process Ra is late. Fixed-time tool change wastes carbide. Threshold TCM catches breakage, not a 12-second Ra cliff.")
    speak_card(s, Inches(0.35), Inches(4.10), Inches(6.25), Inches(2.85), "National / MSME reason",
               "Indian job shops are asked for documented quality. They have used PCs and operators who hear the cut — not six-figure TCM on every vice. A laptop-plus-Arduino path is the first layer they can actually try.")
    speak_card(s, Inches(6.80), Inches(4.10), Inches(6.15), Inches(2.85), "The sentence to remember",
               "We are not trying to replace the machine operator. We are trying to give the operator an earlier and more explainable warning — in micrometres and millimetres, not in an opaque score.")
    notes(s, """
We are making this project for four reasons.

Academically: connect manufacturing science to a system another person can run.

Industrially: the cut changes during the programme; late Ra and calendar tool-change both waste money.

For MSMEs and colleges: a cheap first integrity layer.

Ethically: we help the operator; we do not replace the operator.
""")


def t_research():
    s = blank()
    header(s, "Theory  ·  speak this", "Why this is a good research topic", 6)
    points = [
        ("Surface integrity is a moving window", "Wear, chatter and heat shift Ra during a single programme. Predicting that shift is a research problem, not only a coding exercise."),
        ("The 2025 literature is still thin here", "Wear class, VB, chatter and Ra are standard ML tasks. Simultaneous Ra + VB + named regimes + a physics residual + an honest HMI is still early-stage."),
        ("Unsupervised regimes match the shop", "Nobody agrees how to label every window as “chatter” or “BUE”. GMM finds neighbourhoods. We name them after we see the behaviour."),
        ("Physics-informed at the right scale", "P ≈ Pidle + Fc·Vc is a constraint a lecturer can write on the board. That is research honesty, not a FEM twin we cannot identify."),
        ("The formulation is citable", "Integrity as short-horizon Ra-proxy risk in a latent regime, with a mechanics residual, delivered as an artefact. That can be attacked and improved."),
        ("The limitation is part of the topic", "Simulation ≠ lab. Refusing fake 95% accuracy is itself a research contribution at B.Tech scale."),
    ]
    for i, (t, b) in enumerate(points):
        x = Inches(0.35) + (i % 3) * Inches(4.28)
        y = Inches(1.18) + (i // 3) * Inches(2.85)
        speak_card(s, x, y, Inches(4.12), Inches(2.70), t, b)
    notes(s, """
This is a research topic because surface integrity moves during the cut, the literature still treats simultaneous Ra and wear as early-stage, unsupervised regimes match how shops actually talk, and the physics residual is a real constraint.

The contribution appropriate to this degree is the formulation plus the artefact plus the refusals — not a fake laboratory accuracy number.
""")


def t_current():
    s = blank()
    header(s, "Theory  ·  speak this", "Current impact — what this already changes", 7)
    speak_card(s, Inches(0.35), Inches(1.18), Inches(6.25), Inches(2.75), "What exists today because of this B.Tech",
               "A complete, runnable integrity layer: dashboard, simulator, serial path, mill bridge, typed limits, and three honesty sentences. A laboratory can demonstrate early warning tomorrow morning without buying a commercial TCM.")
    speak_card(s, Inches(6.80), Inches(1.18), Inches(6.15), Inches(2.75), "Who is helped right now",
               "Teaching labs: a station between the mill and the profilometer. MSMEs: an architecture they can understand. Tier plants: a clearer vendor brief — regimes, Ra head, operator limits — not a poster.")
    speak_card(s, Inches(0.35), Inches(4.10), Inches(6.25), Inches(2.85), "Market context — not our revenue",
               "Global tool-condition monitoring is about USD 1.8 billion in the mid-2020s. Shops lose money on scrap, unplanned stops, wasted inserts and metrology walks. This repository does not capture that market. It shows the first layer those shops are missing.")
    speak_card(s, Inches(6.80), Inches(4.10), Inches(6.15), Inches(2.85), "What must not be claimed today",
               "We do not claim measured plant savings. We do not claim profilometer accuracy. We do not claim a certified stop. Current impact is architectural and educational first, commercial second.")
    notes(s, """
The current impact is local and real: a runnable monitor and a language for early warning.

Colleges and MSMEs are helped now. The global TCM market is only context.

We do not claim rupee savings or laboratory RMSE from the simulator.
""")


def t_future():
    s = blank()
    header(s, "Theory  ·  speak this", "Future advantages — how this can change industry", 8)
    if (FIG / "fig10_roadmap.png").exists():
        pic(s, FIG / "fig10_roadmap.png", Inches(0.25), Inches(1.15), Inches(12.8), Inches(2.35))
    cards = [
        ("If Ra and VB are measured", "The same HMI becomes an in-process capability story: Regime C predicts a failed coupon with a stated false-alarm rate. Tools can be kept one batch longer or pulled one batch earlier — with a record."),
        ("On quality and digital thread", "Regime traces, predicted Ra and Hold events stored with the job card. Quality can ask: which regime was the cut in when this coupon failed? That is stronger than “what was the programmed feed?”"),
        ("On people and the market", "Operators get a colour they can argue with. Graduates sit between a spindle and a model. Vendors get a specification. “Industry 4.0” becomes a hold request and an Ra forecast, not a corridor poster."),
    ]
    for i, (t, b) in enumerate(cards):
        speak_card(s, Inches(0.35) + i * Inches(4.28), Inches(3.65), Inches(4.12), Inches(3.30), t, b)
    notes(s, """
Future industrial impact is conditional on a labelled campaign.

If measured Ra and VB replace simulated labels, shops can keep or pull tools with a quality record.

A cheap digital thread — regime plus Ra on the job card — changes how quality talks.

People are not replaced. They get a shared language.

We do not advertise autonomous feed override or fake residual stress as the future.
""")


def s01():
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, W, H, NAVY)
    rect(s, 0, 0, Inches(0.18), H, GOLD)
    if LOGO.exists():
        s.shapes.add_picture(str(LOGO), Inches(0.55), Inches(0.32), Inches(0.92), Inches(0.92))
    tb(s, Inches(1.65), Inches(0.42), Inches(11), Inches(0.32), "INDIAN INSTITUTE OF TECHNOLOGY PATNA", size=15, bold=True, color=GOLD)
    tb(s, Inches(1.65), Inches(0.76), Inches(11), Inches(0.30), "Department of Mechanical Engineering  ·  B.Tech Project Presentation", size=14, color=WHITE)
    rect(s, Inches(0.55), Inches(1.50), Inches(2.8), Inches(0.06), GOLD)
    tb(s, Inches(0.55), Inches(1.75), Inches(12.2), Inches(2.05),
       "Physics-Informed Multimodal Learning for Latent Regime Discovery and Early Surface-Integrity Degradation Prediction in CNC Milling of Aluminum Alloy",
       size=26, bold=True, color=WHITE)
    rrect(s, Inches(0.55), Inches(4.00), Inches(12.2), Inches(1.15), NAVY2)
    tb(s, Inches(0.75), Inches(4.18), Inches(11.8), Inches(0.80),
       "Instead of detecting poor surface quality after machining, we use multiple machining signals + physics + machine learning to predict degradation early enough for an operator to act.",
       size=18, color=WHITE)
    for i, (lab, val) in enumerate((
        ("Presented by", "Rajshekhar   ·   Piyush Jatoliya"),
        ("Guide", "Dr. Mahavir Singh"),
        ("The shift", "Post-process detection  →  early prediction"),
    )):
        x = Inches(0.55) + i * Inches(4.15)
        rrect(s, x, Inches(5.40), Inches(3.95), Inches(1.25), NAVY2)
        tb(s, x + Inches(0.16), Inches(5.50), Inches(3.65), Inches(0.28), lab.upper(), size=11, bold=True, color=GOLD)
        tb(s, x + Inches(0.16), Inches(5.82), Inches(3.65), Inches(0.65), val, size=15, bold=True, color=WHITE)
    tb(s, Inches(0.55), Inches(6.85), Inches(12.2), Inches(0.3),
       "20 slides  ·  theory you can speak  ·  method diagrams  ·  live site  ·  October 2026", size=13, color=RGBColor(0xB8, 0xC4, 0xD0))
    notes(s, """
Good morning everyone.

Our project is titled “Physics-Informed Multimodal Learning for Latent Regime Discovery and Early Surface-Integrity Degradation Prediction in CNC Milling of Aluminum Alloy.”

The basic problem we are addressing is quite simple.

In CNC milling, we want to produce a component with good surface quality. But normally, surface roughness is measured after the machining operation. So if the surface has already become unacceptable, we discover the problem only after the damage has happened.

Similarly, operators may change a tool after a fixed number of parts or when they hear chatter.

Our objective is therefore to move from post-process detection to early prediction.

We developed a system that continuously observes machining signals and tries to answer:

“Is the machining process still healthy, and is the surface likely to become unacceptable in the near future?”
""")


def s02():
    s = blank()
    header(s, "Method  ·  60 seconds", "Why is this problem important?", 9)
    pic(s, ASSETS / "talk_paths.png", Inches(0.28), Inches(1.20), Inches(12.75), Inches(3.15))
    pic(s, ASSETS / "talk_drivers.png", Inches(0.28), Inches(4.40), Inches(12.75), Inches(2.55))
    notes(s, """
The main motivation comes from the fact that machining is a dynamic process.

During milling, several things change simultaneously.

First, the tool gradually wears.

Second, vibration and chatter can increase.

Third, cutting forces and spindle power can change.

Temperature also changes during the operation.

All of these can eventually affect the surface roughness.

The problem with conventional post-process inspection is that the operator learns about the problem only after the pass is complete.

On the other hand, simply changing the tool after a fixed number of parts can waste tool life.

So our idea is to continuously monitor the process and identify when the machining process moves from a stable condition towards degradation.

The report specifically defines surface integrity for this B.Tech project using Ra, arithmetic mean surface roughness, as the primary proxy.

Important sentence: “We are not trying to replace the machine operator. We are trying to give the operator an earlier and more explainable warning.”
""")


def s03():
    s = blank()
    header(s, "Method  ·  60 seconds", "What exactly are we monitoring?", 10)
    # input table header
    heads = ["Signal", "What it tells us"]
    rows = [
        ("Vibration", "Chatter / instability"),
        ("Force", "Cutting load"),
        ("Spindle power", "Energy consumption"),
        ("Temperature", "Thermal behaviour"),
        ("Feed & speed", "Operating condition"),
    ]
    rect(s, Inches(0.35), Inches(1.22), Inches(6.35), Inches(0.46), NAVY)
    tb(s, Inches(0.50), Inches(1.28), Inches(2.6), Inches(0.36), "INPUT SIGNAL", size=13, bold=True, color=WHITE)
    tb(s, Inches(3.20), Inches(1.28), Inches(3.3), Inches(0.36), "WHAT IT TELLS US", size=13, bold=True, color=WHITE)
    for i, (a, b) in enumerate(rows):
        y = Inches(1.68) + i * Inches(0.62)
        bg = WHITE if i % 2 == 0 else RGBColor(0xE8, 0xEE, 0xF4)
        rect(s, Inches(0.35), y, Inches(6.35), Inches(0.62), bg)
        tb(s, Inches(0.50), y + Inches(0.12), Inches(2.6), Inches(0.40), a, size=16, bold=True, color=NAVY)
        tb(s, Inches(3.20), y + Inches(0.12), Inches(3.3), Inches(0.40), b, size=16, color=INK)

    tb(s, Inches(7.00), Inches(1.22), Inches(5.95), Inches(0.36), "OUTPUTS OF THE SYSTEM", size=13, bold=True, color=GOLD)
    outs = [
        ("Regime A–D", "Latent machining state"),
        ("Ra prediction", "Surface integrity proxy"),
        ("Tool wear VB", "Flank-wear land"),
        ("Wear rate", "How fast the tool is dying"),
        ("Temperature", "Thermal state"),
        ("Degradation probability", "Risk in the next 30 s"),
    ]
    for i, (t, d) in enumerate(outs):
        y = Inches(1.62) + i * Inches(0.62)
        rrect(s, Inches(7.00), y, Inches(5.95), Inches(0.56), WHITE, line=LINE)
        tb(s, Inches(7.15), y + Inches(0.08), Inches(2.7), Inches(0.40), t, size=14, bold=True, color=NAVY)
        tb(s, Inches(9.90), y + Inches(0.08), Inches(2.9), Inches(0.40), d, size=13, color=MUTED)

    rrect(s, Inches(0.35), Inches(4.90), Inches(12.6), Inches(2.05), WHITE, line=LINE)
    tb(s, Inches(0.55), Inches(5.02), Inches(12.2), Inches(0.32), "DEFAULT PROCESS WINDOW  ·  AL 6061 END MILLING", size=12, bold=True, color=GOLD)
    tb(s, Inches(0.55), Inches(5.40), Inches(12.2), Inches(1.35),
       "10 mm four-flute tool   ·   3000 r/min   ·   0.12 mm/tooth   ·   ap = 1.0 mm\nRa limit = 1.6 µm   ·   VB demo limit = 0.30 mm   ·   Vc ≈ 94 m/min   ·   tooth-passing frequency = 200 Hz\nMultimodal = we do not ask one sensor to explain the whole cut.",
       size=18, color=NAVY)
    notes(s, """
For the material, we use Aluminium 6061 as our default workpiece.

The system considers multiple signals instead of relying on just one sensor.

We use vibration, cutting force, spindle power, temperature, and commanded machining parameters such as feed and spindle speed.

This is what we mean by multimodal learning.

Instead of asking one signal to explain the entire machining process, we combine information from different physical sources.

Our system then predicts several quantities: surface roughness Ra, flank wear VB, wear rate, temperature, and short-horizon degradation probability.

For the demonstration, the roughness limit is 1.6 micrometres, and the demonstration flank-wear limit is 0.30 mm.
""")


def s04():
    s = blank()
    header(s, "Method  ·  70 seconds  ·  key diagram", "Overall methodology — the pipeline", 11)
    pic(s, ASSETS / "talk_pipeline.png", Inches(0.20), Inches(1.15), Inches(12.95), Inches(5.85))
    notes(s, """
Now I will explain the complete methodology.

First, all our data sources are converted into a common structure called a SensorFrame.

This is important because our system can receive information from a simulator, serial sensors, or an HTTP-based bridge without changing the rest of the ML pipeline.

We then divide the signals into short windows. In our implementation, the feature window is 0.25 seconds.

From each window, we calculate meaningful features.

These include vibration RMS, kurtosis, crest factor, force RMS, force fluctuation, chatter-band energy, spectral entropy, temperature, spindle power, and a physics residual.

These features are then given to two major parts of the system.

The first is Gaussian Mixture Model, or GMM, which discovers the current machining regime.

The second is Histogram-based Gradient Boosting, which predicts quantities such as Ra and tool wear.

Finally, the supervisor compares these predictions with physical limits and presents the result through our dashboard.
""")


def s05():
    s = blank()
    header(s, "Method  ·  75 seconds  ·  viva hotspot", "The physics-informed part", 12)
    rrect(s, Inches(0.35), Inches(1.22), Inches(6.25), Inches(2.55), WHITE, line=LINE)
    tb(s, Inches(0.55), Inches(1.35), Inches(5.9), Inches(0.32), "PHYSICS CONSTRAINT", size=13, bold=True, color=GOLD)
    tb(s, Inches(0.55), Inches(1.80), Inches(5.9), Inches(0.85), "P  ≈  Pidle  +  Fc · Vc", size=32, bold=True, color=NAVY, align="center")
    tb(s, Inches(0.55), Inches(2.75), Inches(5.9), Inches(0.75), "Cutting power should match cutting force × cutting speed, plus a roughly constant idle term.", size=15, color=INK)

    rrect(s, Inches(6.80), Inches(1.22), Inches(6.15), Inches(2.55), WHITE, line=LINE)
    tb(s, Inches(7.00), Inches(1.35), Inches(5.8), Inches(0.32), "PHYSICS RESIDUAL  (ML FEATURE)", size=13, bold=True, color=GOLD)
    tb(s, Inches(7.00), Inches(1.78), Inches(5.8), Inches(1.05), "R  =  |Pmeas − (Pidle + Fc·Vc)|\n        /  max(Pmeas , 1)", size=22, bold=True, color=NAVY, align="center")
    tb(s, Inches(7.00), Inches(2.95), Inches(5.8), Inches(0.60), "Large R  →  process changed, or the sensing chain is lying.", size=14, color=INK)

    pic(s, ASSETS / "talk_physics.png", Inches(0.25), Inches(3.95), Inches(12.8), Inches(2.95))
    notes(s, """
The important part that makes our approach physics-informed is that we don't allow the machine-learning model to rely only on statistical correlations.

We introduce a simple physical relationship from cutting mechanics.

Cutting power can approximately be related to cutting force and cutting velocity:

P is approximately equal to idle power plus cutting force multiplied by cutting velocity.

So we compare the measured spindle power with the power expected from the measured cutting force and cutting speed.

The difference between these two gives us a physics residual.

If measured power and force-based power disagree significantly, it can indicate that either the machining process has changed or something is wrong in the sensing chain.

We then provide this residual as an additional feature to the machine-learning model.

This is what makes the model physics-informed at the scale of this project. It is not a finite-element digital twin and it is not a residual-stress calculation.

In simple terms: Machine learning tells us what pattern the data resembles, while physics gives the model an engineering constraint that the process should obey.
""")


def s06():
    s = blank()
    header(s, "Method  ·  70 seconds", "Latent regime discovery using GMM", 13)
    pic(s, ASSETS / "talk_regimes.png", Inches(0.25), Inches(1.18), Inches(12.8), Inches(3.15))
    rrect(s, Inches(0.35), Inches(4.50), Inches(6.25), Inches(2.45), WHITE, line=LINE)
    tb(s, Inches(0.55), Inches(4.62), Inches(5.9), Inches(0.32), "GMM  =  UNSUPERVISED LEARNING", size=13, bold=True, color=GOLD)
    tb(s, Inches(0.55), Inches(5.05), Inches(5.9), Inches(1.70),
       "No manual rule “if vibration > X, call it unstable.”\nThe model finds clusters in feature space.\nWe name the clusters afterwards: A–D.",
       size=16, color=INK)
    rrect(s, Inches(6.80), Inches(4.50), Inches(6.15), Inches(2.45), WHITE, line=LINE)
    tb(s, Inches(7.00), Inches(4.62), Inches(5.8), Inches(0.32), "IF ASKED: WHY NOT K-MEANS?", size=13, bold=True, color=GOLD)
    tb(s, Inches(7.00), Inches(5.05), Inches(5.8), Inches(1.70),
       "GMM gives probabilistic membership, not only a hard label. Machining regimes change gradually. Soft assignment matches that physics.",
       size=16, color=INK)
    notes(s, """
The next question is: how do we determine the current state of machining?

Instead of manually writing rules such as “if vibration is greater than X, call it unstable,” we use an unsupervised machine-learning method called a Gaussian Mixture Model.

The GMM looks at the feature space and identifies groups of similar operating conditions.

We use four regimes.

Regime A represents stable cutting.

Regime B represents a transitional condition.

Regime C represents an unstable or surface-risk condition.

And Regime D represents severe degradation.

Importantly, the GMM itself doesn't understand words like “stable” or “severe.”

Mathematically, it only discovers clusters.

We assign engineering meaning to those clusters based on their behaviour.

In our simulator, as tool wear and chatter increase, the system moves approximately from A to B to C and finally D.

If they ask “Why GMM instead of K-means?”

Say: GMM gives us probabilistic cluster membership rather than only a hard cluster assignment, so it is useful when the transition between machining regimes is gradual rather than perfectly separated.
""")


def s07():
    s = blank()
    header(s, "Method  ·  75 seconds", "Prediction and early warning", 14)
    pic(s, ASSETS / "talk_early.png", Inches(0.22), Inches(1.15), Inches(8.15), Inches(4.35))
    outs = ["Ra", "VB", "Wear rate", "Temperature", "P(degrade in 30 s)"]
    tb(s, Inches(8.55), Inches(1.20), Inches(4.45), Inches(0.32), "GRADIENT BOOSTING HEADS", size=12, bold=True, color=GOLD)
    for i, t in enumerate(outs):
        y = Inches(1.58) + i * Inches(0.62)
        rrect(s, Inches(8.55), y, Inches(4.40), Inches(0.54), WHITE, line=LINE)
        tb(s, Inches(8.70), y + Inches(0.08), Inches(4.1), Inches(0.38), t, size=16, bold=True, color=NAVY)
    rrect(s, Inches(0.35), Inches(5.60), Inches(12.6), Inches(1.35), WHITE, line=LINE)
    tb(s, Inches(0.55), Inches(5.72), Inches(12.2), Inches(1.10),
       "Key concept: current Ra may still be safe, but 30-second future risk may already be high.\nThat is the window in which the operator can inspect, finish the feature, or prepare a tool change.",
       size=18, bold=True, color=NAVY)
    notes(s, """
After discovering the machining regime, we need to predict what is going to happen next.

For this we use Histogram-based Gradient Boosting models.

We train prediction heads for surface roughness Ra, flank wear VB, wear rate, temperature and short-horizon degradation probability.

The important concept here is early warning.

Suppose the current Ra is still below the allowed limit.

If we only look at the current Ra, we might say that everything is fine.

But the other signals — for example increasing vibration, chatter energy, force and wear — may indicate that the surface will cross the limit soon.

Therefore, our degradation head looks ahead by a 30-second horizon.

This creates a useful situation where: current surface quality is still acceptable, but future risk is increasing.

That is exactly the window in which an operator can inspect the tool, finish the current feature, or prepare for a tool change.

The report specifically shows this transition in the simulated run: predicted Ra rises toward 1.6 µm, VB approaches 0.30 mm, while degradation probability can rise earlier.
""")


def s08():
    s = blank()
    header(s, "Method  ·  60 seconds", "Dashboard and decision logic", 15)
    # three status chips
    for i, (name, col) in enumerate((("STABLE", GREEN), ("WATCH", RGBColor(0xC4, 0x8A, 0x1A)), ("SURFACE RISK", RED))):
        rrect(s, Inches(0.35) + i * Inches(4.28), Inches(1.22), Inches(4.10), Inches(0.70), col)
        tb(s, Inches(0.35) + i * Inches(4.28), Inches(1.34), Inches(4.10), Inches(0.48), name, size=20, bold=True, color=WHITE, align="center")
    metrics = ["Regime A–D", "Ra (µm)", "VB (mm)", "Temperature", "Risk probability", "ETA to limit"]
    for i, m in enumerate(metrics):
        x = Inches(0.35) + (i % 3) * Inches(4.28)
        y = Inches(2.10) + (i // 3) * Inches(0.85)
        rrect(s, x, y, Inches(4.10), Inches(0.74), WHITE, line=LINE)
        tb(s, x, y + Inches(0.16), Inches(4.10), Inches(0.44), m, size=18, bold=True, color=NAVY, align="center")
    pic(s, ASSETS / "talk_decision.png", Inches(0.20), Inches(3.90), Inches(12.9), Inches(2.05))
    rrect(s, Inches(0.35), Inches(6.05), Inches(12.6), Inches(0.95), NAVY)
    tb(s, Inches(0.55), Inches(6.22), Inches(12.2), Inches(0.65),
       "Probability informs   ·   physical limits trip   ·   software Hold is not an emergency stop.",
       size=20, bold=True, color=GOLD, align="center")
    notes(s, """
All these predictions are brought together in a shop-floor dashboard.

The dashboard uses simple terminology such as STABLE, WATCH and SURFACE RISK, rather than forcing the operator to understand the underlying machine-learning mathematics.

It displays the current regime, predicted Ra, tool wear, temperature and degradation probability.

One of the most important design decisions we made concerns safety.

We do not use degradation probability itself as an automatic hard stop.

Instead, probability is used as a warning.

Physical quantities such as Ra, VB, temperature, vibration or force can be compared against operator-defined limits.

If a physical hard limit is crossed, the system can request a software Hold on the visualisation CNC.

This is different from an emergency stop.

A software Hold is only a demonstration/control action; it is not a certified safety function.

Say this clearly: “Probability informs; physical limits trip; and software Hold is not an emergency stop.”
""")


def s09():
    s = blank()
    header(s, "Results  ·  70 seconds", "Results — what the demonstration actually shows", 16)
    pic(s, FIG / "fig2_regimes.png", Inches(0.25), Inches(1.15), Inches(8.05), Inches(4.05))
    bullets = [
        "A → B → C → D",
        "Ra rises toward 1.6 µm",
        "VB toward 0.30 mm",
        "Vibration / chatter rise",
        "Risk rises before the limit",
        "Dashboard responds",
    ]
    for i, t in enumerate(bullets):
        y = Inches(1.20) + i * Inches(0.68)
        rrect(s, Inches(8.50), y, Inches(4.45), Inches(0.60), WHITE, line=LINE)
        tb(s, Inches(8.65), y + Inches(0.10), Inches(4.2), Inches(0.40), t, size=16, bold=True, color=NAVY)
    rrect(s, Inches(0.35), Inches(5.35), Inches(12.6), Inches(1.60), WHITE, line=LINE)
    tb(s, Inches(0.55), Inches(5.48), Inches(12.2), Inches(1.35),
       "Main result is not “high accuracy.” Main result is the complete pipeline:\nsignal → features → physics → regime → prediction → risk → operator decision.\nTraining today is physics-simulated. Simulation ≠ laboratory validation.",
       size=17, bold=True, color=NAVY)
    notes(s, """
Now coming to the results.

I want to be very clear about what these results mean.

Our current training results are based on a physics-inspired simulator, not a fully labelled physical CNC campaign.

In the simulated run, the system starts in Regime A.

As wear and instability increase, the feature values change and the GMM moves toward Regime B and then Regime C.

At the same time, predicted Ra increases toward the 1.6 micrometre limit and predicted flank wear approaches 0.30 millimetres.

The degradation probability can become high before the current Ra actually crosses the limit.

Therefore, the main result is not simply “our model has high accuracy.”

The more important result is that we demonstrated the complete early-warning pipeline:

signal acquisition → feature extraction → physics constraint → regime discovery → prediction → risk assessment → operator decision.

The report deliberately treats the simulation as a necessary demonstration, but not as a substitute for laboratory validation.
""")


def s10():
    s = blank()
    header(s, "Close  ·  75–90 seconds", "Comparison, conclusion and future work", 17)
    rows = [
        ("Existing method", "Limitation"),
        ("Fixed-time tool change", "Wastes tool life"),
        ("Post-process Ra", "Detects the problem late"),
        ("Threshold TCM", "Limited early prediction"),
        ("Black-box deep learning", "Less interpretable; needs labelled data"),
        ("Our approach", "Early + multimodal + physics-informed"),
    ]
    for i, (a, b) in enumerate(rows):
        y = Inches(1.18) + i * Inches(0.52)
        bg = NAVY if i == 0 else (RGBColor(0xE4, 0xF0, 0xE8) if i == 5 else (WHITE if i % 2 else RGBColor(0xE8, 0xEE, 0xF4)))
        fg = WHITE if i == 0 else NAVY
        rect(s, Inches(0.35), y, Inches(6.15), Inches(0.52), bg)
        rect(s, Inches(6.50), y, Inches(6.45), Inches(0.52), bg)
        tb(s, Inches(0.50), y + Inches(0.08), Inches(5.9), Inches(0.36), a, size=14, bold=True, color=fg)
        tb(s, Inches(6.65), y + Inches(0.08), Inches(6.15), Inches(0.36), b, size=14, bold=(i in (0, 5)), color=fg)

    tb(s, Inches(0.40), Inches(4.40), Inches(12.5), Inches(0.32), "FUTURE WORK  —  not a bigger network first", size=13, bold=True, color=GOLD)
    future = ["Simulation", "Real CNC", "Measured Ra / VB", "Retrain", "Validation", "Industrialise"]
    for i, t in enumerate(future):
        x = Inches(0.35) + i * Inches(2.15)
        rrect(s, x, Inches(4.78), Inches(2.00), Inches(0.70), NAVY2)
        tb(s, x, Inches(4.90), Inches(2.00), Inches(0.48), t, size=13, bold=True, color=WHITE, align="center")
        if i < 5:
            tb(s, x + Inches(1.85), Inches(4.90), Inches(0.35), Inches(0.48), "→", size=16, bold=True, color=GOLD, align="center")

    rrect(s, Inches(0.35), Inches(5.65), Inches(12.6), Inches(1.30), NAVY)
    tb(s, Inches(0.55), Inches(5.80), Inches(12.2), Inches(1.05),
       "We move CNC milling from “detect the problem after it happens” to “predict the problem before it happens.”\nLimitation: current training is simulation-based. Real Ra and VB are the next experiment.",
       size=16, bold=True, color=WHITE)
    notes(s, """
Finally, how is our approach different from existing strategies?

With fixed-time tool change, we may replace a tool that still has useful life.

With post-process roughness measurement, we detect the problem only after the surface has already been produced.

Threshold-based tool-condition monitoring is useful, particularly for events such as tool breakage, but it does not necessarily predict future surface roughness.

And large black-box machine-learning models can be difficult to interpret and require large amounts of labelled data.

Our approach tries to combine the advantages: multimodal sensing, physics-based information, unsupervised regime discovery, short-horizon prediction and an explainable dashboard.

However, our work has an important limitation.

The current models are trained using simulated data.

So the next step is not simply to use a bigger neural network.

The next step is to collect real experimental data.

We would perform controlled experiments on Al 6061, measure vibration, current and temperature, and after each pass measure Ra using a profilometer and VB using tool inspection. The models can then be retrained and evaluated using real labels.

Only after this validation should we move toward industrial deployment and discuss more advanced quantities such as residual stress.

So, to conclude, our project demonstrates a complete and explainable framework for moving CNC machining from “detect the problem after it happens” toward “predict the problem before it happens.”

Thank you.

30-SECOND BACKUP IF INTERRUPTED:
Our project is an early-warning system for surface degradation during CNC milling of Al 6061. We combine vibration, force, spindle power, temperature and machining parameters into a multimodal feature vector. A Gaussian Mixture Model identifies machining regimes from stable to severe, while gradient-boosting models predict Ra, tool wear and short-term degradation risk. We also introduce a physics residual based on the cutting-power relationship, making the prediction more physically interpretable. The complete system is demonstrated through a dashboard and simulator. The important limitation is that the current training is simulation-based, so real CNC experiments with measured Ra and VB are the next step.
""")


def s11_mill():
    s = blank()
    header(s, "Part II  ·  live artefact", "The CNC site we built — ForgeMill", 18)
    mill = ASSETS / "mill_full.png"
    if not mill.exists():
        mill = ASSETS / "mill_running.png"
    pic(s, mill, Inches(0.25), Inches(1.15), Inches(8.6), Inches(5.75))
    points = [
        "Cycle start / Hold / Stop",
        "Iso + Top 3-D toolpath",
        "G-code + DRO",
        "Bridge on :8766 hooks the mill",
        "Cycle start starts the monitor",
        "Hold freezes pose — not e-stop",
    ]
    for i, t in enumerate(points):
        y = Inches(1.22) + i * Inches(0.78)
        rrect(s, Inches(9.05), y, Inches(3.95), Inches(0.68), WHITE, line=LINE)
        tb(s, Inches(9.18), y + Inches(0.14), Inches(3.7), Inches(0.42), t, size=14, bold=True, color=NAVY)
    notes(s, "This is Part II — the actual site. Open the Vercel mill, press Cycle start, show Iso view, then Hold. Do not call Hold an emergency stop.")


def s12_dash():
    s = blank()
    header(s, "Part II  ·  live artefact", "Integrity monitor — live simulator", 19)
    pic(s, ASSETS / "dashboard_live.png", Inches(0.22), Inches(1.15), Inches(8.7), Inches(5.75))
    points = [
        "STABLE / WATCH / SURFACE RISK",
        "Regime, Ra, VB, risk, ETA",
        "Typed physical hard-stops",
        "This capture: Regime B, risk high, wear-rate trip",
        "Decision support only",
        "streamlit run dashboard/app.py",
    ]
    for i, t in enumerate(points):
        y = Inches(1.22) + i * Inches(0.78)
        rrect(s, Inches(9.10), y, Inches(3.90), Inches(0.68), WHITE, line=LINE)
        tb(s, Inches(9.22), y + Inches(0.12), Inches(3.65), Inches(0.46), t, size=13, bold=True, color=NAVY)
    notes(s, "Show the live dashboard. Point to regime colour, Ra, risk, and the hard-stop banner. Repeat: probability informs; millimetres trip.")


def s13_thanks():
    s = prs.slides.add_slide(prs.slide_layouts[6])
    rect(s, 0, 0, W, H, NAVY)
    rect(s, 0, 0, Inches(0.18), H, GOLD)
    if LOGO.exists():
        s.shapes.add_picture(str(LOGO), Inches(0.50), Inches(0.32), Inches(0.78), Inches(0.78))
    tb(s, Inches(1.45), Inches(0.42), Inches(11), Inches(0.30), "INDIAN INSTITUTE OF TECHNOLOGY PATNA", size=14, bold=True, color=GOLD)
    tb(s, Inches(1.45), Inches(0.76), Inches(11), Inches(0.28), "Department of Mechanical Engineering", size=13, color=WHITE)
    tb(s, Inches(0.4), Inches(1.25), Inches(12.5), Inches(0.85), "Thank you", size=54, bold=True, color=WHITE, align="center")
    tb(s, Inches(0.4), Inches(2.12), Inches(12.5), Inches(0.40),
       "Questions welcome  ·  scan a code  ·  or open the live mill", size=18, color=GOLD, align="center")
    for x, title, sub, qn_ in (
        (Inches(2.15), "Open the live site", SITE, ASSETS / "qr_site.png"),
        (Inches(7.35), "Scan to ask a question", "Opens a mail draft — type your question", ASSETS / "qr_ask.png"),
    ):
        rrect(s, x, Inches(2.70), Inches(3.85), Inches(3.45), NAVY2)
        if qn_.exists():
            s.shapes.add_picture(str(qn_), x + Inches(0.95), Inches(2.85), Inches(1.95), Inches(1.95))
        tb(s, x + Inches(0.12), Inches(4.90), Inches(3.60), Inches(0.32), title, size=15, bold=True, color=WHITE, align="center")
        tb(s, x + Inches(0.12), Inches(5.25), Inches(3.60), Inches(0.70), sub, size=11, color=RGBColor(0xC5, 0xD0, 0xDA), align="center")
    box = tb(s, Inches(1.0), Inches(6.35), Inches(11.3), Inches(0.32), SITE, size=14, bold=True, color=GOLD, align="center")
    try:
        r_id = s.part.relate_to(SITE, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
        for p in box.text_frame.paragraphs:
            for run in p.runs:
                rPr = run._r.get_or_add_rPr()
                hlink = etree.SubElement(rPr, qn("a:hlinkClick"))
                hlink.set(qn("r:id"), r_id)
    except Exception:
        pass
    tb(s, Inches(0.4), Inches(6.80), Inches(12.5), Inches(0.35),
       "Rajshekhar  ·  Piyush Jatoliya  ·  Guide: Dr. Mahavir Singh", size=14, color=WHITE, align="center")
    notes(s, """
30-SECOND CONCLUSION — MEMORIZE:

Our project is an early-warning system for surface degradation during CNC milling of Al 6061. We combine vibration, force, spindle power, temperature and machining parameters into a multimodal feature vector. A Gaussian Mixture Model identifies machining regimes from stable to severe, while gradient-boosting models predict Ra, tool wear and short-term degradation risk. We also introduce a physics residual based on the cutting-power relationship, making the prediction more physically interpretable. The complete system is demonstrated through a dashboard and simulator. The important limitation is that the current training is simulation-based, so real CNC experiments with measured Ra and VB are the next step.
""")


def main():
    global prs
    make_qrs()
    prs = Presentation()
    prs.slide_width = W
    prs.slide_height = H
    s01()
    t_about()
    t_aim()
    t_ideation()
    t_why()
    t_research()
    t_current()
    t_future()
    s02()
    s03()
    s04()
    s05()
    s06()
    s07()
    s08()
    s09()
    s10()
    s11_mill()
    s12_dash()
    s13_thanks()
    prs.save(OUT)
    print("slides", len(prs.slides), "wrote", OUT)


if __name__ == "__main__":
    main()
