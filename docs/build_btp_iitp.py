"""IIT Patna MED B.Tech Project Report — formatted to the official template."""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor, Twips, Cm, Emu

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
LOGO = ROOT / "template_assets" / "image1.png"
OUT = ROOT / "BTP_IITP_MED_Report.docx"

TITLE = (
    "Physics-Informed Multimodal Learning for Latent Regime Discovery and "
    "Early Surface-Integrity Degradation Prediction in CNC Milling of Aluminum Alloy"
)
STUDENT = "Rajshekhar"
STUDENT2 = "Piyush Jatoliya"
STUDENTS = f"{STUDENT} and {STUDENT2}"
SUPERVISOR = "Dr. Mahavir Singh"
MONTH_YEAR = "October, 2026"


def set_run(run, name="Times New Roman", size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    run._element.rPr.rFonts.set(qn("w:ascii"), name)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    else:
        run.font.color.rgb = RGBColor(0x00, 0x00, 0x00)


def _p(doc, text="", *, font="Times New Roman", size=12, bold=False, italic=False,
       align="justify", first_indent=False, space_before=0, space_after=0,
       line=1.5, style=None):
    p = doc.add_paragraph(style=style) if style else doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE if line == 1.5 else WD_LINE_SPACING.SINGLE
    if line == 1.5:
        pf.line_spacing = 1.5
    pf.first_line_indent = Inches(0.5) if first_indent else Inches(0)
    p.alignment = {
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }[align]
    if text:
        r = p.add_run(text)
        set_run(r, name=font, size=size, bold=bold, italic=italic)
    return p


def body(doc, text, first=False):
    return _p(doc, text, first_indent=not first, space_before=0, space_after=0)


def gap(doc):
    return _p(doc, "", space_after=0, space_before=0)


def chapter_title(doc, number, name, new_page=True):
    if new_page:
        doc.add_page_break()
    _p(doc, f"Chapter {number}", font="Book Antiqua", size=22, bold=True, align="left",
       space_before=12, space_after=6)
    p = doc.add_paragraph(style="Heading 1")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(f"{number}  {name}")
    set_run(r, "Book Antiqua", 18, bold=True)
    gap(doc)


def section(doc, text):
    gap(doc)
    p = doc.add_paragraph(style="Heading 2")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(text)
    set_run(r, "Times New Roman", 16, bold=True)
    gap(doc)


def subsection(doc, text):
    gap(doc)
    p = doc.add_paragraph(style="Heading 3")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    set_run(r, "Times New Roman", 14, bold=True)
    gap(doc)


def unnumbered_head(doc, text):
    doc.add_page_break()
    p = doc.add_paragraph(style="Heading 1")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run(text)
    set_run(r, "Book Antiqua", 18, bold=True)
    gap(doc)


def bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    if p.runs:
        p.runs[0].text = text
        set_run(p.runs[0], "Times New Roman", 12)
    else:
        r = p.add_run(text)
        set_run(r, "Times New Roman", 12)


def add_figure(doc, name, caption):
    gap(doc)
    path = FIG / name
    if path.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(0)
        p.add_run().add_picture(str(path), width=Inches(5.8))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(4)
    cap.paragraph_format.space_after = Pt(8)
    cap.paragraph_format.line_spacing = 1.0
    r = cap.add_run(caption)
    set_run(r, "Times New Roman", 12, bold=False)
    gap(doc)


def add_table(doc, caption, headers, rows):
    gap(doc)
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(6)
    cap.paragraph_format.space_after = Pt(6)
    cap.paragraph_format.line_spacing = 1.0
    r = cap.add_run(caption)
    set_run(r, "Times New Roman", 12, bold=True)
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.0
        rr = p.add_run(h)
        set_run(rr, "Times New Roman", 10, bold=True)
        rr.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        tcpr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "1F4E79")
        shd.set(qn("w:val"), "clear")
        tcpr.append(shd)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            rr = p.add_run(str(val))
            set_run(rr, "Times New Roman", 10)
    gap(doc)
    return table


def add_page_field(paragraph):
    run = paragraph.add_run()
    set_run(run, "Times New Roman", 12)
    r = run._r
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "end")
    r.append(fld1)
    r.append(instr)
    r.append(fld2)


def set_page_format(section, fmt="decimal", start=None, show_number=True):
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.header_distance = Inches(0.5)
    section.footer_distance = Inches(0.5)
    sectPr = section._sectPr
    for el in list(sectPr):
        if el.tag == qn("w:pgNumType"):
            sectPr.remove(el)
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), fmt)
    if start is not None:
        pg.set(qn("w:start"), str(start))
    sectPr.append(pg)
    footer = section.footer
    footer.is_linked_to_previous = False
    fp = footer.paragraphs[0]
    fp.clear()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if show_number:
        add_page_field(fp)


def configure_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.space_before = Pt(0)
    for name, font, size in (
        ("Heading 1", "Book Antiqua", 18),
        ("Heading 2", "Times New Roman", 16),
        ("Heading 3", "Times New Roman", 14),
    ):
        st = doc.styles[name]
        st.font.name = font
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor(0x00, 0x00, 0x00)
        st.paragraph_format.line_spacing = 1.5


# ---------------------------------------------------------------------------
# Front matter
# ---------------------------------------------------------------------------

def cover(doc):
    for _ in range(1):
        gap(doc)
    if LOGO.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(LOGO), width=Inches(1.35))
    gap(doc)
    _p(doc, TITLE, font="Book Antiqua", size=22, bold=True, align="center", space_after=12)
    gap(doc)
    _p(doc, "B.Tech Project Report submitted", font="Times New Roman", size=14, italic=True, align="center")
    _p(doc, "in partial fulfillment of the requirements", font="Times New Roman", size=14, align="center")
    _p(doc, "for the degree of", font="Times New Roman", size=14, align="center")
    gap(doc)
    _p(doc, "Bachelor of Technology", font="Book Antiqua", size=18, bold=True, align="center")
    _p(doc, "in", font="Times New Roman", size=14, align="center")
    _p(doc, "Mechanical Engineering", font="Book Antiqua", size=18, bold=True, align="center")
    gap(doc)
    gap(doc)
    _p(doc, "by", font="Times New Roman", size=13, align="center")
    _p(doc, STUDENT, font="Book Antiqua", size=18, bold=True, align="center")
    _p(doc, STUDENT2, font="Book Antiqua", size=18, bold=True, align="center")
    gap(doc)
    _p(doc, "under the guidance of", font="Times New Roman", size=13, align="center")
    _p(doc, SUPERVISOR, font="Book Antiqua", size=18, bold=True, align="center")
    gap(doc)
    gap(doc)
    _p(doc, "DEPARTMENT OF MECHANICAL ENGINEERING", font="Times New Roman", size=16, bold=True, align="center")
    _p(doc, "INDIAN INSTITUTE OF TECHNOLOGY PATNA", font="Times New Roman", size=18, bold=True, align="center")
    _p(doc, MONTH_YEAR, font="Book Antiqua", size=16, bold=True, align="center")


def certificate(doc):
    _p(doc, "Certificate", font="Book Antiqua", size=24, bold=True, align="center", space_before=24, space_after=24)
    gap(doc)
    _p(
        doc,
        f"This is to certify that the work contained in this thesis titled “{TITLE}” "
        f"is a bonafide research work of {STUDENTS}, carried out in the Department of Mechanical "
        f"Engineering, Indian Institute of Technology Patna, under my supervision and that it has "
        f"not been submitted elsewhere for a degree.",
        font="Times New Roman",
        size=16,
        italic=True,
        align="justify",
    )
    gap(doc)
    gap(doc)
    gap(doc)
    _p(doc, "Supervisor", font="Times New Roman", size=16, align="right")
    _p(doc, SUPERVISOR, font="Times New Roman", size=14, align="right")
    gap(doc)
    _p(doc, "Date: ____________________", font="Times New Roman", size=16, align="left")
    _p(doc, "Place: IIT Patna", font="Times New Roman", size=16, align="left")


def declaration(doc):
    doc.add_page_break()
    _p(doc, "Declaration", font="Book Antiqua", size=24, bold=True, align="center", space_before=12, space_after=18)
    _p(doc, f"Name of the Student(s):  {STUDENTS}", size=14, align="left")
    gap(doc)
    _p(doc, f"Signature of the Student(s):  {STUDENT}  ____________________", size=14, align="left")
    _p(doc, f"                              {STUDENT2}  ____________________", size=14, align="left")
    gap(doc)
    _p(doc, f"B.Tech. Project Title:  {TITLE}", size=14, align="left")
    gap(doc)
    _p(doc, f"This is to certify that Mr {STUDENT} and Mr {STUDENT2}", size=14, align="left")
    bullet(doc, "has/have sincerely worked on their project,")
    bullet(doc, "has/have contacted me regularly to update on the progress of the assigned project,")
    bullet(
        doc,
        "has/have received my comments on the preliminary version of the report and presentation "
        "and will address those prior to final submission/presentation,",
    )
    bullet(doc, "may be allowed to present/defend the project before the department.")
    gap(doc)
    _p(
        doc,
        "Remarks (if any): Simulated training results are not presented as certified laboratory "
        "measurements. Software feed-hold is not a safety-rated emergency stop. Surface integrity "
        "in this B.Tech work is proxied by roughness Ra unless a laboratory measurement is later booked.",
        size=14,
        align="left",
    )
    gap(doc)
    gap(doc)
    _p(doc, "Name of the Project Guide(s)                         Signature of the Project Guide(s)", size=14, align="left")
    _p(doc, SUPERVISOR, size=14, align="left")
    gap(doc)
    _p(doc, "Date: ____________________", size=14, align="left")


def dedication(doc):
    doc.add_page_break()
    for _ in range(8):
        gap(doc)
    _p(doc, "Dedicated to", font="Lucida Handwriting", size=20, bold=True, align="center")
    _p(doc, "my parents and teachers", font="Lucida Handwriting", size=18, bold=True, align="center")


def acknowledgements(doc):
    doc.add_page_break()
    _p(doc, "Acknowledgements", font="Book Antiqua", size=20, bold=True, align="center", space_after=18)
    body(
        doc,
        "The authors express sincere gratitude to the project supervisor, Dr. Mahavir Singh, and to the faculty of the "
        "Department of Mechanical Engineering, Indian Institute of Technology Patna, for guidance "
        "in framing a B.Tech problem that remains both academically honest and industrially relevant. "
        "The work sits between manufacturing science and applied machine learning. It does not claim "
        "a finished digital twin of a certified machine, and it does not claim residual-stress maps "
        "from X-ray diffraction unless that measurement is later booked in the laboratory.",
        first=True,
    )
    body(
        doc,
        "Acknowledgements are also due to the open tooling used to build the demonstration — Python, "
        "scikit-learn, Streamlit, and a browser-based CNC visualisation used for cycle follow — and "
        "to the need, repeatedly emphasised during the work, to keep software Hold clearly separated "
        "from a hardwired emergency stop. Any laboratory facilities of the Department that are used "
        "in a later labelled campaign will be acknowledged in a revised certificate.",
    )
    gap(doc)
    gap(doc)
    _p(doc, STUDENT.upper(), font="Times New Roman", size=12, align="right")
    _p(doc, STUDENT2.upper(), font="Times New Roman", size=12, align="right")


def abstract_page(doc):
    doc.add_page_break()
    _p(doc, "Abstract", font="Book Antiqua", size=20, bold=True, align="center", space_after=18)
    body(
        doc,
        "Surface integrity after CNC milling decides whether an aluminium part is accepted, reworked "
        "or scrapped. In teaching laboratories and small job shops the usual practice is still "
        "post-process: roughness is measured after the pass, or the tool is changed when the operator "
        "senses chatter, or the tool is changed on a conservative clock. That loop is late. Damage "
        "to the surface has already occurred. The present project builds an early-warning integrity "
        "monitor for end milling of Al 6061. Multimodal process signals — vibration, force, spindle "
        "power, temperature and commanded feed/speed — are reduced to a compact feature vector. A "
        "Gaussian mixture model discovers latent machining regimes (stable, transitional, unstable "
        "and severe). Gradient-boosting heads predict roughness Ra, flank wear VB, wear rate, "
        "temperature and the probability that the surface will leave specification inside a short "
        "horizon. A physics residual, formed from the cutting-power identity P ≈ Fc · Vc, is treated "
        "as a first-class feature so that the learner is not purely correlational.",
        first=True,
    )
    body(
        doc,
        "A shop-floor dashboard presents live metrics, regimes, forecasts and operator-set hard-stop "
        "limits. A local bridge can follow Cycle start and Hold on a visualisation CNC so that a "
        "second computer can run the monitor during a cut. Training in the present codebase is on "
        "physics-inspired simulated runs. That is sufficient to exercise the full pipeline before a "
        "labelled laboratory campaign. For the B.Tech integrity proxy, degradation is declared when "
        "predicted or measured Ra exceeds the specification (default 1.6 µm). Residual stress by XRD "
        "is not claimed. Automatic Hold is decision support, not a certified safety function. The "
        "report records ideation, aims, method, implementation, comparison with existing practice, "
        "industry and market implications, limitations and a realistic path from simulator to shop floor.",
    )
    gap(doc)
    _p(
        doc,
        "Key words: CNC Milling; Aluminium 6061; Surface Integrity; Roughness Ra; Flank Wear; "
        "Latent Regime Discovery; Gaussian Mixture Model; Physics-Informed Machine Learning; "
        "Tool Condition Monitoring; Early Warning.",
        italic=False,
        align="justify",
    )
    # make Key words bold+italic label
    # already as one paragraph; acceptable


def toc_and_lists(doc):
    doc.add_page_break()
    _p(doc, "Contents", font="Times New Roman", size=22, bold=True, align="center", space_after=12)
    items = [
        ("Certificate", "i", 0),
        ("Declaration", "ii", 0),
        ("Dedication", "iii", 0),
        ("Acknowledgements", "iv", 0),
        ("Abstract", "v", 0),
        ("Contents", "vi", 0),
        ("List of Figures", "vii", 0),
        ("List of Tables", "viii", 0),
        ("Nomenclature", "ix", 0),
        ("1  Introduction", "1", 1),
        ("    1.1  Introduction", "", 2),
        ("    1.2  Literature Review", "", 2),
        ("    1.3  Motivation", "", 2),
        ("    1.4  Objectives", "", 2),
        ("    1.5  Scope and Limitations", "", 2),
        ("    1.6  Organisation of the Report", "", 2),
        ("2  Methodology", "", 1),
        ("    2.1  Introduction", "", 2),
        ("    2.2  Process Window and Materials", "", 2),
        ("    2.3  Data Acquisition", "", 2),
        ("    2.4  Feature Extraction", "", 2),
        ("    2.5  Latent Regime Discovery", "", 2),
        ("    2.6  Predictive Models", "", 2),
        ("    2.7  Physics Residual and Simulator", "", 2),
        ("    2.8  Supervisor and Hard-Stop Logic", "", 2),
        ("    2.9  System Architecture and Implementation", "", 2),
        ("3  Results and Findings", "", 1),
        ("    3.1  Introduction", "", 2),
        ("    3.2  Simulated Campaign", "", 2),
        ("    3.3  Integration Observations", "", 2),
        ("    3.4  Comparison with Alternative Strategies", "", 2),
        ("    3.5  Industry Impact and Markets", "", 2),
        ("    3.6  How the Results Must Be Read", "", 2),
        ("4  Conclusions and Scope for Future Work", "", 1),
        ("    4.1  Conclusions", "", 2),
        ("    4.2  Scope for Future Work", "", 2),
        ("References", "", 1),
        ("Appendices", "", 1),
        ("    Appendix A  Default Process Parameters", "", 2),
        ("    Appendix B  How to Run the Demonstration", "", 2),
        ("    Appendix C  Feature List", "", 2),
        ("    Appendix D  Risk Register", "", 2),
        ("    Appendix E  Suggested Viva Questions", "", 2),
    ]
    for text, page, level in items:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.27), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        bold = level == 1 or level == 0
        r = p.add_run(text + (f"\t{page}" if page else "\t"))
        set_run(r, "Times New Roman", 12, bold=bold)

    doc.add_page_break()
    _p(doc, "List of Figures", font="Times New Roman", size=22, bold=True, align="center", space_after=12)
    figs = [
        "Figure 1.1  Positioning against common shop-floor strategies",
        "Figure 2.1  Sensor paths that collapse into one SensorFrame",
        "Figure 2.2  Feature pipeline from a SensorFrame to the model heads",
        "Figure 2.3  Taylor-type flank-wear growth used in the physics simulator",
        "Figure 2.4  Supervisor logic: physical limits trip, risk informs",
        "Figure 2.5  End-to-end architecture of the machining integrity monitor",
        "Figure 3.1  Latent regimes along a simulated Al 6061 end-milling run",
        "Figure 3.2  Indicative TCM market trajectory",
        "Figure 3.3  Where an early Ra/VB warning can reduce shop cost (indicative)",
        "Figure 4.1  Honest industrialisation path",
    ]
    for f in figs:
        _p(doc, f, align="left", space_after=4)

    doc.add_page_break()
    _p(doc, "List of Tables", font="Times New Roman", size=22, bold=True, align="center", space_after=12)
    tabs = [
        "Table 2.1  Default process window used in the implemented system",
        "Table 2.2  Feature vector used by GMM and HGB heads",
        "Table 3.1  Qualitative comparison of shop-floor strategies",
        "Table 3.2  Stakeholder map",
        "Table 3.3  Indicative cost model for a two-VMC aluminium cell",
        "Table 3.4  Honest claims versus refused claims",
    ]
    for t in tabs:
        _p(doc, t, align="left", space_after=4)

    doc.add_page_break()
    _p(doc, "Nomenclature", font="Times New Roman", size=22, bold=True, align="center", space_after=12)
    _p(doc, "Roman Symbols", size=14, bold=True, align="left", space_after=6)
    symbols = [
        ("ap", "Axial depth of cut, mm"),
        ("D", "Tool diameter, mm"),
        ("fz", "Feed per tooth, mm/tooth"),
        ("Fc", "Cutting force, N"),
        ("n", "Spindle speed, r/min"),
        ("P", "Spindle power, W"),
        ("Pidle", "Idle / offset power, W"),
        ("Ra", "Arithmetic mean roughness, µm"),
        ("Ra,lim", "Roughness specification, µm"),
        ("Tw", "Feature-window length, s"),
        ("VB", "Flank wear land, mm"),
        ("VB,lim", "Demo flank-wear limit, mm"),
        ("Vc", "Cutting speed, m/min"),
        ("z", "Number of teeth"),
        ("Δt", "Forecast horizon, s"),
    ]
    for sym, meaning in symbols:
        _p(doc, f"{sym}    =    {meaning}", align="left", space_after=2)
    gap(doc)
    _p(doc, "Greek Symbols", size=14, bold=True, align="left", space_after=6)
    _p(doc, "—    No independent Greek process variable is used as a primary symbol in this report.", align="left")
    gap(doc)
    _p(doc, "Acronyms", size=14, bold=True, align="left", space_after=6)
    acr = [
        ("CNC", "Computer Numerical Control"),
        ("DAQ", "Data Acquisition"),
        ("DRO", "Digital Read-Out"),
        ("GMM", "Gaussian Mixture Model"),
        ("HGB", "Histogram-based Gradient Boosting"),
        ("HMI", "Human–Machine Interface"),
        ("ISO", "International Organization for Standardization"),
        ("MED", "Department of Mechanical Engineering"),
        ("MSME", "Micro, Small and Medium Enterprise"),
        ("SI", "Surface Integrity (here proxied by Ra)"),
        ("TCM", "Tool Condition Monitoring"),
        ("XRD", "X-ray Diffraction (not implemented)"),
    ]
    for a, m in acr:
        _p(doc, f"{a}    ≡    {m}", align="left", space_after=2)


# ---------------------------------------------------------------------------
# Chapters
# ---------------------------------------------------------------------------

def ch1(doc):
    chapter_title(doc, 1, "Introduction", new_page=False)
    section(doc, "1.1  Introduction")
    body(
        doc,
        "Mechanical engineering graduates are asked, more often than a decade ago, to connect a "
        "cutting process to data. Industry 4.0 documents speak of digital twins, predictive "
        "maintenance and zero-defect machining. On a real shop floor the gap is still large. A "
        "vertical machining centre already records spindle load and axis positions, but it does not "
        "tell the operator that the next thirty seconds of cutting will push Ra through the drawing "
        "limit. A profilometer tells the truth after the fact. A worn end mill tells the truth when "
        "the finish turns cloudy or the spindle note changes. The ideation of the present project is "
        "therefore simple: a monitor is to sit beside the mill, consume the same kinds of signals a "
        "laboratory can actually instrument, and raise an early, explainable warning before the "
        "surface is lost.",
        first=True,
    )
    body(
        doc,
        "The ideation is also deliberately modest. Many research papers jump from a few accelerometer "
        "traces to a deep network that claims residual stress, white-layer thickness and fatigue life. "
        "Those quantities matter in aerospace and biomedical work, but they require residual-stress "
        "measurement, metallography and a designed experiment that a single B.Tech semester rarely "
        "completes. This project therefore locks a B.Tech integrity proxy: the surface is treated as "
        "degraded when Ra exceeds the specification. Flank wear VB, wear rate, vibration, force and "
        "temperature are monitored as the physical drivers of that roughness. If the department later "
        "books XRD or a stylus campaign, the same software sockets can accept those labels. Until then "
        "the claim stays inside what the code and the simulator can support.",
    )
    body(
        doc,
        "Milling is treated as a multimodal, physics-constrained time series. The signals are windowed. "
        "Features that a manufacturing engineer already understands (RMS, chatter-band energy, power "
        "residual) are extracted. Latent regimes are discovered without forcing the operator to name "
        "them in advance. Ra and tool state are forecast a short horizon ahead. The result is shown "
        "on a shop-floor dashboard. If the operator’s typed hard-stop is crossed, feed-hold is "
        "requested on the visualisation mill so that the tool freezes where it is. Degradation "
        "probability remains on the screen as a risk number, not as an automatic crash stop. Training "
        "is first performed on a physics-inspired simulator so that the pipeline is complete before "
        "the first labelled cut.",
    )
    body(
        doc,
        "Aluminium 6061 is the default workpiece because it is the alloy a teaching mill actually cuts: "
        "plates are inexpensive, chips are manageable, cutting speeds around 90–100 m/min are "
        "conventional, and the drawing almost always specifies Ra rather than a residual-stress "
        "envelope. A 10 mm four-flute end mill at 3000 r/min and 0.12 mm/tooth is a window a student "
        "can picture. Axial depth 1.0 mm keeps the demonstration in a finishing or semi-finishing "
        "story. The Ra specification of 1.6 µm is a common general-engineering finish, tight enough "
        "that wear and chatter will violate it, loose enough that the first seconds of a sharp tool "
        "are clearly legal.",
    )
    body(
        doc,
        "Ideas that were rejected are part of the research record. A live stylus roughness meter "
        "mounted on the spindle is not available and is not how Ra is measured. A residual-stress "
        "predictor from vibration alone is dishonest without XRD. Reinforcement-learning feed override "
        "changes the interpolator without a risk assessment. A large convolutional network on raw "
        "5 kHz traces is uninterpretable and hungry for labelled cuts that do not exist. Automatic "
        "e-stop from degradation probability was observed to trip the demonstration while the cut was "
        "still useful. Using mill Stop as if it were Hold resets programme progress. Each rejection "
        "left a sentence in the code or the user interface.",
    )
    add_figure(doc, "fig5_compare.png", "Figure 1.1: Positioning against common shop-floor strategies (qualitative).")
    body(
        doc,
        "Figure 1.1 places the present work against fixed-time tool change, threshold tool-condition "
        "monitoring and purely data-driven deep learning. The intended advantage is not a higher "
        "paper metric. It is a complete, inspectable, physically annotated early-warning layer that "
        "a mechanical reader can defend.",
        first=True,
    )

    section(doc, "1.2  Literature Review")
    body(
        doc,
        "Surface integrity is the set of geometric and metallurgical conditions left by the last cut: "
        "roughness, lay, residual stress, hardness alteration and, in severe cases, white layer or "
        "cracks [Kalpakjian and Schmid, 2014; Altintas, 2012]. For aluminium housings, manifolds and "
        "fixtures the drawing almost always specifies Ra (and sometimes Rz). Fatigue-critical "
        "aerospace aluminium may additionally specify residual stress. In a B.Tech laboratory the "
        "instrument that is actually available is usually a portable profilometer. That is why the "
        "present project uses Ra as the integrity proxy. The literature is clear that flank wear, "
        "built-up edge, chatter and thermal softening all move Ra before a catastrophic insert "
        "failure [Tlusty, 2000; ISO 8688].",
        first=True,
    )
    body(
        doc,
        "Tool-condition monitoring (TCM) is the research name for listening to the cut while it "
        "happens. Typical sensors are accelerometers on the spindle or vice, dynamometers, current "
        "transformers on the spindle motor, acoustic emission and thermocouples. Commercial units "
        "(threshold TCM) trip when a band exceeds a limit. They are good at detecting a broken tool; "
        "they are weak at saying that Ra will fail in twelve seconds. Recent surveys of machine "
        "learning in CNC milling show that classification of wear stage, regression of VB, chatter "
        "detection and roughness prediction are now standard research tasks [Advances in Manufacturing, "
        "2025]. Simultaneous monitoring of roughness and wear is still described as early-stage in "
        "2025 experimental papers [Scientific Reports, 2025]. Digital-twin papers add on-machine "
        "inspection and remaining-life models, with a visible gap between offline error and live "
        "error [Journal of Intelligent Manufacturing, 2025]. The present project does not claim to "
        "close that gap. It claims to assemble a complete, inspectable pipeline that a student and "
        "a shop can run, then replace the simulated labels with measured ones.",
    )
    body(
        doc,
        "A purely data-driven model will happily learn the correlation between a noisy accelerometer "
        "and a simulated Ra label. When the fixture changes, the correlation dies. Physics-informed "
        "learning adds a constraint the cut already obeys [Altintas, 2012]. Here the constraint is "
        "elementary cutting mechanics: spindle power should be consistent with cutting force and "
        "cutting speed, up to a roughly constant idle offset. The normalised residual of that identity "
        "is a feature. When force and power disagree, something in the sensing chain or in the process "
        "is wrong. That is useful both to the model and to the operator. It is not a finite-element "
        "residual-stress solver. It is the level of physics a B.Tech monitor can compute in 250 ms.",
    )
    body(
        doc,
        "Supervised fault libraries require someone to label chatter, built-up edge or rubbing on "
        "every window. That labelling is expensive and contested. Unsupervised mixture models find "
        "clusters in feature space and let the engineer name them afterwards. The present project "
        "uses a four-component Gaussian mixture ordered by severity, presented on the dashboard as "
        "Regime A (stable cutting), B (transitional), C (unstable) and D (severe degradation). After "
        "training, the GMM is the regime head. The names are for the operator; the mathematics is "
        "clustering.",
    )
    body(
        doc,
        "Classical metal-cutting texts already contain the quantities this monitor is allowed to see: "
        "cutting power, tool wear, chatter and tooth-passing frequency [Kalpakjian and Schmid, 2014; "
        "Altintas, 2012; Tlusty, 2000]. Taylor’s 1907 tool-life form is used only qualitatively in "
        "the simulator; no claim is made that the accelerated demonstration curve is an identified "
        "Taylor exponent for a named insert [Taylor, 1907]. ISO 8688 supplies the 0.3 mm milling wear "
        "conversation. ISO 4287 / 21920 supply the Ra conversation. Market notes on TCM are used only "
        "as industrial context and are not experimental citations [Dataintelo, 2025].",
    )
    body(
        doc,
        "What the literature does not yet hand a B.Tech student is a complete, honest, runnable stack "
        "with a declared integrity proxy and a declared safety non-claim. Filling that systems-and-honesty "
        "gap is the literature justification for the present report.",
    )

    section(doc, "1.3  Motivation")
    body(
        doc,
        "CNC end milling of aluminium produces acceptable surface integrity only inside a moving "
        "process window. Tool wear, chatter and thermal drift move that window during a single "
        "programme. Post-process Ra measurement detects the failure after the surface is already out "
        "of specification. Fixed-interval tool change wastes tool life. Threshold alarms fire too "
        "late or too often. The industrial irritation is therefore late discovery. The academic "
        "irritation is that Industry 4.0 is often taught as a poster rather than as a SensorFrame, "
        "a limit and a hold request.",
        first=True,
    )
    body(
        doc,
        "Motivation is both academic and economic. Academically, the project forces a connection "
        "between manufacturing science (Taylor-type wear, cutting power, chatter bands) and a software "
        "system that another person can run. Economically, unplanned tool events and scrap from poor "
        "finish are among the largest avoidable costs in milling cells. Public market notes place "
        "tool-condition monitoring in the order of USD 1.8 billion in the mid-2020s with high "
        "single-digit to low double-digit growth, and they attribute tens of billions of dollars of "
        "annual downtime to tool-related stops [Dataintelo, 2025]. A student project does not capture "
        "that market. It can, however, show a shop what a cheap early-warning layer looks like before "
        "anyone writes a purchase order for a closed commercial stack.",
    )
    body(
        doc,
        "Indian job shops are being asked for documented quality by export customers and by larger "
        "domestic OEMs. They rarely have a metrology room on every shift. They do have used computers, "
        "inexpensive microcontrollers and operators who already hear the cut. A monitor that starts "
        "on that equipment is a more realistic national intervention than a lecture on digital twins "
        "that assumes OPC-UA, a historian and a six-figure licence. The present project is intended "
        "to occupy that gap.",
    )
    body(
        doc,
        "A further pedagogical motivation exists inside the department. Manufacturing laboratories "
        "teach speeds and feeds, then teach a profilometer, then teach a toolmaker’s microscope if "
        "one exists. They rarely teach the hour between those instruments. The present dashboard is "
        "intended to occupy that hour. A junior batch can be asked to explain why Regime C appeared, "
        "to type a hard-stop, and to write the honesty sentences from memory.",
    )

    section(doc, "1.4  Objectives")
    body(
        doc,
        "The aim of the project is to design, implement and demonstrate a physics-informed multimodal "
        "learning system for latent regime discovery and early surface-integrity degradation prediction "
        "in CNC end milling of aluminium alloy (default Al 6061), and to package that system as a "
        "usable shop-floor dashboard with optional linkage to a browser CNC and to serial data-acquisition "
        "hardware.",
        first=True,
    )
    body(doc, "The specific objectives are as follows.")
    objs = [
        "To define a process window (tool, speed, feed, depth, Ra specification) that is typical of teaching-laboratory aluminium milling.",
        "To build a SensorFrame contract so that simulator, Arduino serial and HTTP/bridge sources look the same to the model.",
        "To extract time-domain, frequency-domain and physics-residual features from each window.",
        "To train a Gaussian mixture model to assign latent regimes A–D on simulated multimodal features.",
        "To train gradient-boosting heads for Ra, VB, wear rate, temperature and short-horizon degradation probability.",
        "To implement a supervisor with operator-set desired maxima and hard-stop limits, without hard-stopping on risk alone.",
        "To deliver a Streamlit integrity monitor with live plots, regime colour, estimated time of arrival to a limit, and manual overlay of measured readings.",
        "To provide a local mill bridge so that Cycle start and Hold on a visualisation CNC can start and freeze the monitor.",
        "To state limitations honestly: simulated labels, Ra as the surface-integrity proxy, and software Hold not equal to a certified emergency stop.",
    ]
    for o in objs:
        bullet(doc, o)
    gap(doc)
    body(
        doc,
        "The working hypothesis is that if multimodal features are constrained by a cutting-power "
        "residual and clustered by a Gaussian mixture, then short-horizon Ra and wear heads will rise "
        "through identifiable regimes before a hard Ra or VB limit, and an operator-set supervisor "
        "can request Hold without treating probability itself as a trip. The hypothesis is tested in "
        "this report on simulated runs and on the integrated dashboard. Confirmation on a physical "
        "mill requires a later labelled campaign.",
        first=True,
    )

    section(doc, "1.5  Scope and Limitations")
    body(
        doc,
        "In scope are Al 6061 end milling in the configured window; simulated and serial/HTTP "
        "acquisition; feature extraction; GMM regimes; gradient-boosting forecasts; the dashboard; "
        "mill-cycle follow; and a software Hold request. Out of scope unless separately booked are "
        "XRD residual stress, microhardness maps, white-layer measurement, five-axis toolpaths, "
        "titanium or hardened steel, closed-loop override of a real Fanuc or Siemens interpolator, "
        "and any claim that the Python process is a Category-0 or Category-1 stop under machine-tool "
        "safety standards.",
        first=True,
    )
    body(
        doc,
        "Dr. Mahavir Singh, the academic supervisor of the project, is not a certified CNC emergency-stop authority. "
        "Any shop-floor use remains under the licensed machine operator. Simulated training results "
        "are not laboratory measurements. Those two sentences are part of the scope, not an apology "
        "after the fact.",
    )

    section(doc, "1.6  Organisation of the Report")
    body(
        doc,
        "The report follows the official B.Tech format of the Department of Mechanical Engineering, "
        "Indian Institute of Technology Patna. Chapter 1 introduces the problem, reviews the "
        "literature, states motivation and objectives, and fixes scope. Chapter 2 presents the "
        "methodology: process window, acquisition, features, models, physics residual, supervisor "
        "and architecture. Chapter 3 reports simulated findings, integration observations, comparison "
        "with alternatives, and industry-market implications, and states how those findings must be "
        "read. Chapter 4 concludes and sets out the scope for future work. References and appendices "
        "follow. Front matter uses lower-case roman pagination. Arabic pagination begins at Chapter 1.",
        first=True,
    )


def ch2(doc):
    chapter_title(doc, 2, "Methodology")
    section(doc, "2.1  Introduction")
    body(
        doc,
        "The methodology is organised so that a change in sensors does not rewrite the user interface. "
        "Every source emits a SensorFrame. Processing turns a frame into a feature vector. An ensemble "
        "holds the Gaussian mixture and the boosting heads. A supervisor emits a control decision. "
        "The Streamlit application is only a view and a place to type limits. A CNC bridge is a "
        "separate process. The present chapter records the process window, the acquisition contract, "
        "the features, the learners, the physics residual, the supervisor ethics and the implemented "
        "repository. Main-body style follows the departmental template: Times New Roman, 12 point, "
        "1.5 line spacing, SI units, and passive voice [IIT Patna MED template].",
        first=True,
    )

    section(doc, "2.2  Process Window and Materials")
    body(
        doc,
        "Unless the operator overrides the sidebar, the monitor assumes Al 6061, end milling, a 10 mm "
        "four-flute tool, 3000 r/min, 0.12 mm/tooth, 1.0 mm axial depth and an Ra specification of "
        "1.6 µm. Cutting speed is then about 94 m/min. That is a conventional teaching-laboratory "
        "aluminium window: fast enough to show wear and chatter in a short demonstration, mild enough "
        "that a real 6061 plate would not immediately rub or weld. The simulator also trains at "
        "neighbouring speeds and feeds (2400–3600 r/min, 0.08–0.18 mm/tooth) so that the mixture model "
        "sees more than one operating point.",
        first=True,
    )
    add_table(
        doc,
        "Table 2.1: Default process window used in the implemented system",
        ["Quantity", "Symbol", "Default value", "Role"],
        [
            ["Workpiece", "Al 6061", "T6 plate (assumed)", "Alloy spoken by models and HMI"],
            ["Tool diameter", "D", "10 mm", "Sets cutting speed with spindle speed"],
            ["Teeth", "z", "4", "Tooth-passing frequency 200 Hz at 3000 r/min"],
            ["Spindle speed", "n", "3000 r/min", "Process window; also a training axis"],
            ["Feed per tooth", "fz", "0.12 mm/tooth", "Chip load; training axis 0.08–0.18"],
            ["Axial depth", "ap", "1.0 mm", "Finishing / semi-finishing story"],
            ["Ra specification", "Ra,lim", "1.6 µm", "B.Tech integrity-proxy threshold"],
            ["VB demo limit", "VB,lim", "0.30 mm", "ISO 8688-style 100 % wear for demo"],
            ["Window length", "Tw", "0.25 s", "Feature frame"],
            ["Sample rate", "fs", "5000 Hz", "Simulator / Arduino target"],
            ["Horizon", "Δt", "30 s", "Risk-head look-ahead"],
            ["Refresh", "—", "400 ms", "Dashboard loop"],
        ],
    )
    body(
        doc,
        "Table 2.1 is the contractual process window. Changing only the configuration file should not "
        "collapse the thesis story. Tooth-passing frequency is n × z / 60. For 3000 r/min and four "
        "flutes that is 200 Hz. Chatter, if it appears, is usually not exactly at that line. The "
        "feature extractor therefore keeps a tooth band and a chatter band separate.",
        first=True,
    )

    section(doc, "2.3  Data Acquisition")
    body(
        doc,
        "Every source — simulator, serial Arduino, HTTP or G-code playback — must emit a SensorFrame: "
        "time, vibration window, optional force window, temperature, spindle power or current, "
        "commanded r/min and feed, and optional true Ra if a later experiment writes it. The rest of "
        "the stack never asks which source produced the frame. That is the main software idea. It is "
        "why the dashboard can be developed without a mill and later pointed at a COM port or at a "
        "bridge URL without rewriting the model.",
        first=True,
    )
    add_figure(doc, "fig7_sensors.png", "Figure 2.1: Sensor paths that collapse into one SensorFrame.")
    body(
        doc,
        "Three paths are provided. Path A is simulator only: Start run on the dashboard. Path B is "
        "serial: the Arduino sketch is flashed, analog accelerometer to A0, current transformer to A1, "
        "LM35 to A2, and a COM port is selected. Path C is HTTP/bridge: the source in the configuration "
        "file is set to http, the monitor is left open, and Cycle start is pressed on the hooked mill. "
        "All three paths end in the same inference call and the same plots. Figure 2.1 summarises the "
        "collapse into one contract.",
        first=True,
    )
    body(
        doc,
        "Large automotive and aerospace plants buy MTConnect or OPC-UA stacks and commercial TCM. "
        "Indian MSME job shops and college laboratories usually have a Fanuc or Siemens mill, a vice, "
        "and no budget for a dynamometer on every machine. Accepting three sources is therefore a "
        "pedagogical and industrial choice, not a claim that the simulator replaces ISO 8688 tool-life "
        "testing.",
    )

    section(doc, "2.4  Feature Extraction")
    body(
        doc,
        "Each 0.25 s window at up to 5 kHz is reduced to a ten-dimensional vector used by the models: "
        "vibration RMS, kurtosis, crest factor, force RMS, force fluctuation, chatter-band energy, "
        "spectral entropy, temperature, spindle power and the physics residual. Additional quantities "
        "(tooth-pass band, peak-to-peak, current) are computed for plots. Time-domain RMS tracks energy. "
        "Kurtosis and crest factor rise when impacts or chatter spikes appear. The chatter band is the "
        "spectral region away from the tooth-passing frequency where self-excited vibration lives. "
        "Spectral entropy rises as the spectrum becomes less tonal.",
        first=True,
    )
    add_figure(doc, "fig4_features.png", "Figure 2.2: Feature pipeline from a SensorFrame to the model heads.")
    add_table(
        doc,
        "Table 2.2: Feature vector used by GMM and HGB heads",
        ["Feature", "Domain", "Why it is retained"],
        [
            ["Vibration RMS", "Time", "Energy of the cut; rises with chatter and wear"],
            ["Kurtosis", "Time", "Spikiness; early departure from a Gaussian rub"],
            ["Crest factor", "Time", "Peak-to-RMS; impacts and intermittent chatter"],
            ["Force RMS", "Time", "Load; related to chip thickness and dulling"],
            ["Force fluctuation", "Time", "Unsteady cutting, built-up edge, runout"],
            ["Chatter-band energy", "Frequency", "Energy away from the tooth-passing line"],
            ["Spectral entropy", "Frequency", "Loss of a clean tonal cut"],
            ["Temperature", "Thermal", "Lagged bulk / sensor temperature"],
            ["Spindle power", "Energy", "What the motor is actually spending"],
            ["Physics residual", "Mechanics", "Disagreement of P with Fc · Vc + idle"],
        ],
    )
    body(
        doc,
        "None of the features in Table 2.2 is new. The contribution is to keep them, to refuse to drown "
        "them in an uninterpreted embedding, and to add one mechanics residual that can be written on "
        "the board in one line. Figure 2.2 shows the pipeline from window to model heads.",
        first=True,
    )

    section(doc, "2.5  Latent Regime Discovery")
    body(
        doc,
        "A four-component Gaussian mixture is fitted on standardised feature vectors from six simulated "
        "cutting conditions. Components are ordered so that the dashboard can name them A–D from stable "
        "to severe. The operator sees a colour and a confidence. The method is unsupervised: nobody "
        "labelled chatter on the training windows. After deployment, a shift from A to C is a regime "
        "discovery event — the cut has entered a different statistical neighbourhood — which is more "
        "honest than a brittle if-then fault tree, and more usable than a 128-dimensional autoencoder "
        "latent space with no names.",
        first=True,
    )
    body(
        doc,
        "Four regimes were chosen because they map onto a shop sentence. A is the sentence “leave it.” "
        "B is “watch the next thirty seconds.” C is “finish this feature and inspect.” D is “hold and "
        "change the tool.” Three components collapsed stable and transitional on the simulated cloud. "
        "Five components split severe into two unnamed shards. Four survived. On real data that number "
        "must be re-chosen with a cutting teacher in the room, not with a default from this report. "
        "StandardScaler is fit on the training cloud so that temperature in Celsius and chatter energy "
        "in arbitrary units do not dominate the mixture by unit choice.",
    )

    section(doc, "2.6  Predictive Models")
    body(
        doc,
        "Histogram-based gradient boosting is used for Ra, VB, wear rate, temperature and a head for "
        "short-horizon degradation probability. The models are small, train on a laptop, and remain "
        "inspectable through feature contributions on the dashboard. They are not long short-term "
        "memory networks. For a 0.25 s window and a 30 s horizon, a boosted tree on engineered features "
        "is an appropriate B.Tech estimator. The forecast object also carries a textual recommendation "
        "and a tool-health percentage relative to the 0.30 mm VB demonstration limit (ISO 8688-style, "
        "not a certified tool-life test of this specific insert).",
        first=True,
    )
    body(
        doc,
        "Class imbalance is structural: most windows are stable. The risk head therefore sees a horizon "
        "label (will Ra or VB cross inside Δt?) rather than “is this millisecond a failure.” That is "
        "the early-warning trick. It is also why probability can be high while the current Ra is still "
        "legal. The supervisor’s refusal to trip on that probability is the corresponding safety trick.",
    )

    section(doc, "2.7  Physics Residual and Simulator")
    body(
        doc,
        "The physics residual is |Pmeas − (Pidle + Fc · Vc)| / max(Pmeas, 1), written conceptually as "
        "Eq. (2.1). When force and power disagree, either the process or the sensing chain has left "
        "the model that can be defended on a whiteboard. That is physics-informed learning at the "
        "correct scale for this degree. It is not a digital twin in the finite-element sense.",
        first=True,
    )
    _p(doc, "P ≈ Pidle + Fc · Vc                                          (2.1)", align="center", italic=True)
    gap(doc)
    body(
        doc,
        "The simulator grows flank wear with a Taylor-type rate that increases with cutting speed, "
        "feed, chatter and current wear [Taylor, 1907]. Temperature is a first-order lag toward a "
        "power-and-wear steady state. Time is accelerated so a wear curve that would take minutes to "
        "hours on a real tool fits in about one minute on screen. Vibration and force traces become "
        "more impulsive as chatter and wear rise. True Ra in the simulator is a function of the same "
        "drivers, which is why the learned Ra head can look accurate on simulated data. That accuracy "
        "is not transferable to the laboratory until measured Ra is logged.",
        first=True,
    )
    add_figure(doc, "fig3_wear.png", "Figure 2.3: Taylor-type flank-wear growth used in the physics simulator.")
    body(
        doc,
        "Figure 2.3 shows the qualitative wear curve and the 0.30 mm demonstration limit. Training "
        "walks six (r/min, feed, seed) conditions, extracts windows, and fits the scaler, the mixture "
        "and the separate boosting pipelines. The trained_on string stored with the model states that "
        "the data are physics-simulated. Replacing the dataset is a one-function change once CSV logs "
        "of real Ra and microscope VB exist.",
        first=True,
    )

    section(doc, "2.8  Supervisor and Hard-Stop Logic")
    body(
        doc,
        "The supervisor compares live Ra, VB, wear rate, temperature, vibration RMS and force RMS with "
        "the operator’s typed desired maxima and hard-stop values. Degradation probability is displayed "
        "and may be used for alerts, but in the delivered dashboard it is not an armed hard-stop. That "
        "decision came from the demonstration itself: risk often sat in the 70–90 % band while the "
        "physical cut was still useful. Tripping on probability emptied the demonstration and would "
        "train an operator to ignore the system. Hard-stop therefore stays on quantities an inspector "
        "could later measure.",
        first=True,
    )
    add_figure(doc, "fig8_supervisor.png", "Figure 2.4: Supervisor logic: physical limits trip, risk informs.")
    body(
        doc,
        "When a hard-stop fires, the monitor requests software Hold on the bridged mill so the tool "
        "freezes at the current pose rather than returning to programme origin. That Hold is not an "
        "emergency stop. Figure 2.4 records the rule. Three sentences belong in every release: "
        "simulated training is not a laboratory result; Ra is the B.Tech surface-integrity proxy; "
        "software Hold is not a certified emergency stop.",
        first=True,
    )

    section(doc, "2.9  System Architecture and Implementation")
    body(
        doc,
        "The repository is layered. Acquisition implements a sensor source. Processing turns a frame "
        "into a feature vector. The advanced monitor holds the mixture and the boosting heads. The "
        "supervisor emits a decision. The Streamlit application is the view. The CNC bridge binds "
        "port 8766, proxies a browser mill, injects a cycle hook, and exposes status and event routes.",
        first=True,
    )
    add_figure(doc, "fig1_architecture.png", "Figure 2.5: End-to-end architecture of the machining integrity monitor.")
    body(
        doc,
        "Figure 2.5 is the architecture diagram. A second computer in a demonstration setting ran a "
        "ForgeMill visualisation. That mill has Cycle start, Hold, Stop, digital read-out and an "
        "isometric toolpath view. It has no official telemetry application-programming interface. "
        "HTTPS pages cannot call http://localhost on the monitor computer (mixed content). The "
        "engineering answer used here is a local reverse proxy: the CNC computer opens an HTTP "
        "address on the monitor, which serves the mill plus a small hook. Cycle start sets the bridge "
        "running flag; the dashboard starts the simulator; hard-stop posts a hold request; the hook "
        "clicks Hold so the pose freezes.",
        first=True,
    )
    body(
        doc,
        "It is unusual to put transport-layer security mixed-content and HTTP proxies in a mechanical "
        "report. They are here because they decided whether Cycle start was an experimental factor or "
        "a wish. In-process monitoring includes the path the process event takes to the model. The "
        "hook must not flood the proxy with per-frame pose posts; that was observed to freeze the mill "
        "tab and was corrected. The intended client is a standard browser on the local-area-network "
        "URL, not an integrated-development-environment preview.",
    )
    body(
        doc,
        "Dashboard language is shop language: STABLE, WATCH, SURFACE RISK; regimes A–D; Ra in "
        "micrometres; VB in millimetres; temperature in Celsius; a refresh control that actually reruns "
        "the script; optional typed measured values so a student can overlay a profilometer reading. "
        "The point of the human–machine interface is not novelty. It is that a mechanical supervisor "
        "can read it without opening a notebook.",
    )


def ch3(doc):
    chapter_title(doc, 3, "Results and Findings")
    section(doc, "3.1  Introduction")
    body(
        doc,
        "The present chapter reports what the implemented system shows, what integration revealed, "
        "how the approach compares with common shop-floor strategies, and how industry and markets "
        "are affected if the idea is adopted after a labelled campaign. The chapter also states, with "
        "deliberate repetition, what the demonstration does not show. Anyone using these pages as a "
        "journal results chapter in the laboratory sense is misusing them. The correct use is: the "
        "pipeline is complete, the interface is usable, the failure modes of Hold-versus-Stop and "
        "probability-versus-hard-stop were found in software, and the next experiment is well defined.",
        first=True,
    )

    section(doc, "3.2  Simulated Campaign")
    body(
        doc,
        "On a typical simulator run the dashboard moves from STABLE to WATCH to SURFACE RISK. Regime "
        "colour walks A → B → C → D. Predicted Ra approaches 1.6 µm. VB climbs toward 0.30 mm. "
        "Temperature lags power. Degradation probability rises earlier than the Ra trace, which is "
        "exactly what an early-warning head is for — and exactly why it must not be the emergency "
        "stop. When a typed hard-stop is crossed, the run halts and, if the mill is bridged, Hold is "
        "requested. Feature-contribution bars usually light vibration, chatter-band energy, force and "
        "the physics residual, which matches the story a manufacturing lecturer would tell.",
        first=True,
    )
    add_figure(doc, "fig2_regimes.png", "Figure 3.1: Latent regimes along a simulated Al 6061 end-milling run.")
    body(
        doc,
        "Figure 3.1 illustrates the four neighbourhoods along an accelerated cut. In the first seconds "
        "the simulator emits a relatively stationary vibration cloud, modest force, temperature still "
        "climbing toward its lagged steady state, and a small physics residual. The mixture assigns "
        "Regime A. Predicted Ra sits well below 1.6 µm. Tool health is near 100 % because VB is a "
        "small land. This is the cut a calendar-based shop would also accept. The difference is that "
        "the acceptance is now a recorded neighbourhood, not a habit.",
        first=True,
    )
    body(
        doc,
        "As accelerated wear grows, RMS, crest factor and chatter-band energy rise. The mixture weight "
        "shifts toward B and then C. The Ra head climbs. The risk head, looking thirty seconds ahead, "
        "is already high while current Ra is still legal. This is the early-warning interval the "
        "project exists to create. In a bad design the machine would hold here because a probability "
        "crossed 0.7. In this design the operator sees SURFACE RISK forming, sees estimated time of "
        "arrival to the typed Ra or VB stop, and decides. If a hard Ra or VB limit has been set, the "
        "supervisor eventually requests Hold and the visualisation mill freezes at pose. If not, the "
        "demonstration continues into Regime D so that the cliff can be watched. Both behaviours are "
        "useful. Only the first is a model of a cautious shop.",
    )
    body(
        doc,
        "The same walk-through on a real mill will differ in clock time, in the shape of the wear "
        "curve, and in the meaning of the mixture components. It should not differ in the ethics of "
        "the walk-through: probability informs, millimetres trip, Hold is not emergency stop, labels "
        "are declared. Any examiner with Python 3 and the requirements file can recreate the simulated "
        "figures. That repeatability is a strength. It is also a temptation to skip the laboratory. "
        "Reproducible simulation is treated as a necessary but not sufficient condition for a "
        "manufacturing thesis.",
    )

    section(doc, "3.3  Integration Observations")
    body(
        doc,
        "Several engineering facts appeared only when the mill and the monitor were connected. The "
        "visualisation mill’s Stop resets programme progress, so a “stop” that is implemented as Stop "
        "looks like a return to origin. Hold freezes the interpolator pose. A pose post on every "
        "animation frame can stall a threaded Python proxy. Reading the word Hold from the Hold button "
        "and treating it as machine state makes the bridge think the mill is always in feed-hold. "
        "HTTPS cannot phone home to HTTP. An integrated-development-environment preview draws buttons "
        "but does not reliably run the canvas or click handlers.",
        first=True,
    )
    body(
        doc,
        "Those observations are results of systems engineering. They belong in a B.Tech report because "
        "they are what a digital-manufacturing project actually spends time on. They also constrain "
        "the scientific claim: Cycle start is an observed event only when the mill page is served "
        "through the local HTTP proxy.",
    )

    section(doc, "3.4  Comparison with Alternative Strategies")
    body(
        doc,
        "Changing an end mill every N parts is easy to audit and wasteful. Tools that are still in "
        "Regime A are thrown away. Tools that entered Regime D early still cut scrap until the clock "
        "expires. The present system does not abolish planned tool change. It adds a reason to deviate: "
        "if VB and Ra forecasts stay flat, the tool is kept; if Regime C appears with a short estimated "
        "time of arrival to the Ra stop, the cycle is stopped and the surface is inspected.",
        first=True,
    )
    body(
        doc,
        "Commercial threshold boxes are mature and should be used for breakage and collision. They are "
        "not early surface-integrity predictors. They have no latent regime, no Ra head, no physics "
        "residual, and no notion of a 30 s horizon. The present project is complementary: a cheap "
        "analytical layer above, not a replacement of, a hardware trip. A large network trained on "
        "someone else’s prognostics dataset can win a paper metric and still be unusable on a college "
        "mill: no SensorFrame, no serial path, no operator limits, no Hold semantics, no honesty about "
        "labels. The present project inverts that priority. The model is small on purpose. The sockets "
        "and the safety wording are large on purpose.",
    )
    body(
        doc,
        "The literature sometimes infers residual stress from vibration. That can be a research goal "
        "if XRD is in the experimental plan. It is not better science to print the word integrity and "
        "mean residual stress when the only instrument is a dashboard. Integrity here means Ra-proxy "
        "plus wear and thermal drivers, until the laboratory book says otherwise.",
    )
    add_table(
        doc,
        "Table 3.1: Qualitative comparison of shop-floor strategies",
        ["Strategy", "When the surface loss is known", "Capital", "Explainable", "Safety honesty"],
        [
            ["Fixed-time tool change", "After the clock, often after the fail", "Low", "Yes (calendar)", "Does not touch interpolator"],
            ["Threshold TCM", "When a band exceeds a trip", "Medium–high", "Partial", "Good if hardware-rated"],
            ["Post-process Ra / vision", "After the pass", "Low–medium", "Yes", "High"],
            ["Deep PHM, no HMI", "When a score crosses a paper threshold", "Low software / high data", "Usually no", "Often over-claimed"],
            ["Commercial digital twin", "Vendor-defined", "High", "Vendor-dependent", "Vendor-dependent"],
            ["Present project", "Short horizon before Ra/VB limit, if labels are real", "Low", "Yes (regimes, µm, mm)", "Hold ≠ e-stop; sim ≠ lab"],
        ],
    )
    body(
        doc,
        "Table 3.1 is the comparison in one view. The last row is why the project is better for a "
        "college and an MSME, and not yet better for a certified cell. The software will not "
        "out-perform a well-tuned commercial breakage unit. It should not be sold as if it would. "
        "Its competitive position is early, inexpensive, multimodal, physics-annotated, regime-aware "
        "roughness warning with an honest integrity proxy. That niche is empty on most college mills "
        "and many job shops.",
        first=True,
    )

    section(doc, "3.5  Industry Impact and Markets")
    body(
        doc,
        "Milling cells lose money in four ordinary ways: scrap and rework when Ra or dimension fails; "
        "unplanned stops when a tool breaks or a chatter mark forces a re-cut; wasted tool life from "
        "conservative change-out; and idle spindles while a quality engineer walks a part to a "
        "metrology room. Industry notes compiled for this report place global tool-condition monitoring "
        "around USD 1.8 billion in the mid-2020s, with published compound-annual-growth figures in the "
        "roughly 9–12 % range depending on the analyst [Dataintelo, 2025]. Those figures are market "
        "context, not a revenue forecast for this repository. They explain why a mechanical project "
        "on early warning is not a toy theme.",
        first=True,
    )
    add_figure(doc, "fig6_market.png", "Figure 3.2: Indicative TCM market trajectory compiled from public forecasts.")
    body(
        doc,
        "Figure 3.2 is an indicative curve, not an econometric forecast and not a valuation of the "
        "present software. Sectors that feel an early Ra/VB warning include automotive tier suppliers "
        "milling aluminium housings; aerospace and defence shops machining 6061 and 7075 structures "
        "where documentation of process control is part of the contract; die-mould shops for which "
        "polishing time is labour; and medical and semiconductor equipment shops moving tolerances "
        "down. College and MSME shops are the near-term users of this exact stack: they will not buy "
        "a full digital twin, but they will run a laptop beside a mill if it speaks Ra and VB.",
        first=True,
    )
    add_table(
        doc,
        "Table 3.2: Stakeholder map",
        ["Stakeholder", "What changes if the idea is adopted", "What this B.Tech build already gives"],
        [
            ["Teaching laboratory", "A station between the mill and the profilometer", "Dashboard, simulator, serial path, honesty sentences"],
            ["MSME job shop", "Tool change by regime, not only by habit", "Architecture and Arduino path; not a certified product"],
            ["Tier-1 / OEM", "A clearer vendor brief for integrity TCM", "Named heads (Ra, VB, regime, limits)"],
            ["Tool vendor", "Telemetry for service contracts", "Wear-rate socket; no commercial contract"],
            ["Insurer / auditor", "A log of holds and regime shifts", "Concept only until labels are real"],
            ["Machine builder", "Possible documented feed-hold interlock", "Software Hold on a visualisation mill only"],
        ],
    )
    body(
        doc,
        "Table 3.2 separates who is helped now from who is only briefed. Helping a market is not the "
        "same as capturing it. The repository will not move the global TCM number. It helps the market "
        "in smaller, real ways. It trains buyers. A graduate who has implemented a SensorFrame will "
        "not buy a black box that cannot say whether it trips on probability or on millimetres. It "
        "trains vendors. A named list of heads and limits is a product specification. It trains "
        "colleges. Packaged laboratories can sell mill plus accelerometer plus this style of dashboard "
        "as one teaching stock-keeping unit. It trains policy talk. Industry 4.0 becomes a hold "
        "request and an Ra forecast instead of a poster in the corridor.",
        first=True,
    )
    add_figure(doc, "fig9_value.png", "Figure 3.3: Where an early Ra/VB warning can reduce shop cost (indicative, not a measured saving).")
    body(
        doc,
        "Figure 3.3 is an index of where savings could appear after labelled TCM; the percentages are "
        "teaching targets, not results. The following arithmetic is likewise a teaching model. Suppose "
        "a two-VMC aluminium cell scraps or reworks finish-related work, wastes carbide on conservative "
        "change-out, and loses spindle time to unplanned tool events and metrology walks, totalling "
        "₹80,000 a month of integrity-adjacent leakage. A 20 % reduction — the sort of number TCM "
        "vendors put on slides and that this project does not claim — would be ₹16,000 a month. An "
        "Arduino-class installation plus a used computer is far below that. A commercial TCM "
        "installation may be far above it and must be justified on breakage and collision as well as "
        "on Ra.",
        first=True,
    )
    add_table(
        doc,
        "Table 3.3: Indicative cost model for a two-VMC aluminium cell (teaching arithmetic only)",
        ["Leakage", "Illustrative monthly cost (INR)", "What an early Ra/VB warning attacks"],
        [
            ["Finish scrap / rework", "40,000", "Hold before the cloudy pass is completed"],
            ["Conservative insert waste", "15,000", "Keep Regime A tools in the spindle"],
            ["Unplanned stop + walk time", "25,000", "Estimated time of arrival and regime instead of surprise"],
            ["Total leakage (model)", "80,000", "Not a measured result of this B.Tech build"],
        ],
    )
    body(
        doc,
        "If measured Ra and VB replace simulated labels, the same interface becomes a candidate "
        "in-process capability study: Regime C predicts a failed Ra coupon with a stated false-alarm "
        "rate. That would justify keeping a tool one batch longer, or pulling a tool one batch earlier, "
        "with a quality record. If multiple machines share a regime model, plants get a common language "
        "(“B-to-C shifts on mill 4 after lunch”) instead of tribal operator lore. Those future impacts "
        "are conditional on data and on safety engineering that this B.Tech build does not pretend to "
        "have finished.",
        first=True,
    )
    body(
        doc,
        "Aluminium scrap is recyclable but not free: energy, logistics and schedule are lost when a "
        "plate is re-cut. Carbide tools have embodied energy and cobalt supply constraints. Using a "
        "tool to the last safe VB, and not past the Ra cliff, is a sustainability argument as well as "
        "a cost argument. The wear-rate head exists for that reason. Operators are not replaced by a "
        "mixture model. They are given a shared colour and a number they can argue with. The future "
        "skill is to disagree productively: the dashboard says C, the chips still look right, this "
        "pocket will be finished and measured. That disagreement is healthier than silent tribal "
        "knowledge and healthier than blind obedience to a probability.",
    )

    section(doc, "3.6  How the Results Must Be Read")
    body(
        doc,
        "The demonstration does not show a confusion matrix on profilometer Ra. It does not show a "
        "wear-land photograph. It does not show residual stress. It does not show that the mixture "
        "components found on the simulator are the same components a physical 6061 campaign would "
        "find. Table 3.4 states the claims that are made and the claims that are refused. A "
        "demonstration that looks more finished than it is is a form of academic harm. Every impressive "
        "clause in the title has a matching limitation sentence in the body.",
        first=True,
    )
    add_table(
        doc,
        "Table 3.4: Honest claims versus claims this report refuses",
        ["Sentence", "Status"],
        [
            ["A complete, runnable integrity-monitor stack was built", "Claimed"],
            ["GMM regimes and HGB heads run on a ten-dimensional multimodal vector", "Claimed"],
            ["A physics residual from P ≈ Fc · Vc is a first-class feature", "Claimed"],
            ["The dashboard can follow Cycle start / Hold on a bridged visualisation mill", "Claimed"],
            ["Ra is the B.Tech surface-integrity proxy", "Claimed"],
            ["Training labels in the present codebase are physics-simulated", "Claimed"],
            ["Software Hold is not a certified emergency stop", "Claimed"],
            ["Predicted Ra on the simulator equals laboratory profilometer Ra", "Refused"],
            ["GMM components on the simulator are the physical mill’s components", "Refused"],
            ["Residual stress / XRD maps were obtained", "Refused"],
            ["The Python process is a Category-0 or Category-1 stop", "Refused"],
            ["Global TCM growth is a revenue forecast for this repository", "Refused"],
            ["Table 3.3 savings were measured on a plant", "Refused"],
        ],
    )
    body(
        doc,
        "Table 3.4 is the results discipline of the project. Advanced, at B.Tech scale, does not mean "
        "a larger network. It means a problem that sits on manufacturing science, statistics, software "
        "architecture and safety language at once, and that refuses the cheap exits of fake XRD, fake "
        "emergency stop and fake laboratory error metrics.",
        first=True,
    )


def ch4(doc):
    chapter_title(doc, 4, "Conclusions and Scope for Future Work")
    section(doc, "4.1  Conclusions")
    body(
        doc,
        "The B.Tech project started from a clear industrial irritation: surface-integrity failure in "
        "aluminium milling is usually discovered too late. That irritation was turned into a complete, "
        "runnable system. Multimodal features, a physics residual, latent Gaussian-mixture regimes and "
        "small boosting heads feed a shop-floor dashboard. A supervisor respects operator-typed physical "
        "limits and refuses to treat degradation probability as an emergency stop. A mill bridge shows "
        "how a visualisation CNC without an application-programming interface can still start and freeze "
        "a monitor. Training is simulated; integrity is an Ra proxy; Hold is software. Those constraints "
        "are the scientific character of the work, not its failure.",
        first=True,
    )
    body(
        doc,
        "The aim stated in Chapter 1 was met at the level appropriate to this degree: a physics-informed "
        "multimodal monitor for latent regime discovery and early surface-integrity degradation prediction "
        "in CNC end milling of aluminium alloy was designed, implemented and demonstrated, and packaged "
        "as a usable dashboard with optional mill and data-acquisition linkage. The ideation survived "
        "because more glamorous architectures failed a constraint that a mechanical project must keep: "
        "measurable quantities, runnable software, and sentences that remain true when the mill is real.",
    )
    body(
        doc,
        "Relative to fixed-time tool change, the system adds a reason to keep or pull a tool based on "
        "regime and forecast rather than a calendar. Relative to threshold tool-condition monitoring, "
        "it adds an Ra head, a horizon and named neighbourhoods. Relative to opaque deep models, it "
        "keeps features a mechanical reader can point at. Relative to papers that promise residual "
        "stress without a diffractometer, it refuses the claim. The work is not better than a certified "
        "commercial breakage unit on a high-volume line. Claiming that would be a market lie.",
    )
    body(
        doc,
        "Industry is affected first as a teaching and MSME layer: a station between the mill and the "
        "profilometer, and an architecture a job shop can understand. Markets are helped when buyers, "
        "vendors, colleges and graduates share a narrower, truer sentence about what an integrity "
        "warning is. Global tool-condition-monitoring growth is context, not a revenue forecast for "
        "the repository. The future industrial impact, if the laboratory campaign is completed, is "
        "longer tool life, less scrap, and a common language for the statement that the cut has left "
        "the stable regime.",
    )
    body(
        doc,
        "Three sentences remain the conclusion as much as any metric. Simulated training is not a "
        "laboratory result. Ra is the B.Tech surface-integrity proxy. Software Hold is not a certified "
        "emergency stop. If those sentences are remembered, the artefact is usable. If they are "
        "forgotten, the artefact becomes a hazard.",
    )
    add_figure(doc, "fig10_roadmap.png", "Figure 4.1: Honest industrialisation path — measurement before productisation.")
    body(
        doc,
        "Figure 4.1 is the closing picture. Measurement comes before productisation. Machine builders "
        "still own safety. XRD still owns residual stress. A Python process is not an emergency stop. "
        "That picture is enough ambition for a mechanical B.Tech, and it is an honest one.",
        first=True,
    )

    section(doc, "4.2  Scope for Future Work")
    body(
        doc,
        "The next twelve months of a serious continuation are not the addition of transformers. They "
        "are measurement. A factorial on Al 6061 is to be booked: two speeds, two feeds, two worn "
        "states of the same four-flute mill. Vibration, current and temperature are to be logged. Ra "
        "is to be measured on a profilometer after each pass. VB is to be photographed. The monitor "
        "is then to be retrained on those labels. Precision and recall for the Ra-spec event, and "
        "calibration of the probability head, are to be reported. Only then is residual stress to be "
        "discussed, and only if XRD time is actually reserved.",
        first=True,
    )
    body(
        doc,
        "Software futures that are worth doing after labels exist include a National-Instruments "
        "DAQmx source behind the same SensorFrame; MTConnect spindle-load as a power proxy; a "
        "documented Hold via the real controller’s feed-hold bit under a safety review; a simple "
        "digital thread that stores regime traces with the job card; and a comparison against a "
        "threshold-only baseline on the same cuts. Software futures that are not worth doing first "
        "include generative G-code, reinforcement-learning feed override on an unguarded mill, or a "
        "public claim of certified emergency stop.",
    )
    body(
        doc,
        "Pedagogical futures include freezing the dashboard as a laboratory station where juniors "
        "must explain why Regime C appeared, and must write the three honesty sentences from memory. "
        "That may be a larger impact than any single error metric. In a cautious ten-year picture, "
        "teaching mills run a descendant of this dashboard as a standard laboratory. A fraction of "
        "MSMEs run an Arduino-class path and change tools when Regime C repeats. A fraction of tier "
        "plants use the named heads as acceptance tests when they buy commercial TCM. A few research "
        "groups replace the simulated labels and publish calibrated Ra-risk numbers for 6061, then "
        "for 7075, then for a steel. That picture is enough.",
    )


def references(doc):
    unnumbered_head(doc, "References")
    body(
        doc,
        "References are listed in the sequence they are cited, following the numbered format permitted "
        "by the departmental template. Style is kept uniform.",
        first=True,
    )
    gap(doc)
    items = [
        "Kalpakjian, S. and Schmid, S.R. (2014) Manufacturing Engineering and Technology. Pearson.",
        "Altintas, Y. (2012) Manufacturing Automation: Metal Cutting Mechanics, Machine Tool Vibrations, and CNC Design. Cambridge University Press.",
        "Tlusty, J. (2000) Manufacturing Processes and Equipment. Prentice Hall.",
        "ISO 8688-1/2. Tool life testing in milling. International Organization for Standardization.",
        "ISO 4287 / ISO 21920. Geometrical product specifications — Surface texture (Ra conventions).",
        "Taylor, F.W. (1907) On the art of cutting metals. Transactions of the ASME.",
        "Survey on machine learning applied to CNC milling processes (2025) Advances in Manufacturing. https://link.springer.com/article/10.1007/s40436-025-00564-x",
        "A novel simultaneous monitoring method for surface roughness and tool wear in milling process (2025) Scientific Reports. https://www.nature.com/articles/s41598-025-92178-3",
        "Intelligent real-time tool life prediction for a digital twin framework (2025) Journal of Intelligent Manufacturing. https://link.springer.com/article/10.1007/s10845-025-02606-4",
        "Dataintelo (2025) Tool Condition Monitoring Market Size, Share and Forecast Report 2025 to 2034. Market context only.",
        "scikit-learn documentation. GaussianMixture; HistGradientBoostingRegressor/Classifier.",
        "Streamlit documentation. Used for the shop-floor user interface.",
        "Department of Mechanical Engineering, Indian Institute of Technology Patna. B.Tech Thesis-or-Report template (MED).",
    ]
    for i, it in enumerate(items, 1):
        _p(doc, f"[{i}]  {it}", align="justify", first_indent=False, space_after=6)


def appendices(doc):
    unnumbered_head(doc, "Appendices")
    section(doc, "Appendix A  Default Process Parameters")
    body(
        doc,
        "Material Al 6061; operation end milling; tool diameter 10 mm; teeth 4; spindle 3000 r/min; "
        "feed 0.12 mm/tooth; depth of cut 1.0 mm; Ra specification 1.6 µm; sample rate 5000 Hz; "
        "window 0.25 s; dashboard refresh 400 ms; forecast horizon 30 s; VB demonstration limit "
        "0.30 mm. Source in the configuration file may be simulator, serial or http.",
        first=True,
    )
    section(doc, "Appendix B  How to Run the Demonstration")
    body(
        doc,
        "Python 3 is installed and the requirements file is applied. The dashboard is launched with "
        "python -m streamlit run dashboard/app.py --server.port 8501. Optionally, python scripts/cnc_bridge.py "
        "is run and http://127.0.0.1:8766/ is opened in Chrome or Edge (not an integrated-development-environment "
        "preview). Cycle start is pressed on the mill, or Start run on the monitor. Serial mode requires "
        "the Arduino firmware and a COM port.",
        first=True,
    )
    section(doc, "Appendix C  Feature List")
    body(
        doc,
        "Vibration RMS; kurtosis; crest factor; force RMS; force fluctuation; chatter-band energy; "
        "spectral entropy; temperature; spindle power; physics residual. These ten numbers are the "
        "feature names used by the model module.",
        first=True,
    )
    section(doc, "Appendix D  Risk Register")
    body(
        doc,
        "Risk: an examiner treats plots as laboratory data. Mitigation: trained_on string and Chapter 3 "
        "wording. Risk: an operator treats Hold as emergency stop. Mitigation: user-interface caption "
        "and this report. Risk: the mill tab freezes from a pose flood. Mitigation: throttled hook, "
        "single proxy process. Risk: mixed content blocks the start signal. Mitigation: local-area-network "
        "HTTP mill URL, not raw HTTPS. Risk: mixture components are uninterpretable on real data. "
        "Mitigation: keep the rule-based stand-in until clusters are named from chips and Ra coupons.",
        first=True,
    )
    section(doc, "Appendix E  Suggested Viva Questions")
    pairs = [
        "Why Al 6061? It is the alloy the teaching mill cuts and the alloy whose drawing specifies Ra.",
        "Why not residual stress? XRD was not booked; claiming it would be false.",
        "Why a Gaussian mixture and not a deep autoencoder? Four named neighbourhoods can be said aloud.",
        "Why gradient boosting and not a long short-term memory network? Tabular engineered features, 0.25 s windows, laptop training, inspectable contributions.",
        "Why a physics residual? Force and power cannot silently disagree.",
        "Why is risk not a trip? It rose early while the cut was still useful and would train operators to disable the system.",
        "Was a real CNC stopped? No. Software Hold on a visualisation mill is not an emergency stop.",
        "Are the plots laboratory results? No. They are simulated training and integration observations.",
        "How does this help the market? It trains buyers and colleges on a minimum integrity layer; it does not capture the tool-condition-monitoring market.",
        "What is done if the mill is available for a week? A factorial on speed and feed, measured Ra and VB, retrain, report calibration.",
    ]
    for ptxt in pairs:
        bullet(doc, ptxt)
    gap(doc)
    body(
        doc,
        "The contribution of this B.Tech project is a complete, honest, physics-informed multimodal "
        "monitor for latent regime discovery and early Ra-proxy integrity warning in Al 6061 end "
        "milling, with a shop-floor interface, operator-owned physical limits, optional serial "
        "data acquisition, and a mill bridge that respects Hold versus Stop. The contribution is "
        "not a certified safety function, not an XRD study, and not a measured plant saving. Those "
        "non-contributions are listed so that the real contribution remains visible.",
        first=True,
    )


def main():
    doc = Document()
    configure_styles(doc)

    # Section 0 — cover, no page number
    set_page_format(doc.sections[0], fmt="decimal", start=1, show_number=False)
    cover(doc)

    # Section 1 — front matter, lower roman starting at 1
    doc.add_section()
    set_page_format(doc.sections[1], fmt="lowerRoman", start=1, show_number=True)
    certificate(doc)
    declaration(doc)
    dedication(doc)
    acknowledgements(doc)
    abstract_page(doc)
    toc_and_lists(doc)

    # Section 2 — body, arabic starting at 1
    doc.add_section()
    set_page_format(doc.sections[2], fmt="decimal", start=1, show_number=True)
    ch1(doc)
    ch2(doc)
    ch3(doc)
    ch4(doc)
    references(doc)
    appendices(doc)

    doc.save(OUT)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
