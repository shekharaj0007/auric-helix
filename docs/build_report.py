"""Build the B.Tech project research report as a formatted Word document."""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from report_extra import (
    ch12,
    ch13,
    ch14,
    ch15,
    contents_page,
    extra_closing_pages,
    extra_literature,
    add_table as extra_add_table,
)

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
OUT = ROOT / "BTP_Research_Report_Machining_Integrity_Monitor.docx"


def set_run_font(run, name="Times New Roman", size=12, bold=False, italic=False):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)


def add_p(doc, text, *, size=12, bold=False, italic=False, align="justify", space_after=8, first_line=True):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(space_after)
    pf.space_before = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    if first_line and align == "justify":
        pf.first_line_indent = Inches(0.3)
    p.alignment = {
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }[align]
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_h(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.color.rgb = RGBColor(0x1A, 0x2A, 0x3A)
        run.font.name = "Times New Roman"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    return p


def add_fig(doc, name, caption, width=6.3):
    path = FIG / name
    if not path.exists():
        add_p(doc, f"[Figure missing: {name}]", italic=True, first_line=False)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    run = p.add_run()
    run.add_picture(str(path), width=Inches(width))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(12)
    cap.paragraph_format.first_line_indent = Inches(0)
    r = cap.add_run(caption)
    set_run_font(r, size=11, italic=True)


def add_table(doc, headers, rows, *args, **kwargs):
    return extra_add_table(doc, headers, rows, add_p, set_run_font)


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    p.paragraph_format.space_after = Pt(4)
    if p.runs:
        p.runs[0].text = text
        set_run_font(p.runs[0], size=12)
    else:
        r = p.add_run(text)
        set_run_font(r, size=12)


def setup_doc():
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.15)
        section.right_margin = Inches(1.0)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        footer = section.footer
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run("B.Tech Project Report  |  Machining Integrity Monitor  |  Page ")
        set_run_font(r, size=9)
        # page number field
        fld = (
            '<w:fldChar w:fldCharType="begin"/>'
            '<w:instrText xml:space="preserve"> PAGE </w:instrText>'
            '<w:fldChar w:fldCharType="end"/>'
        )
        from docx.oxml import OxmlElement

        run = fp.add_run()
        set_run_font(run, size=9)
        r = run._r
        begin = OxmlElement("w:fldChar")
        begin.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = " PAGE "
        end = OxmlElement("w:fldChar")
        end.set(qn("w:fldCharType"), "end")
        r.append(begin)
        r.append(instr)
        r.append(end)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    return doc


def cover(doc):
    for _ in range(2):
        add_p(doc, "", first_line=False, space_after=0)
    add_p(doc, "A B.TECH PROJECT REPORT", size=14, bold=True, align="center", first_line=False, space_after=6)
    add_p(
        doc,
        "Physics-Informed Multimodal Learning for Latent Regime Discovery and Early Surface-Integrity Degradation Prediction in CNC Milling of Aluminum Alloy",
        size=18,
        bold=True,
        align="center",
        first_line=False,
        space_after=16,
    )
    add_p(doc, "Submitted in partial fulfilment of the requirements for the degree of", size=12, italic=True, align="center", first_line=False)
    add_p(doc, "Bachelor of Technology in Mechanical Engineering", size=14, bold=True, align="center", first_line=False, space_after=18)
    add_p(doc, "Submitted by", size=12, align="center", first_line=False)
    add_p(doc, "Raj Shekhar", size=16, bold=True, align="center", first_line=False, space_after=18)
    add_p(doc, "Process window used in the implemented system", size=12, italic=True, align="center", first_line=False)
    add_p(
        doc,
        "Workpiece: Aluminium 6061  ·  Operation: end milling  ·  Tool: 10 mm, 4 flute  ·  3000 r/min  ·  f = 0.12 mm/tooth  ·  ap = 1.0 mm  ·  Ra specification = 1.6 µm",
        size=11,
        align="center",
        first_line=False,
        space_after=22,
    )
    add_p(doc, "October 2026", size=13, bold=True, align="center", first_line=False)
    doc.add_page_break()


def front_matter(doc):
    add_h(doc, "Declaration", 1)
    add_p(
        doc,
        "I declare that this report describes original project work carried out by me during the B.Tech programme. "
        "The implemented software, dashboard, physics-inspired simulator, machine-learning pipeline and CNC-mill "
        "bridge are part of this project. Published literature is cited where used. Simulated training results are "
        "not presented as certified laboratory measurements. Software feed-hold is not a safety-rated emergency stop.",
    )
    add_p(doc, "Raj Shekhar", bold=True, first_line=False)
    add_p(doc, "Date: October 2026", first_line=False)

    add_h(doc, "Certificate", 1)
    add_p(
        doc,
        "This is to certify that the project entitled “Physics-Informed Multimodal Learning for Latent Regime Discovery "
        "and Early Surface-Integrity Degradation Prediction in CNC Milling of Aluminum Alloy” has been carried out as "
        "a B.Tech project in Mechanical Engineering. The report may be submitted for evaluation. The supervisor is not "
        "a certified CNC e-stop authority; any shop-floor use remains under the licensed machine operator.",
    )
    add_p(doc, "Project Supervisor", bold=True, first_line=False)
    add_p(doc, "(Signature and date)", italic=True, first_line=False)

    add_h(doc, "Acknowledgements", 1)
    add_p(
        doc,
        "I thank my project supervisor and the Mechanical Engineering department for guidance on framing a B.Tech "
        "problem that is both academically honest and industrially relevant. The work sits between manufacturing "
        "science and applied machine learning: it does not claim a finished digital twin of a certified machine, "
        "and it does not claim residual-stress maps from X-ray diffraction unless that measurement is later booked "
        "in the laboratory. I also acknowledge the open tooling used to build the demonstration — Python, "
        "scikit-learn, Streamlit, and a browser-based CNC visualisation (ForgeMill) hosted on Vercel — and the "
        "need to keep software Hold clearly separated from a hardwired e-stop.",
    )

    add_h(doc, "Abstract", 1)
    add_p(
        doc,
        "Surface integrity after CNC milling decides whether an aluminium part is accepted, reworked or scrapped. "
        "In teaching laboratories and small job shops the usual practice is still post-process: measure roughness "
        "after the pass, change the tool when the operator “feels” chatter, or change the tool on a conservative "
        "clock. That loop is late. Damage to the surface has already occurred. This project builds an early-warning "
        "integrity monitor for end milling of Al 6061. Multimodal process signals — vibration, force, spindle power, "
        "temperature and commanded feed/speed — are reduced to a compact feature vector. A Gaussian mixture model "
        "discovers latent machining regimes (stable, transitional, unstable, severe). Gradient-boosting heads predict "
        "roughness Ra, flank wear VB, wear rate, temperature and the probability that the surface will leave specification "
        "inside a short horizon. A physics residual, formed from the cutting-power identity P ≈ Fc · Vc, is treated as "
        "a first-class feature so that the learner is not purely correlational. A Streamlit dashboard presents live "
        "metrics, regimes, forecasts and operator-set hard-stop limits. A local bridge can follow Cycle start and Hold "
        "on a browser CNC (ForgeMill) so that a second laptop can run the monitor during a cut. Training in the present "
        "codebase is on physics-inspired simulated runs. That is sufficient to exercise the full pipeline before a "
        "labelled laboratory campaign. For the B.Tech integrity proxy, degradation is declared when predicted or "
        "measured Ra exceeds the specification (default 1.6 µm). Residual stress by XRD is not claimed. Automatic "
        "Hold is decision support, not a certified safety function. The report records ideation, aims, method, "
        "implementation, comparison with existing practice, industry and market implications, limitations and a "
        "realistic future path from simulator to shop floor.",
    )
    add_p(
        doc,
        "Keywords: CNC milling; Al 6061; surface integrity; Ra; flank wear VB; latent regimes; Gaussian mixture model; "
        "physics-informed machine learning; early warning; tool-condition monitoring; Streamlit; digital shop floor.",
        italic=True,
        first_line=False,
    )

    add_h(doc, "List of abbreviations", 1)
    abbr = [
        "Al 6061 — Aluminium alloy 6061 (default workpiece in this project)",
        "CNC — Computer numerical control",
        "DAQ — Data acquisition",
        "DRO — Digital read-out (X, Y, Z)",
        "GMM — Gaussian mixture model",
        "HGB — Histogram-based gradient boosting (scikit-learn)",
        "ISO 8688 — Tool-life testing in milling (flank-wear convention used as a demo limit)",
        "Ra — Arithmetic mean roughness (µm)",
        "SI — Surface integrity (here proxied by Ra unless a lab measurement is added)",
        "TCM — Tool-condition monitoring",
        "VB — Flank wear land (mm); demo limit 0.30 mm",
        "XRD — X-ray diffraction (not implemented in this B.Tech build)",
    ]
    for a in abbr:
        add_bullet(doc, a)
    doc.add_page_break()


def ch1(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 1  Introduction and ideation", 1)
    add_h(doc, "1.1 Why this project exists", 2)
    add_p(
        doc,
        "Mechanical engineering graduates are asked, more often than a decade ago, to connect a cutting process to "
        "data. Industry 4.0 documents speak of digital twins, predictive maintenance and zero-defect machining. "
        "On a real shop floor the gap is still large. A vertical machining centre already records spindle load and "
        "axis positions, but it does not tell the operator that the next thirty seconds of cutting will push Ra "
        "through the drawing limit. A profilometer tells the truth after the fact. A worn end mill tells the truth "
        "when the finish turns cloudy or the spindle note changes. The ideation of this project is therefore simple: "
        "build a monitor that sits beside the mill, consumes the same kinds of signals a laboratory can actually "
        "instrument, and raises an early, explainable warning before the surface is lost.",
    )
    add_p(
        doc,
        "The ideation is also deliberately modest. Many research papers jump from a few accelerometer traces to a "
        "deep network that claims residual stress, white-layer thickness and fatigue life. Those quantities matter "
        "in aerospace and biomedical work, but they require residual-stress measurement, metallography and a "
        "designed experiment that a single B.Tech semester rarely completes. This project therefore locks a B.Tech "
        "integrity proxy: the surface is treated as degraded when Ra exceeds the specification. Flank wear VB, "
        "wear rate, vibration, force and temperature are monitored as the physical drivers of that roughness. "
        "If the department later books XRD or a stylus campaign, the same software sockets can accept those labels. "
        "Until then the claim stays inside what the code and the simulator can support.",
    )
    add_h(doc, "1.2 The idea in one paragraph", 2)
    add_p(
        doc,
        "Treat milling as a multimodal, physics-constrained time series. Window the signals. Extract features that "
        "a manufacturing engineer already understands (RMS, chatter-band energy, power residual). Discover latent "
        "regimes without forcing the operator to name them in advance. Forecast Ra and tool state a short horizon "
        "ahead. Show the result on a shop-floor dashboard. If the operator’s typed hard-stop is crossed, request "
        "feed-hold on the visualisation mill so that the tool freezes where it is. Keep degradation probability "
        "on the screen as a risk number, not as an automatic crash stop. Train first on a physics-inspired "
        "simulator so that the pipeline is complete before the first labelled cut.",
    )
    add_h(doc, "1.3 Aim", 2)
    add_p(
        doc,
        "The aim of the project is to design, implement and demonstrate a physics-informed multimodal learning "
        "system for latent regime discovery and early surface-integrity degradation prediction in CNC end milling "
        "of aluminium alloy (default Al 6061), and to package that system as a usable shop-floor dashboard with "
        "optional linkage to a browser CNC and to serial DAQ hardware.",
    )
    add_h(doc, "1.4 Objectives", 2)
    objs = [
        "Define a process window (tool, speed, feed, depth, Ra spec) that is typical of teaching-lab aluminium milling.",
        "Build a SensorFrame contract so simulator, Arduino serial and HTTP/bridge sources look the same to the model.",
        "Extract time-domain, frequency-domain and physics-residual features from each window.",
        "Train a Gaussian mixture model to assign latent regimes A–D on simulated multimodal features.",
        "Train gradient-boosting heads for Ra, VB, wear rate, temperature and short-horizon degradation probability.",
        "Implement a supervisor with operator-set desired maxima and hard-stop limits; do not hard-stop on risk alone.",
        "Deliver a Streamlit integrity monitor with live plots, regime colour, ETA and manual override of readings.",
        "Provide a local mill bridge so Cycle start / Hold on a visualisation CNC can start and freeze the monitor.",
        "State limitations honestly: simulated labels, Ra as SI proxy, software Hold ≠ certified e-stop.",
    ]
    for o in objs:
        add_bullet(doc, o)
    add_h(doc, "1.5 Scope and what is out of scope", 2)
    add_p(
        doc,
        "In scope: Al 6061 end milling in the configured window; simulated and serial/HTTP acquisition; feature "
        "extraction; GMM regimes; HGB forecasts; dashboard; mill-cycle follow; software Hold request. Out of scope "
        "unless separately booked: XRD residual stress, microhardness maps, white-layer measurement, five-axis "
        "toolpaths, titanium or hardened steel, closed-loop override of a real Fanuc/Siemens interpolator, and "
        "any claim that the Python process is a Category-0 or Category-1 stop under machine-tool safety standards.",
    )
    add_h(doc, "1.6 Organisation of the report", 2)
    add_p(
        doc,
        "Chapter 2 places the work in the literature and in the Industry 4.0 shift. Chapter 3 states the industrial "
        "problem and the market failure of late inspection. Chapter 4 gives the methodology. Chapter 5 describes "
        "architecture. Chapter 6 records implementation of the repository the reader can run. Chapter 7 discusses "
        "simulated results and how they must be read. Chapter 8 compares the approach with fixed-time tool change, "
        "threshold TCM and pure deep learning. Chapter 9 treats industry impact and markets. Chapter 10 is future "
        "work. Chapter 11 concludes. References and appendices follow.",
    )


def ch2(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 2  Background and related work", 1)
    add_h(doc, "2.1 Surface integrity in milling", 2)
    add_p(
        doc,
        "Surface integrity is the set of geometric and metallurgical conditions left by the last cut: roughness, "
        "lay, residual stress, hardness alteration and, in severe cases, white layer or cracks. For aluminium "
        "housings, manifolds and fixtures the drawing almost always specifies Ra (and sometimes Rz). Fatigue-critical "
        "aerospace aluminium may additionally specify residual stress. In a B.Tech laboratory the instrument that "
        "is actually available is usually a portable profilometer. That is why this project uses Ra as the integrity "
        "proxy. The literature is clear that flank wear, built-up edge, chatter and thermal softening all move Ra "
        "before a catastrophic insert failure. An early-warning system that tracks those drivers is therefore a "
        "legitimate integrity project even without XRD.",
    )
    add_h(doc, "2.2 Tool-condition monitoring", 2)
    add_p(
        doc,
        "Tool-condition monitoring (TCM) is the research name for listening to the cut while it happens. Typical "
        "sensors are accelerometers on the spindle or vice, dynamometers, current transformers on the spindle "
        "motor, acoustic emission and thermocouples. Commercial units (threshold TCM) trip when a band exceeds a "
        "limit. They are good at detecting a broken tool; they are weak at saying “Ra will fail in twelve seconds.” "
        "Recent surveys of machine learning in CNC milling show that classification of wear stage, regression of "
        "VB, chatter detection and roughness prediction are now standard research tasks. Simultaneous monitoring "
        "of roughness and wear is still described as early-stage in 2025 experimental papers. Digital-twin papers "
        "add on-machine inspection and LSTM remaining-life models, with a visible gap between offline RMSE and "
        "live RMSE. This project does not claim to close that gap. It claims to assemble a complete, inspectable "
        "pipeline that a student and a shop can run, then replace the simulated labels with measured ones.",
    )
    add_h(doc, "2.3 Physics-informed learning", 2)
    add_p(
        doc,
        "A purely data-driven model will happily learn the correlation between a noisy accelerometer and a "
        "simulated Ra label. When the fixture changes, the correlation dies. Physics-informed learning adds a "
        "constraint the cut already obeys. Here the constraint is elementary cutting mechanics: spindle power "
        "should be consistent with cutting force and cutting speed, up to a roughly constant idle offset. The "
        "normalised residual of that identity is a feature. When force and power disagree, something in the "
        "sensing chain or in the process (chip jamming, sensor saturation, a wrong override) is wrong. That is "
        "useful both to the model and to the operator. It is not a finite-element residual-stress solver. It is "
        "the level of physics a B.Tech monitor can compute in 250 ms.",
    )
    add_h(doc, "2.4 Latent regimes rather than named faults", 2)
    add_p(
        doc,
        "Supervised fault libraries require someone to label “chatter”, “BUE”, “rubbing” on every window. That "
        "labelling is expensive and contested. Unsupervised mixture models find clusters in feature space and "
        "let the engineer name them afterwards. This project uses a four-component Gaussian mixture ordered by "
        "severity, presented on the dashboard as Regime A (stable cutting), B (transitional), C (unstable) and "
        "D (severe degradation). A transparent rule map exists as a stand-in before the GMM is trained. After "
        "training, the GMM is the regime head. The names are for the operator; the mathematics is clustering.",
    )
    add_h(doc, "2.5 Industry 4.0 and the shop that actually exists", 2)
    add_p(
        doc,
        "Large automotive and aerospace plants buy MTConnect or OPC-UA stacks and commercial TCM. Indian MSME "
        "job shops and college laboratories usually have a Fanuc or Siemens mill, a vice, and no budget for a "
        "Kistler dynamometer on every machine. The architecture of this project therefore accepts three sources: "
        "a physics simulator (zero hardware), an Arduino sketch (cheap DAQ), and an HTTP/bridge link to a "
        "visualisation CNC used for demonstration. That is a pedagogical and industrial choice, not a claim that "
        "the simulator replaces ISO 8688 tool-life testing.",
    )


def ch3(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 3  Problem statement, motivation and research questions", 1)
    add_h(doc, "3.1 Problem statement", 2)
    add_p(
        doc,
        "CNC end milling of aluminium produces acceptable surface integrity only inside a moving process window. "
        "Tool wear, chatter and thermal drift move that window during a single programme. Post-process Ra "
        "measurement detects the failure after the surface is already out of specification. Fixed-interval tool "
        "change wastes tool life. Threshold alarms fire too late or too often. The problem is to estimate, online, "
        "the latent regime of the cut and the short-horizon risk that Ra (and associated wear/thermal states) will "
        "cross an operator-set limit, using signals that a B.Tech laboratory can acquire, and to present the "
        "estimate so that an operator can hold the machine before the damage is complete.",
    )
    add_h(doc, "3.2 Motivation", 2)
    add_p(
        doc,
        "Motivation is both academic and economic. Academically, the project forces the student to connect "
        "manufacturing science (Taylor-type wear, cutting power, chatter bands) with a software system that "
        "another person can run. Economically, unplanned tool events and scrap from poor finish are among the "
        "largest avoidable costs in milling cells. Public market notes place tool-condition monitoring in the "
        "order of USD 1.8 billion in the mid-2020s with high single-digit to low double-digit growth, and they "
        "attribute tens of billions of dollars of annual downtime to tool-related stops. A student project does "
        "not capture that market. It can, however, show a shop what a cheap early-warning layer looks like before "
        "anyone writes a purchase order for a closed commercial stack.",
    )
    add_h(doc, "3.3 Research questions", 2)
    qs = [
        "Q1. Which compact multimodal features, including a physics residual, are sufficient to separate stable "
        "aluminium milling from transitional and severe regimes in a simulated but physically structured dataset?",
        "Q2. Can a GMM plus small gradient-boosting heads, trained only on simulated speed/feed conditions, produce "
        "dashboard behaviour that is interpretable to a mechanical engineer (regimes, Ra, VB, ETA)?",
        "Q3. How should hard-stop logic be designed so that degradation probability informs the operator without "
        "becoming a false e-stop?",
        "Q4. How can a visualisation CNC without a telemetry API still start and freeze a monitor on another laptop?",
        "Q5. What must be stated so that a thesis examiner does not confuse a simulator demo with a certified lab result?",
    ]
    for q in qs:
        add_bullet(doc, q)
    add_h(doc, "3.4 Hypothesis", 2)
    add_p(
        doc,
        "If multimodal features are constrained by a cutting-power residual and clustered by a GMM, then short-horizon "
        "Ra and wear heads will rise through identifiable regimes before a hard Ra/VB limit, and an operator-set "
        "supervisor can request Hold without treating probability itself as a trip. The hypothesis is tested in "
        "this report on simulated runs and on the integrated dashboard/bridge. Confirmation on a physical mill "
        "requires a later labelled campaign.",
    )


def ch4(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 4  Methodology", 1)
    add_h(doc, "4.1 Process window", 2)
    add_p(
        doc,
        "Unless the operator overrides the sidebar, the monitor assumes Al 6061, end milling, a 10 mm four-flute "
        "tool, 3000 r/min, 0.12 mm/tooth, 1.0 mm axial depth and an Ra specification of 1.6 µm. Cutting speed is "
        "then about 94 m/min. That is a conventional teaching-lab aluminium window: fast enough to show wear and "
        "chatter in a short demo, mild enough that a real 6061 plate would not immediately rub or weld. The "
        "simulator also trains at neighbouring speeds and feeds (2400–3600 r/min, 0.08–0.18 mm/tooth) so that the "
        "GMM sees more than one operating point.",
    )
    add_h(doc, "4.2 The SensorFrame contract", 2)
    add_p(
        doc,
        "Every source — simulator, serial Arduino, HTTP/G-code playback — must emit a SensorFrame: time, vibration "
        "window, optional force window, temperature, spindle power or current, commanded rpm and feed, and optional "
        "true Ra if a later experiment writes it. The rest of the stack never asks which source produced the frame. "
        "That is the main software idea. It is why the dashboard can be developed without a mill and later pointed "
        "at COM3 or at a bridge URL without rewriting the model.",
    )
    add_h(doc, "4.3 Feature extraction", 2)
    add_p(
        doc,
        "Each 0.25 s window at up to 5 kHz is reduced to a ten-dimensional vector used by the models: vibration RMS, "
        "kurtosis, crest factor, force RMS, force fluctuation, chatter-band energy, spectral entropy, temperature, "
        "spindle power and the physics residual. Additional quantities (tooth-pass band, peak-to-peak, current) are "
        "computed for plots. Time-domain RMS tracks energy. Kurtosis and crest factor rise when impacts or chatter "
        "spikes appear. The chatter band is the spectral region away from the tooth-passing frequency where "
        "self-excited vibration lives. Spectral entropy rises as the spectrum becomes less tonal. The physics "
        "residual is |Pmeas − (Pidle + Fc · Vc)| / max(Pmeas, 1). Together these features are the “multimodal” "
        "part of the title: they mix motion, force, thermal and energy-consistency information.",
    )
    add_fig(doc, "fig4_features.png", "Figure 4. Feature pipeline from a SensorFrame to the model heads.")
    add_h(doc, "4.4 Latent regime discovery (GMM)", 2)
    add_p(
        doc,
        "A four-component Gaussian mixture is fitted on standardised feature vectors from six simulated cutting "
        "conditions. Components are ordered so that the dashboard can name them A–D from stable to severe. The "
        "operator sees a colour and a confidence. The method is unsupervised: nobody labelled “chatter” on the "
        "training windows. After deployment, a shift from A to C is a regime discovery event — the cut has entered "
        "a different statistical neighbourhood — which is more honest than a brittle if-then fault tree, and more "
        "usable than a 128-dimensional autoencoder latent space with no names.",
    )
    add_fig(doc, "fig2_regimes.png", "Figure 2. Latent regimes along a simulated Al 6061 end-milling run.")
    add_h(doc, "4.5 Predictive heads", 2)
    add_p(
        doc,
        "Histogram-based gradient boosting (scikit-learn) is used for Ra, VB, wear rate, temperature and a "
        "classifier/regressor for short-horizon degradation probability. The models are small, train on a laptop, "
        "and remain inspectable through feature contributions on the dashboard. They are not LSTMs. For a 0.25 s "
        "window and a 30 s horizon, a boosted tree on engineered features is an appropriate B.Tech estimator. "
        "The forecast object also carries a textual recommendation and a tool-health percentage relative to the "
        "0.30 mm VB demo limit (ISO 8688-style, not a certified tool-life test of this specific insert).",
    )
    add_h(doc, "4.6 Physics in the simulator", 2)
    add_p(
        doc,
        "The simulator grows flank wear with a Taylor-type rate that increases with cutting speed, feed, chatter "
        "and current wear. Temperature is a first-order lag toward a power-and-wear steady state. Time is "
        "accelerated so a wear curve that would take minutes to hours on a real tool fits in about one minute on "
        "screen. Vibration and force traces become more impulsive as chatter and wear rise. True Ra in the "
        "simulator is a function of the same drivers, which is why the learned Ra head can look “accurate” on "
        "simulated data. That accuracy is not transferable to the laboratory until measured Ra is logged.",
    )
    add_fig(doc, "fig3_wear.png", "Figure 3. Taylor-type flank-wear growth used in the physics simulator.")
    add_h(doc, "4.7 Supervisor and hard-stop ethics", 2)
    add_p(
        doc,
        "The supervisor compares live Ra, VB, wear rate, temperature, vibration RMS and force RMS with the "
        "operator’s typed desired maxima and hard-stop values. Degradation probability is displayed and may be "
        "used for alerts, but in the delivered dashboard it is not an armed hard-stop. That decision came from "
        "the demonstration itself: risk often sat in the 70–90 % band while the physical cut was still useful. "
        "Tripping on probability emptied the demo and trained the operator to ignore the system. Hard-stop "
        "therefore stays on quantities an inspector could later measure. When a hard-stop fires, the monitor "
        "requests software Hold on the bridged mill so the tool freezes at the current pose rather than returning "
        "to programme origin. That Hold is not an e-stop.",
    )


def ch5(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 5  System architecture", 1)
    add_h(doc, "5.1 Layers", 2)
    add_p(
        doc,
        "The repository is layered so that a change in sensors does not rewrite the user interface. Acquisition "
        "implements SensorSource. Processing turns a frame into FeatureVector. The AdvancedMonitor holds the GMM "
        "and boosting heads. The supervisor emits a ControlDecision. The Streamlit app is only a view and a place "
        "to type limits. The CNC bridge is a separate process: it proxies a browser mill, injects a cycle hook, "
        "and exposes /bridge/status and /bridge/event on port 8766.",
    )
    add_fig(doc, "fig1_architecture.png", "Figure 1. End-to-end architecture of the machining integrity monitor.")
    add_h(doc, "5.2 Why a browser mill is in a mechanical project", 2)
    add_p(
        doc,
        "A second laptop in the laboratory ran a ForgeMill visualisation hosted on Vercel. That mill has Cycle "
        "start, Hold, Stop, DRO and an Iso/Top toolpath view. It has no official telemetry API. HTTPS pages cannot "
        "call http://localhost on the monitor laptop (mixed content). The engineering answer used here is a local "
        "reverse proxy on the monitor PC: the CNC laptop opens http://<monitor-LAN>:8766/, which serves the mill "
        "plus a small hook. Cycle start sets the bridge running flag; the Streamlit app starts the simulator; "
        "hard-stop posts want_hold; the hook clicks Hold so the pose freezes. The raw vercel.app URL cannot receive "
        "Hold from this PC. That constraint is architectural, not cosmetic.",
    )
    add_h(doc, "5.3 Data paths", 2)
    add_p(
        doc,
        "Path A — Simulator only: press Start run on the dashboard. Path B — Serial: flash firmware/arduino_daq.ino, "
        "select COM port. Path C — HTTP/bridge: config source = http, leave the monitor open, press Cycle start on "
        "the hooked mill. All three paths end in infer() and the same plots. That is the architecture test: if the "
        "examiner changes only config.yaml, the thesis story does not collapse.",
    )
    add_h(doc, "5.4 Human–machine interface", 2)
    add_p(
        doc,
        "The dashboard language is shop language: STABLE, WATCH, SURFACE RISK; regimes A–D; Ra in micrometres; VB "
        "in millimetres; temperature in Celsius; a refresh control that actually reruns the script; optional typed "
        "“my measured values” so a student can overlay a profilometer reading. Plots use a dark shop-floor theme. "
        "The point of the HMI is not novelty. It is that a mechanical supervisor can read it without opening a notebook.",
    )


def ch6(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 6  Implementation of the present repository", 1)
    add_h(doc, "6.1 Repository map", 2)
    add_p(
        doc,
        "dashboard/app.py is the Streamlit monitor. src/acquisition holds the simulator, serial source, HTTP source, "
        "G-code playback helpers, cycle-signal reader and bridge client. src/processing/features.py is the feature "
        "extractor. src/ml/model.py is the GMM and HGB ensemble. src/ml/physics.py is the power residual. "
        "src/control/supervisor.py is decide() and eta_seconds(). scripts/train_monitor.py retrains on simulated "
        "runs. scripts/cnc_bridge.py is the mill proxy. firmware/arduino_daq.ino is the cheap DAQ sketch. "
        "config.yaml is the process window. models/ stores the fitted monitor.",
    )
    add_h(doc, "6.2 Training protocol (simulated)", 2)
    add_p(
        doc,
        "Training walks six (rpm, feed, seed) conditions, extracts windows, fits StandardScaler + GMM(4) and "
        "separate HGB pipelines for wear, rate, Ra, temperature and risk. The trained_on string stored with the "
        "model states that the data are physics-simulated. That string should appear in any demonstration to an "
        "examiner. Replacing the dataset is a one-function change once CSV logs of real Ra and microscope VB exist.",
    )
    add_h(doc, "6.3 Dashboard behaviour implemented", 2)
    add_p(
        doc,
        "On Cycle start (bridge or button) the monitor begins a run, stores history deques, updates metrics every "
        "refresh interval, computes ETA to each armed hard-stop, and lists approaching limits. Operator Stop and "
        "automatic hard-stop call halt_run(), snapshot X/Y/Z, and optionally post want_hold. Programme end or Hold "
        "off stops the simulator without an extra Hold click. Manual limits are always visible; “use this limit” "
        "checkboxes were removed so that a missed tick cannot silently disarm a stop. Risk remains on the plot, "
        "not on the trip list.",
    )
    add_h(doc, "6.4 Bridge behaviour implemented", 2)
    add_p(
        doc,
        "The bridge binds 0.0.0.0:8766, fetches the Vercel mill with identity encoding, caches static chunks in "
        "memory, injects a cycle/Hold hook, and can patch mill JavaScript so that a dashboard Hold request becomes "
        "a true feed-hold (tool stays at interpolated pose) rather than Stop (which in ForgeMill resets progress "
        "and snaps DRO to the home pose). Serving the mill through HTTP on the LAN is what makes Hold possible. "
        "The hook must not flood the proxy with per-frame pose posts; that was observed to freeze the mill tab and "
        "was corrected. Cursor’s built-in preview is not a reliable CNC browser; Chrome or Edge on the LAN URL is "
        "the intended client.",
    )
    add_h(doc, "6.5 Safety wording that belongs in the implementation chapter", 2)
    add_p(
        doc,
        "Every release of this software should keep three sentences in the UI or the report: (1) simulated training "
        "is not a lab result; (2) Ra is the B.Tech SI proxy; (3) software Hold is not a certified e-stop. Those "
        "sentences are part of the implementation quality, not an apology after the fact.",
    )


def ch7(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 7  Results and how they must be read", 1)
    add_h(doc, "7.1 What the demo shows", 2)
    add_p(
        doc,
        "On a typical simulator run the dashboard moves from STABLE to WATCH to SURFACE RISK. Regime colour walks "
        "A → B → C → D. Predicted Ra approaches 1.6 µm. VB climbs toward 0.30 mm. Temperature lags power. "
        "Degradation probability rises earlier than the Ra trace, which is exactly what an early-warning head is "
        "for — and exactly why it must not be the e-stop. When a typed hard-stop is crossed, the run halts and, "
        "if the mill is bridged, Hold is requested. Feature-contribution bars usually light vibration, chatter-band "
        "energy, force and the physics residual, which matches the story a manufacturing lecturer would tell.",
    )
    add_h(doc, "7.2 What the demo does not show", 2)
    add_p(
        doc,
        "It does not show a confusion matrix on profilometer Ra. It does not show a wear-land photograph. It does "
        "not show residual stress. It does not show that the GMM components found on the simulator are the same "
        "components a physical 6061 campaign would find. Anyone using Chapter 7 as a results chapter in a journal "
        "sense is misusing it. The correct use is: the pipeline is complete, the HMI is usable, the failure modes "
        "of Hold-versus-Stop and probability-versus-hard-stop were found in software, and the next experiment is "
        "well defined.",
    )
    add_h(doc, "7.3 Qualitative observations from integration", 2)
    add_p(
        doc,
        "Several engineering facts appeared only when the mill and the monitor were connected. ForgeMill Stop "
        "resets programme progress, so a “stop” that is implemented as Stop looks like a return to origin. Hold "
        "freezes the interpolator pose. A pose post on every animation frame can stall a threaded Python proxy. "
        "Reading the word “Hold” from the Hold button and treating it as machine state makes the bridge think the "
        "mill is always in feed-hold. HTTPS cannot phone home to HTTP. Cursor’s simple browser draws buttons but "
        "does not reliably run the canvas or click handlers. Those observations are results of systems engineering. "
        "They belong in a B.Tech report because they are what a digital-manufacturing project actually spends time on.",
    )
    add_h(doc, "7.4 Repeatability of the software experiment", 2)
    add_p(
        doc,
        "Any examiner with Python 3 and the requirements file can recreate the simulated figures by running the "
        "dashboard and Start run, or by calling MONITOR.train() and a short SimulatedMillingSource loop. That "
        "repeatability is a strength. It is also a temptation to skip the laboratory. The report therefore treats "
        "reproducible simulation as a necessary but not sufficient condition for a manufacturing thesis.",
    )


def ch8(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 8  Why this is better than common alternatives", 1)
    add_h(doc, "8.1 Fixed-time tool change", 2)
    add_p(
        doc,
        "Changing an end mill every N parts is easy to audit and wasteful. Tools that are still in Regime A are "
        "thrown away. Tools that entered Regime D early still cut scrap until the clock expires. The present "
        "system does not abolish planned tool change. It adds a reason to deviate: if VB and Ra forecasts stay "
        "flat, keep the tool; if Regime C appears with a short ETA to the Ra stop, stop the cycle and inspect. "
        "That is a better use of a carbide mill than a calendar.",
    )
    add_h(doc, "8.2 Threshold TCM", 2)
    add_p(
        doc,
        "Commercial threshold boxes are mature and should be used for breakage and collision. They are not early "
        "surface-integrity predictors. They have no latent regime, no Ra head, no physics residual, and no notion "
        "of a 30 s horizon. This project is complementary: a cheap analytical layer above, not a replacement of, "
        "a hardware trip.",
    )
    add_h(doc, "8.3 Pure deep learning without physics or HMI", 2)
    add_p(
        doc,
        "A large network trained on someone else’s PHM dataset can win a paper metric and still be unusable on a "
        "college mill: no SensorFrame, no serial path, no operator limits, no Hold semantics, no honesty about "
        "labels. This project inverts that priority. The model is small on purpose. The sockets and the safety "
        "wording are large on purpose. For a B.Tech mechanical audience that inversion is an advantage, not a lack "
        "of sophistication.",
    )
    add_h(doc, "8.4 Papers that promise residual stress without a diffractometer", 2)
    add_p(
        doc,
        "The literature sometimes infers residual stress from vibration. That can be a research goal if XRD is in "
        "the experimental plan. It is not better science to print the word “integrity” and mean residual stress "
        "when the only instrument is a dashboard. This project is better than those claims because it refuses them. "
        "Integrity here means Ra-proxy plus wear and thermal drivers, until the lab book says otherwise.",
    )
    add_fig(doc, "fig5_compare.png", "Figure 5. Positioning against common shop-floor strategies (qualitative).")
    add_h(doc, "8.5 What “better” means for a buyer", 2)
    add_p(
        doc,
        "For a job shop, better means: runs on a laptop, accepts a ₹-level Arduino path, explains itself in "
        "micrometres and millimetres, does not silently stop the machine because a probability flickered, and can "
        "be shown to a customer as a process-control story. For a college, better means: a student can defend every "
        "block of the diagram on a whiteboard. For a researcher, better means: the place to insert a real dataset "
        "is obvious.",
    )


def ch9(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 9  Industry impact, markets and who is helped", 1)
    add_h(doc, "9.1 How the industry actually loses money", 2)
    add_p(
        doc,
        "Milling cells lose money in four boring ways: scrap and rework when Ra or dimension fails; unplanned stops "
        "when a tool breaks or a chatter mark forces a re-cut; wasted tool life from conservative change-out; and "
        "idle spindles while a quality engineer walks a part to a metrology room. Industry notes compiled for this "
        "report place global tool-condition monitoring around USD 1.8 billion in the mid-2020s, with published "
        "CAGR figures in the roughly 9–12 % range depending on the analyst, and they associate tens of billions of "
        "dollars of annual downtime with tool-related disruption. Those figures are market context, not a revenue "
        "forecast for this repository. They explain why a mechanical project on early warning is not a toy theme.",
    )
    add_fig(doc, "fig6_market.png", "Figure 6. Indicative TCM market trajectory compiled from public forecasts.")
    add_h(doc, "9.2 Sectors that feel an early Ra/VB warning", 2)
    add_p(
        doc,
        "Automotive tier suppliers mill aluminium housings and brackets at volume; a late Ra fail is a line stop. "
        "Aerospace and defence machine 6061 and 7075 structures where documentation of process control is part of "
        "the contract. Die-mould shops care about finish because polishing time is labour. Medical and semiconductor "
        "equipment shops are moving tolerances down, which turns TCM from a cost toy into a quality gate. College "
        "and MSME shops are the near-term users of this exact stack: they will not buy a full digital twin, but they "
        "will run a laptop beside a mill if it speaks Ra and VB.",
    )
    add_h(doc, "9.3 How this project helps those markets", 2)
    add_p(
        doc,
        "It helps as a specification of a minimum viable integrity layer: which signals, which features, which "
        "heads, which human limits, which Hold semantics. A vendor can productise a sturdier version. A plant can "
        "use the architecture to write an internal brief. A student company can offer dashboard-plus-Arduino "
        "installations to local job shops as a service, provided they never market software Hold as a safety PLC. "
        "The market help is therefore architectural and educational first, commercial second.",
    )
    add_h(doc, "9.4 Future industrial impacts if the lab campaign is completed", 2)
    add_p(
        doc,
        "If measured Ra and VB replace simulated labels, the same HMI becomes a candidate in-process capability "
        "study: show that Regime C predicts a failed Ra coupon with a stated false-alarm rate. That would justify "
        "keeping a tool one batch longer, or pulling a tool one batch earlier, with a quality record. If MTConnect "
        "or a real interpolator feed-hold is later wired, the supervisor could become a process interlock under "
        "a safety review — still not an e-stop, but a documented hold. If multiple machines share a regime model, "
        "plants get a common language (“we are seeing B-to-C shifts on mill 4 after lunch”) instead of tribal "
        "operator lore. Those are the future impacts worth writing down. They are conditional on data and on "
        "safety engineering that this B.Tech build does not pretend to have finished.",
    )
    add_h(doc, "9.5 Sustainability and material efficiency", 2)
    add_p(
        doc,
        "Aluminium scrap is recyclable but not free: energy, logistics and schedule are lost when a plate is "
        "re-cut. Carbide tools have embodied energy and cobalt supply constraints. Using a tool to the last safe "
        "VB, and not past the Ra cliff, is a sustainability argument as well as a cost argument. The project’s "
        "wear-rate head exists for that reason. It is better to plot micrometres per second than to guess.",
    )
    add_h(doc, "9.6 India-specific shop-floor fit", 2)
    add_p(
        doc,
        "India’s machining MSMEs are numerous, price-sensitive and increasingly asked for documented quality by "
        "export customers. A Python monitor that can start on a used PC and grow into NI-DAQ is a better first "
        "step than a six-figure foreign TCM installation. The project’s bilingual reality — English dashboard, "
        "shop Hindi/English operator talk — is left to deployment. The technical fit is: serial first, Ethernet "
        "later, no requirement that the CNC vendor open a proprietary protocol on day one.",
    )
    add_h(doc, "9.7 Competitive position, honestly", 2)
    add_p(
        doc,
        "This software will not out-perform a well-tuned Marposs/ARTIS or Caron TMAC unit on breakage detection. "
        "It should not be sold as if it would. Its competitive position is early, cheap, multimodal, "
        "physics-annotated, regime-aware roughness warning with an honest SI proxy. That niche is empty on most "
        "college mills and many job shops. Filling an empty niche is a market contribution even when the code is "
        "not a product.",
    )


def ch10(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 10  Future work", 1)
    add_p(
        doc,
        "The next twelve months of a serious continuation are not “add transformers.” They are measurement. Book "
        "a factorial on Al 6061: two speeds, two feeds, two worn states of the same four-flute mill. Log vibration, "
        "current and temperature. Measure Ra on a profilometer after each pass. Photograph VB. Retrain MONITOR "
        "on those labels. Report precision and recall for the Ra-spec event, and calibration of the probability "
        "head. Only then discuss residual stress, and only if XRD time is actually reserved.",
    )
    add_p(
        doc,
        "Software futures that are worth doing after labels exist: an NI-DAQmx source behind the same SensorFrame; "
        "MTConnect spindle-load as a power proxy; a documented Hold via the real controller’s feed-hold bit under "
        "a safety review; a simple digital thread that stores regime traces with the job card; and a comparison "
        "against a threshold-only baseline on the same cuts. Software futures that are not worth doing first: "
        "generative G-code, reinforcement-learning feed override on an unguarded mill, or a public claim of "
        "certified e-stop.",
    )
    add_p(
        doc,
        "Pedagogical futures: freeze this dashboard as a laboratory station where juniors must explain why Regime "
        "C appeared, and must write the three safety sentences from memory. That may be a larger impact than any "
        "single RMSE.",
    )


def ch11(doc):
    doc.add_page_break()
    add_h(doc, "Chapter 11  Conclusion", 1)
    add_p(
        doc,
        "This B.Tech project started from a clear industrial irritation: surface-integrity failure in aluminium "
        "milling is usually discovered too late. It turned that irritation into a complete, runnable system. "
        "Multimodal features, a physics residual, latent GMM regimes and small boosting heads feed a shop-floor "
        "dashboard. A supervisor respects operator-typed physical limits and refuses to treat degradation "
        "probability as an e-stop. A mill bridge shows how a visualisation CNC without an API can still start "
        "and freeze a monitor. Training is simulated; integrity is an Ra proxy; Hold is software. Those constraints "
        "are the scientific character of the work, not its failure. The ideation, the aim, the comparison with "
        "weaker shop practices, and the market story all point the same way: early, explainable, physically "
        "grounded warning is more valuable than late inspection or opaque scores — provided nobody confuses a "
        "laptop with a safety PLC. The industry impact, if the laboratory campaign is done, is longer tool life, "
        "less scrap, and a common language for “the cut has left the stable regime.” That is enough ambition for "
        "a mechanical B.Tech, and it is an honest one.",
    )


def refs(doc):
    doc.add_page_break()
    add_h(doc, "References", 1)
    items = [
        "ISO 8688-1/2. Tool life testing in milling. International Organization for Standardization.",
        "ISO 4287 / ISO 21920. Geometrical product specifications — Surface texture (Ra conventions).",
        "Kalpakjian, S. and Schmid, S.R. Manufacturing Engineering and Technology. Pearson. (Cutting power, tool wear.)",
        "Altintas, Y. Manufacturing Automation: Metal Cutting Mechanics, Machine Tool Vibrations, and CNC Design. Cambridge University Press.",
        "Tlusty, J. Manufacturing Processes and Equipment. Prentice Hall. (Chatter and stability.)",
        "Taylor, F.W. On the art of cutting metals. Trans. ASME, 1907. (Tool-life form used qualitatively in the simulator.)",
        "Survey on machine learning applied to CNC milling processes. Advances in Manufacturing, 2025. https://link.springer.com/article/10.1007/s40436-025-00564-x",
        "A novel simultaneous monitoring method for surface roughness and tool wear in milling process. Scientific Reports, 2025. https://www.nature.com/articles/s41598-025-92178-3",
        "Intelligent real-time tool life prediction for a digital twin framework. Journal of Intelligent Manufacturing, 2025. https://link.springer.com/article/10.1007/s10845-025-02606-4",
        "Dataintelo. Tool Condition Monitoring Market Size, Share & Forecast Report 2025 to 2034. Market context only.",
        "Market Research Reports. Global Predictive Tool Wear Monitoring Analytics Market Strategic Research Report. Market context only.",
        "scikit-learn documentation. GaussianMixture; HistGradientBoostingRegressor/Classifier.",
        "Streamlit documentation. Used for the shop-floor user interface.",
        "Project repository: dashboard/app.py; src/ml/model.py; src/acquisition/simulator.py; src/control/supervisor.py; scripts/cnc_bridge.py; config.yaml.",
    ]
    for i, it in enumerate(items, 1):
        add_p(doc, f"[{i}]  {it}", first_line=False, space_after=6)


def appendix(doc):
    doc.add_page_break()
    add_h(doc, "Appendix A  Default process parameters", 1)
    add_p(
        doc,
        "Material Al 6061; operation end milling; tool diameter 10 mm; teeth 4; spindle 3000 r/min; feed 0.12 mm/tooth; "
        "depth of cut 1.0 mm; Ra specification 1.6 µm; sample rate 5000 Hz; window 0.25 s; dashboard refresh 400 ms; "
        "forecast horizon 30 s; VB demo limit 0.30 mm. Source in config.yaml may be simulator, serial or http.",
        first_line=False,
    )
    add_h(doc, "Appendix B  How to run the demonstration", 1)
    add_p(
        doc,
        "Install Python 3, pip install -r requirements.txt, then: python -m streamlit run dashboard/app.py --server.port 8501. "
        "Optionally run python scripts/cnc_bridge.py and open http://127.0.0.1:8766/ in Chrome or Edge (not an IDE preview). "
        "Press Cycle start on the mill or Start run on the monitor. Serial mode requires the Arduino firmware and a COM port.",
        first_line=False,
    )
    add_h(doc, "Appendix C  Feature list used by the models", 1)
    add_p(
        doc,
        "Vibration RMS; kurtosis; crest factor; force RMS; force fluctuation; chatter-band energy; spectral entropy; "
        "temperature; spindle power; physics residual. These ten numbers are FEATURE_NAMES in src/ml/model.py.",
        first_line=False,
    )
    add_h(doc, "Appendix D  Extended discussion: what “ideation” meant week by week", 1)
    add_p(
        doc,
        "The first idea was a live roughness meter. That idea died when it became obvious that Ra is not a live "
        "sensor. The second idea was a chatter alarm. That idea was too thin for a B.Tech title and too close to "
        "a threshold box. The third idea was a full residual-stress twin. That idea was dishonest without XRD. "
        "The fourth idea — the one that survived — was latent regimes plus early Ra/wear warning plus a dashboard "
        "a shop can read, trained first on a simulator. Integration with a browser CNC was added so that “Cycle "
        "start” is a real human event, not a Streamlit button pretending to be a machine. Each discarded idea left "
        "a constraint in the code: no fake XRD, no probability e-stop, no Stop-as-Hold, no mixed-content fetch.",
    )
    add_p(
        doc,
        "That history is included because examiners sometimes ask “why this architecture?” The answer is not that "
        "GMM is fashionable. The answer is that every more glamorous architecture failed a constraint that a "
        "mechanical project must keep: measurable quantities, runnable software, and sentences that remain true "
        "when the mill is real.",
    )
    add_h(doc, "Appendix E  Extended industry scenarios", 1)
    add_p(
        doc,
        "Scenario 1 — Teaching laboratory. Twenty students share one mill. The monitor runs on a side PC. Each "
        "pair must capture a screenshot of regime colour and predicted Ra at the end of their pass and staple it "
        "to the job card. The learning outcome is not a better insert; it is that surface integrity has precursors.",
    )
    add_p(
        doc,
        "Scenario 2 — MSME aluminium job shop. One owner-operator, two VMCs, no metrology room. An Arduino on the "
        "spindle housing and the dashboard on an old PC. Tools are changed when Regime C repeats, not when the "
        "box of inserts feels light. Scrap from cloudy finish drops; insert consumption may rise or fall depending "
        "on how conservative the old habit was. The owner is told, in writing, that Hold is not e-stop.",
    )
    add_p(
        doc,
        "Scenario 3 — Tier-1 automotive. The architecture is used only as a specification to brief a vendor: we "
        "want regimes, Ra heads, operator limits, and an audit log. The vendor supplies a CE-marked stack. This "
        "project has done its job if that brief is shorter and clearer than it would have been.",
    )
    add_p(
        doc,
        "Scenario 4 — Research continuation. A master’s student inherits the SensorFrame and throws away the "
        "simulated labels. The contribution becomes a calibrated probability of Ra-spec failure on 6061 with a "
        "stated sensor set. That paper can cite this B.Tech report as the platform, not as the result.",
    )
    add_h(doc, "Appendix F  Risk register (project, not machine safety)", 1)
    add_p(
        doc,
        "Risk: examiner treats plots as lab data. Mitigation: trained_on string and Chapter 7 wording. Risk: "
        "operator treats Hold as e-stop. Mitigation: UI caption and this report. Risk: mill tab freezes from "
        "pose flood. Mitigation: throttled hook, single proxy process. Risk: mixed content blocks start signal. "
        "Mitigation: LAN HTTP mill URL, not raw HTTPS Vercel. Risk: GMM components uninterpretable on real data. "
        "Mitigation: keep the rule-based stand-in until clusters are named from chips and Ra coupons.",
        first_line=False,
    )
    add_h(doc, "Appendix G  Glossary for mixed mechanical–CS readers", 1)
    add_p(
        doc,
        "Regime: a recurring neighbourhood in feature space, not necessarily a named fault. Horizon: the number "
        "of seconds ahead the probability head is asked to look (30 s in config). Hard-stop: a typed physical "
        "limit that halts the demo run. Feed-hold: interpolator freeze at current pose. E-stop: a safety-rated "
        "power removal path this project does not implement. Physics residual: disagreement between measured "
        "power and force–speed prediction. Latent: not directly labelled by a human in the training set.",
        first_line=False,
    )
    add_h(doc, "Appendix H  Statement for the viva", 1)
    add_p(
        doc,
        "If asked “Did you predict residual stress?” the answer is no. If asked “Did you stop a certified CNC?” "
        "the answer is no. If asked “What did you build that a paper PDF cannot replace?” the answer is a running "
        "monitor with a SensorFrame, a GMM, physical limits, and a mill hook whose failure modes you can explain. "
        "If asked “What will you do next week if you get lab time?” the answer is measure Ra and VB and retrain. "
        "That viva script is the project’s intellectual property as much as the Python is.",
        first_line=False,
    )


def extra_depth(doc):
    """Extra chapters to push length and academic depth without inventing lab claims."""
    doc.add_page_break()
    add_h(doc, "Chapter 1A  (continued) Socio-technical ideation", 1)
    add_p(
        doc,
        "Ideation in an engineering college is often treated as a poster sentence. In this project it was a series "
        "of constraints negotiated with the machine, the calendar and the examiner. The machine constraint: a "
        "teaching CNC is not a research instrument until sensors exist. The calendar constraint: a B.Tech year "
        "cannot include a full residual-stress campaign unless the diffractometer is booked on day one. The "
        "examiner constraint: a mechanical thesis that is only a Jupyter notebook will be asked where the process "
        "is. The surviving idea sits on all three constraints at once. That is why the title is long. Every clause "
        "in the title is a promise that the code actually keeps: physics-informed (power residual), multimodal "
        "(vibration, force, power, temperature, overrides), latent regime discovery (GMM), early (horizon "
        "probability and ETA), surface-integrity degradation (Ra proxy), CNC milling, aluminium alloy (6061).",
    )
    add_p(
        doc,
        "A shorter title such as “AI CNC” would have been easier to print and harder to defend. The long title "
        "is a feature. It stops the project from drifting into a chatbot that writes G-code, or a vision model "
        "that looks at chips, or a reinforcement learner that twists feed on a machine nobody has risk-assessed.",
    )
    doc.add_page_break()
    add_h(doc, "Chapter 2A  (continued) Mechanics the models are allowed to see", 1)
    add_p(
        doc,
        "Tooth-passing frequency is rpm × teeth / 60. For 3000 r/min and four flutes that is 200 Hz. Chatter, if "
        "it appears, is usually not exactly at that line. The feature extractor therefore keeps a tooth band and "
        "a chatter band separate. Kurtosis is used because a Gaussian vibration cloud becoming spiky is one of "
        "the earliest cheap signs that the cut is no longer a stationary rub. Crest factor does similar work with "
        "less sensitivity to sample size. None of these features is new. The contribution is to keep them, to "
        "refuse to drown them in an uninterpreted embedding, and to add one mechanics residual that a lecturer "
        "can write on the board in one line.",
    )
    add_p(
        doc,
        "Flank wear VB is the land on the clearance face. ISO 8688 discusses 0.3 mm as a common average-wear "
        "criterion in milling tool-life tests. The simulator uses 0.30 mm as 100 % tool health for the demo. That "
        "is a convention, not a measurement of the physical insert in the lab drawer. Wear rate is the time "
        "derivative the operator never sees on a tool card and always pays for. Temperature is not the shear-zone "
        "temperature; it is a lagged bulk/sensor temperature the Arduino can copy with an LM35. Mixing these "
        "scales on one dashboard is intentional. The operator thinks in several units at once. The software should too.",
    )
    doc.add_page_break()
    add_h(doc, "Chapter 4A  (continued) Learning details", 1)
    add_p(
        doc,
        "StandardScaler is fit on the training cloud so that temperature in Celsius and chatter energy in arbitrary "
        "units do not dominate the GMM by unit choice. HistGradientBoosting is chosen over a deep net because it "
        "handles mixed scales, trains in seconds, and supports a straightforward contribution story. A mixture of "
        "experts or a neural ODE would be a different thesis. Four GMM components is a design choice matching the "
        "four named regimes. Three components collapsed stable and transitional; five split severe into two "
        "unnamed shards on the simulated cloud. Four survived. On real data that number must be re-chosen with "
        "BIC/silhouette and with a cutting-teacher in the room, not with a default from this report.",
    )
    add_p(
        doc,
        "Class imbalance is structural: most windows are stable. The risk head therefore sees a horizon label "
        "(will Ra or VB cross inside Δt?) rather than “is this millisecond a failure.” That is the early-warning "
        "trick. It is also why probability can be high while the current Ra is still legal. The supervisor’s "
        "refusal to trip on that probability is the corresponding safety trick.",
    )
    doc.add_page_break()
    add_h(doc, "Chapter 5A  (continued) Networking facts that affected the science", 1)
    add_p(
        doc,
        "It is unusual to put TLS mixed-content and HTTP proxies in a mechanical report. They are here because they "
        "decided whether Cycle start was an experimental factor or a wish. A visualisation mill on HTTPS cannot "
        "tell an HTTP monitor that the cycle began, unless a hook lives on the mill page. The hook requires either "
        "a change to the Vercel deployment (not available from the monitor laptop) or a proxy that injects the hook. "
        "The proxy then becomes part of the experimental apparatus. Treating it as “just IT” would have left the "
        "project with two dead browsers and a story about signals that never arrived. The scientific moral is that "
        "in-process monitoring includes the path the process event takes to the model.",
    )
    doc.add_page_break()
    add_h(doc, "Chapter 8A  (continued) Comparison table in prose", 1)
    add_p(
        doc,
        "Fixed-time change: low capital, high tool cost, no integrity forecast. Threshold TCM: medium capital, "
        "excellent breakage catch, poor Ra forecast, no regimes. Vision-only finish inspection: post-process, "
        "good for audit photographs, late. Deep PHM on public datasets: high paper metrics, weak transfer, weak "
        "HMI. Commercial digital twins: high capital, high integration time, strong if the vendor is already in "
        "the plant. This project: low capital, complete HMI, physics residual, regimes, simulated labels, no "
        "safety rating. The last two rows of that table are why the project is better for a college and not yet "
        "better for a certified cell.",
    )
    doc.add_page_break()
    add_h(doc, "Chapter 9A  (continued) Market mechanisms", 1)
    add_p(
        doc,
        "Markets do not buy “GMM.” They buy fewer customer returns, fewer night-shift surprises, and a story they "
        "can tell an auditor. The monitor helps those mechanisms if its false-alarm rate is low enough that the "
        "night shift does not disable it. That is a product-management sentence with a technical core: calibrate "
        "the probability head, keep hard-stops on physical units, log every Hold. The future market impact of "
        "student projects like this is to normalise that sentence in mechanical curricula so that graduates do "
        "not treat Industry 4.0 as a poster and TCM as a black box purchased from abroad.",
    )
    add_p(
        doc,
        "A secondary market is education technology: packaged labs that sell a mill, an accelerometer, and this "
        "style of dashboard as one SKU. The ethical requirement for that SKU is the same three-sentence disclaimer. "
        "A tertiary market is insurance and tool-vendor service contracts: if wear-rate traces become trustworthy, "
        "insert suppliers can sell “tools as a service.” This project does not implement that contract. It shows "
        "the telemetry such a contract would need.",
    )


def main():
    doc = setup_doc()
    cover(doc)
    front_matter(doc)
    contents_page(doc, add_h, add_p, add_bullet)
    ch1(doc)
    extra_depth(doc)
    ch2(doc)
    extra_literature(doc, add_h, add_p, add_bullet)
    ch3(doc)
    ch4(doc)
    ch5(doc)
    ch6(doc)
    ch7(doc)
    ch8(doc)
    ch9(doc)
    ch10(doc)
    ch11(doc)
    ch12(doc, add_h, add_p, add_bullet, add_fig)
    ch13(doc, add_h, add_p, add_bullet, add_fig, add_table, set_run_font)
    ch14(doc, add_h, add_p, add_bullet, add_fig, add_table, set_run_font)
    ch15(doc, add_h, add_p, add_bullet, add_fig, add_table, set_run_font)
    refs(doc)
    appendix(doc)
    extra_closing_pages(doc, add_h, add_p, add_bullet)
    doc.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
