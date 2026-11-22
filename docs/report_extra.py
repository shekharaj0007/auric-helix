"""Long additional chapters so the BTP report is a full research document."""


def add_table(doc, headers, rows, add_p, set_run_font):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.shared import Pt, RGBColor

    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        set_run_font(r, size=10, bold=True)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        from docx.oxml import OxmlElement

        tcpr = hdr[i]._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), "1F4E79")
        shd.set(qn("w:val"), "clear")
        tcpr.append(shd)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ""
            p = cell.paragraphs[0]
            r = p.add_run(str(val))
            set_run_font(r, size=10)
    doc.add_paragraph()
    return table


def contents_page(doc, add_h, add_p, add_bullet):
    add_h(doc, "Contents", 1)
    add_p(
        doc,
        "The report is organised as a full B.Tech research document. Front matter states authorship and limits. "
        "Chapters 1–3 fix ideation, literature and the problem. Chapters 4–6 are method, architecture and the "
        "implemented repository. Chapter 7 is results discipline. Chapters 8–9 compare alternatives and treat "
        "industry and markets. Chapters 10–11 are future work and conclusion. Extended chapters (1A–9A and 12–15) "
        "carry the deeper research discussion required of a thirty-page thesis-style report. Appendices hold "
        "parameters, run instructions, features, ideation history, scenarios, risks, glossary and a viva script.",
        first_line=False,
    )
    items = [
        "Declaration, certificate, acknowledgements, abstract, abbreviations",
        "Chapter 1 — Introduction and ideation",
        "Chapter 1A — Socio-technical ideation",
        "Chapter 2 — Background and related work",
        "Chapter 2A — Mechanics the models are allowed to see",
        "Chapter 3 — Problem statement, motivation and research questions",
        "Chapter 4 — Methodology",
        "Chapter 4A — Learning details",
        "Chapter 5 — System architecture",
        "Chapter 5A — Networking facts that affected the science",
        "Chapter 6 — Implementation of the present repository",
        "Chapter 7 — Results and how they must be read",
        "Chapter 8 — Why this is better than common alternatives",
        "Chapter 8A — Comparison table in prose",
        "Chapter 9 — Industry impact, markets and who is helped",
        "Chapter 9A — Market mechanisms",
        "Chapter 10 — Future work",
        "Chapter 11 — Conclusion",
        "Chapter 12 — Detailed ideation narrative and design rationale",
        "Chapter 13 — Why the project is being done (academic, industrial, national)",
        "Chapter 14 — Future impacts, industry change and market help",
        "Chapter 15 — Worked simulated campaign, economics and ethics",
        "References",
        "Appendices A–H",
    ]
    for it in items:
        add_bullet(doc, it)
    add_h(doc, "List of figures", 1)
    figs = [
        "Figure 1. End-to-end architecture of the machining integrity monitor",
        "Figure 2. Latent regimes along a simulated Al 6061 end-milling run",
        "Figure 3. Taylor-type flank-wear growth used in the physics simulator",
        "Figure 4. Feature pipeline from a SensorFrame to the model heads",
        "Figure 5. Positioning against common shop-floor strategies",
        "Figure 6. Indicative TCM market trajectory",
        "Figure 7. Sensor paths that collapse into one SensorFrame",
        "Figure 8. Supervisor logic: physical limits trip, risk informs",
        "Figure 9. Where an early Ra/VB warning can reduce shop cost (indicative)",
        "Figure 10. Honest industrialisation path",
    ]
    for f in figs:
        add_bullet(doc, f)
    add_h(doc, "List of tables", 1)
    for t in [
        "Table 1. Default process window used in the implemented system",
        "Table 2. Feature vector used by GMM and HGB heads",
        "Table 3. Qualitative comparison of shop-floor strategies",
        "Table 4. Stakeholder map: who is helped and how",
        "Table 5. Indicative cost model for a two-VMC aluminium cell",
        "Table 6. Honest claims versus claims this report refuses",
    ]:
        add_bullet(doc, t)
    doc.add_page_break()


def ch12(doc, add_h, add_p, add_bullet, add_fig):
    doc.add_page_break()
    add_h(doc, "Chapter 12  Detailed ideation narrative and design rationale", 1)
    add_h(doc, "12.1 How the idea was formed", 2)
    add_p(
        doc,
        "The project did not begin as a machine-learning title. It began as a shop observation that every "
        "mechanical student has seen: a part leaves the vice looking acceptable under fluorescent light and fails "
        "a roughness check an hour later. The operator already knew something was changing — the spindle note, "
        "the chip colour, the way the cutter “pushed” — but that knowledge was not written down, not shared with "
        "the next shift, and not attached to the job card. The first ideation question was therefore not “which "
        "neural network?” It was: can we turn the operator’s late, tacit sense that the cut is leaving the good "
        "regime into an early, shared, numerical warning that a second person can read?",
    )
    add_p(
        doc,
        "That question immediately split into three design problems. The sensing problem: which quantities can a "
        "college or an MSME actually measure during a cut? The modelling problem: which representation keeps "
        "manufacturing meaning instead of hiding it in an embedding? The human problem: which interface will a "
        "mechanical supervisor trust enough not to switch off? The architecture of the repository is the answer "
        "to those three problems taken together. A SensorFrame is the sensing answer. A ten-dimensional feature "
        "vector plus a Gaussian mixture plus small boosting heads is the modelling answer. A Streamlit dashboard "
        "with typed physical limits and a refusal to trip on probability is the human answer.",
    )
    add_h(doc, "12.2 Why aluminium 6061 and why this process window", 2)
    add_p(
        doc,
        "Aluminium 6061 is the default workpiece because it is the alloy a teaching mill actually cuts: plates "
        "are cheap, chips are manageable, cutting speeds around 90–100 m/min are conventional, and the drawing "
        "almost always specifies Ra rather than a residual-stress envelope. A 10 mm four-flute end mill at "
        "3000 r/min and 0.12 mm/tooth is a window a student can picture. Axial depth 1.0 mm keeps the demo in "
        "a finishing/semi-finishing story rather than a roughing story. The Ra specification of 1.6 µm is a "
        "common general-engineering finish, tight enough that wear and chatter will violate it, loose enough "
        "that the first seconds of a sharp tool are clearly legal. Choosing titanium or hardened die steel "
        "would have made a more dramatic paper title and an unfinishable laboratory.",
    )
    add_p(
        doc,
        "The same window is also industrially honest. Automotive housings, pneumatic manifolds, jigs, fixtures "
        "and many 6061 aerospace brackets live in this neighbourhood of speeds and finishes. A monitor that "
        "cannot speak to this window cannot speak to the shops that would actually try it. Exotic process "
        "windows belong in a later campaign, after the SensorFrame and the HMI have been proven on the alloy "
        "the laboratory already stocks.",
    )
    add_h(doc, "12.3 Why latent regimes instead of a fault dictionary", 2)
    add_p(
        doc,
        "A fault dictionary is attractive in a slide: chatter, built-up edge, rubbing, tool breakage, coolant "
        "starvation. It is expensive in a laboratory because every window needs a human name, and two instructors "
        "will disagree on the name of a transitional cut. Latent regime discovery postpones the naming. The "
        "mixture model finds neighbourhoods in feature space. The engineer later says: this neighbourhood is "
        "the cut we accept; this neighbourhood is the cut we watch; this neighbourhood is the cut we stop. "
        "That is closer to how a skilled operator already thinks — “it doesn’t sound like itself any more” — "
        "than a twenty-class classifier trained on someone else’s mill.",
    )
    add_p(
        doc,
        "Four regimes were chosen because they map onto a shop sentence. A is the sentence “leave it.” B is "
        "“watch the next thirty seconds.” C is “finish this feature and inspect.” D is “hold and change the "
        "tool.” Three regimes collapsed B into A on simulated data. Five regimes split D into two colours "
        "nobody could explain. Four is therefore not a universal constant. It is the smallest set of colours "
        "that survived both the simulated cloud and a sentence test with a mechanical reader.",
    )
    add_h(doc, "12.4 Why physics is a residual and not a full twin", 2)
    add_p(
        doc,
        "A digital twin of milling can mean a time-domain cutting-force simulation, a finite-element chip, a "
        "thermal-mechanical residual-stress solve, or a plant-wide OPC-UA graph. None of those twins run in "
        "250 ms on a laptop beside a teaching mill, and none of them are identified from the sensors this "
        "project can afford. The physics that is kept is the identity an undergraduate already writes: cutting "
        "power should be consistent with cutting force and cutting speed, plus a roughly constant idle term. "
        "The residual of that identity is a feature. When it grows, either the process or the sensing chain "
        "has left the model the student can defend on a whiteboard. That is physics-informed learning at the "
        "correct scale for this degree.",
    )
    add_h(doc, "12.5 Why the browser mill belongs in the ideation", 2)
    add_p(
        doc,
        "A monitor that only starts from a Streamlit button is a software demo. A monitor that starts when a "
        "human presses Cycle start is a process demo. The laboratory had a second laptop running a ForgeMill "
        "visualisation. That mill has no telemetry API. The ideation therefore expanded: treat the mill page "
        "as an experimental apparatus that must be instrumented, even if the instrumentation is a local reverse "
        "proxy and a JavaScript hook. That decision pulled HTTP, mixed content, Hold-versus-Stop semantics and "
        "LAN serving into a mechanical project. Those topics are not decorations. They decide whether “the cut "
        "has started” is an observed event or a fiction.",
    )
    add_h(doc, "12.6 Ideas that were rejected, and why rejection is part of research", 2)
    rejected = [
        "A live stylus roughness meter mounted on the spindle. Not available, not safe, and not how Ra is measured.",
        "A residual-stress predictor from vibration alone. Dishonest without XRD or at least a published transfer study on this alloy and tool.",
        "Reinforcement-learning feed override. Changes the interpolator without a risk assessment; not a B.Tech deliverable.",
        "A large convolutional network on raw 5 kHz traces. Uninterpretable to the examiner who must sign the certificate, and hungry for labelled cuts we do not have.",
        "Automatic e-stop from degradation probability. Observed to trip the demo while the cut was still useful; trains the operator to disable the system.",
        "Using ForgeMill Stop as if it were Hold. Stop resets programme progress and snaps the DRO home; that is not a feed-hold.",
    ]
    for r in rejected:
        add_bullet(doc, r)
    add_p(
        doc,
        "Each rejection left a sentence in the code or the UI. Research ideation is not the accumulation of "
        "fashionable modules. It is the set of refusals that keep the remaining modules true.",
    )
    add_h(doc, "12.7 The one-sentence ideation that the rest of the report expands", 2)
    add_p(
        doc,
        "Build an early, explainable, physically constrained warning that a milling cut of Al 6061 is leaving "
        "the regime in which Ra will remain inside specification, using signals a college can acquire, models "
        "a mechanical engineer can defend, and a hold request that nobody confuses with an emergency stop.",
    )


def ch13(doc, add_h, add_p, add_bullet, add_fig, add_table, set_run_font):
    doc.add_page_break()
    add_h(doc, "Chapter 13  Why this project is being done", 1)
    add_h(doc, "13.1 The academic reason", 2)
    add_p(
        doc,
        "A Bachelor of Technology in Mechanical Engineering is no longer only a course in machines, materials "
        "and manufacturing processes. Accreditation bodies and employers ask graduates to connect a process to "
        "data, to state uncertainty, and to keep safety language exact. This project is being done so that the "
        "student must practise all three. Connecting a process to data is the SensorFrame and the feature "
        "vector. Stating uncertainty is the GMM confidence, the probability head, and the written limit that "
        "simulated labels are not laboratory results. Keeping safety language exact is the repeated sentence "
        "that software Hold is not a certified e-stop and that the supervisor is not a certified CNC safety "
        "authority.",
    )
    add_p(
        doc,
        "There is a second academic reason. Many student “AI in manufacturing” reports are literature reviews "
        "with a downloaded dataset and a confusion matrix. They do not produce an artefact another person can "
        "run beside a machine. This project is being done to produce that artefact: a repository with a "
        "dashboard, a trainer, a simulator, a serial path, a mill bridge and a config file. The artefact is "
        "the thesis object. Editors can later replace the simulated labels. They should not have to invent "
        "the sockets.",
    )
    add_h(doc, "13.2 The industrial reason", 2)
    add_p(
        doc,
        "Industry is doing in-process monitoring because post-process inspection is late. When Ra fails, the "
        "surface already exists. When a tool breaks, the cycle already stopped. When a tool is changed too "
        "early, carbide and spindle time are already wasted. The industrial reason for this project is to "
        "show, at student scale, the information layer that sits between those three losses: a short-horizon "
        "estimate of regime, roughness, wear and temperature, shown in shop units, with an operator-owned "
        "limit. Plants that already own Marposs, ARTIS or TMAC stacks do not need this repository as a "
        "product. Plants and colleges that own none of those stacks need a picture of what the first layer "
        "looks like. This project is that picture.",
    )
    add_h(doc, "13.3 The national and MSME reason", 2)
    add_p(
        doc,
        "Indian job shops are being asked for documented quality by export customers and by larger domestic "
        "OEMs. They rarely have a metrology room on every shift. They do have used PCs, cheap microcontrollers "
        "and operators who already hear the cut. A monitor that starts on that equipment is a more realistic "
        "national intervention than a lecture on digital twins that assumes OPC-UA, a historian and a six-figure "
        "licence. The project is being done to put a concrete, limited, honest stack in that gap. If it is "
        "later replaced by a vendor product, it has still done the national job: the shop now knows which "
        "questions to ask the vendor.",
    )
    add_h(doc, "13.4 The pedagogical reason inside the department", 2)
    add_p(
        doc,
        "Manufacturing laboratories teach speeds and feeds, then teach a profilometer, then teach a toolmaker’s "
        "microscope if one exists. They rarely teach the hour between those instruments. This project occupies "
        "that hour. A junior batch can be asked to explain why Regime C appeared, to type a hard-stop, and to "
        "write the three honesty sentences from memory. That exercise is why the department should keep the "
        "dashboard even if a later student throws away the simulated trainer. The project is being done to "
        "leave a station, not only a bound report.",
    )
    add_h(doc, "13.5 The research-gap reason", 2)
    add_p(
        doc,
        "The 2025 milling-and-learning literature is rich in wear-stage classification, VB regression, chatter "
        "detection and roughness prediction. It is thinner on systems that do all of the following at once: "
        "(i) multimodal features including a mechanics residual; (ii) unsupervised regime discovery named for "
        "an operator; (iii) short-horizon integrity risk that is not allowed to become an e-stop; (iv) a "
        "runnable HMI; (v) an explicit B.Tech integrity proxy (Ra, not XRD); (vi) a written refusal to treat "
        "simulator RMSE as a laboratory result. This project is being done to occupy that combined gap. It is "
        "not being done to beat a public PHM leaderboard.",
    )
    add_h(doc, "13.6 What would be lost if the project were not done", 2)
    add_p(
        doc,
        "If the project were not done, the department would still have papers on TCM and still have a mill. "
        "What would be lost is the joining tissue: a student who has fought Hold-versus-Stop, mixed content, "
        "probability-versus-hard-stop, and the temptation to write “residual stress” on a cover page. Those "
        "fights are the education. The report records them so that the next student does not have to rediscover "
        "them as folklore.",
    )
    add_fig(doc, "fig7_sensors.png", "Figure 7. Sensor paths that collapse into one SensorFrame.")


def ch14(doc, add_h, add_p, add_bullet, add_fig, add_table, set_run_font):
    doc.add_page_break()
    add_h(doc, "Chapter 14  Future impacts, industry change and market help", 1)
    add_h(doc, "14.1 Immediate impact (this academic year)", 2)
    add_p(
        doc,
        "The immediate impact is local and real. A runnable monitor exists. A supervisor can be shown regimes, "
        "Ra, VB, temperature and ETA without opening an IDE. A second laptop can start and freeze the "
        "visualisation mill through a LAN bridge. Training scripts exist so that a later labelled CSV can "
        "replace the simulator without rewriting the dashboard. Those are impacts because they change what "
        "the laboratory can demonstrate tomorrow morning. They are not yet impacts on a production OEE chart.",
    )
    add_h(doc, "14.2 Impact on the machining industry if the lab campaign is completed", 2)
    add_p(
        doc,
        "The machining industry does not change because a student fitted a GMM. It changes when a cell has a "
        "documented reason to keep a tool one batch longer or to pull a tool one batch earlier, and when that "
        "reason is written in Ra and VB rather than in operator mood. If a labelled Al 6061 campaign shows "
        "that Regime C predicts an Ra-spec failure with a stated false-alarm rate, then three industrial "
        "behaviours become negotiable. Tool stores can stop issuing inserts on a pure calendar. Quality can "
        "reduce the fraction of parts that walk to a profilometer after every pass. Production can hold a "
        "cut before a cloudy finish is cut into a plate that has already consumed roughing time.",
    )
    add_p(
        doc,
        "Those behaviours compound. Less scrap is not only metal. It is schedule, fixturing, inspection and "
        "customer confidence. Less unplanned stop is not only a tool. It is a night shift that finishes the "
        "list. Less wasted tool life is not only carbide. It is cobalt, grinding energy and purchase-order "
        "noise. An early-warning layer is therefore not a gadget on the spindle housing. It is a small change "
        "to how a cell talks about “good enough to continue.”",
    )
    add_h(doc, "14.3 How different industry layers are affected", 2)
    add_p(
        doc,
        "Job shops are affected first because they have the least metrology and the most to gain from a laptop "
        "that speaks micrometres. They must also be protected from over-claim: this stack is not a CE-marked "
        "TCM. Tier suppliers are affected as a specification. They already buy commercial monitoring; they "
        "need a clearer brief for what “integrity warning” means besides breakage. Aerospace and defence "
        "shops are affected as documentation: a regime trace attached to a job card is a process-control "
        "sentence an auditor can read, provided the labels are real. Tool vendors are affected as a future "
        "service model: wear-rate traces are the telemetry that “tools as a service” would require. Machine-tool "
        "builders are affected only later, if Hold is ever wired to a real feed-hold bit under a safety review. "
        "This B.Tech build does not claim that wiring.",
    )
    add_table(
        doc,
        ["Stakeholder", "What changes if the idea is adopted", "What this B.Tech build already gives"],
        [
            ["Teaching laboratory", "A station between the mill and the profilometer", "Dashboard, simulator, serial path, three honesty sentences"],
            ["MSME job shop", "Tool change by regime, not only by habit", "Architecture and Arduino path; not a certified product"],
            ["Tier-1 / OEM", "A clearer vendor brief for integrity TCM", "Named heads (Ra, VB, regime, limits)"],
            ["Tool vendor", "Telemetry for service contracts", "Wear-rate socket; no commercial contract"],
            ["Insurer / auditor", "A log of holds and regime shifts", "Concept only until labels and time-stamps are real"],
            ["Machine builder", "Possible documented feed-hold interlock", "Software Hold on a visualisation mill only"],
        ],
        add_p,
        set_run_font,
    )
    add_p(doc, "Table 4. Stakeholder map: who is helped and how.", italic=True, align="center", first_line=False)
    add_h(doc, "14.4 Why the approach is better than alternatives the industry already has", 2)
    add_p(
        doc,
        "The industry already has calendars, threshold boxes, vision inspection and expensive twins. This "
        "approach is better than a calendar because it uses the tool’s actual state. It is better than a "
        "threshold box for integrity because it forecasts Ra and names a regime instead of waiting for a "
        "broken tooth. It is better than post-process vision because it speaks during the cut. It is better "
        "than an opaque deep model for a college and an MSME because a mechanical reader can point at RMS, "
        "chatter band and a power residual. It is not better than a certified commercial TCM at catching a "
        "catastrophic insert failure on a high-volume line. Claiming that would be a market lie. The "
        "competitive sentence is narrower and stronger: for early, cheap, explainable roughness-and-wear "
        "warning with an honest proxy, this architecture is a better first layer than anything those shops "
        "currently run, which is usually nothing.",
    )
    add_h(doc, "14.5 How the project helps markets, as distinct from “disrupting” them", 2)
    add_p(
        doc,
        "Helping a market is not the same as capturing it. The TCM market is already growing because plants "
        "want less downtime; public notes in the mid-2020s put the category near USD 1.8 billion with "
        "high-single-digit to low-double-digit CAGR depending on the analyst. This repository will not move "
        "that number. It helps the market in four smaller, real ways. It trains buyers. A graduate who has "
        "implemented a SensorFrame will not buy a black box that cannot say whether it trips on probability "
        "or on millimetres. It trains vendors. A named list of heads and limits is a product specification. "
        "It trains colleges. Packaged labs can sell mill plus accelerometer plus this style of dashboard as "
        "one teaching SKU. It trains policy talk. “Industry 4.0” becomes a hold request and an Ra forecast "
        "instead of a poster in the corridor.",
    )
    add_p(
        doc,
        "A fifth help is negative and important. The project helps markets by refusing to pollute them with "
        "a student claim of certified safety or XRD integrity. Markets are harmed when academic prototypes "
        "are described as plant-ready. The report’s limitations are therefore a market contribution. They "
        "keep the idea investable later because they kept it true now.",
    )
    add_fig(doc, "fig9_value.png", "Figure 9. Where an early Ra/VB warning can reduce shop cost (indicative, not a measured saving from this repository).")
    add_h(doc, "14.6 Future impacts on quality systems and digital threads", 2)
    add_p(
        doc,
        "If regime traces, predicted Ra, measured Ra and Hold events are stored with the job card, the shop "
        "gains a digital thread at the scale it can afford: a CSV and a screenshot, not a PLM suite. Quality "
        "engineers can then ask a new question: which regime was the cut in when this coupon failed? That "
        "question is more powerful than “what was the programmed feed?” because it includes the tool’s ageing "
        "and the cut’s vibration neighbourhood. Future ISO-adjacent quality talk — capability, traceability, "
        "process control — can attach to that question. This project does not implement a certified QMS "
        "module. It shows the record such a module would ingest.",
    )
    add_h(doc, "14.7 Future impacts on sustainability and resource markets", 2)
    add_p(
        doc,
        "Carbide, cobalt and aluminium recycling are resource markets as well as shop costs. Using a tool to "
        "the last safe VB, and not past the Ra cliff, reduces both insert consumption and plate scrap. Those "
        "are small percentages on one vice and large tonnages across a national MSME base. The wear-rate head "
        "exists to make that trade visible in micrometres per second. Future impact here is conditional: only "
        "measured VB photographs and measured Ra make the trade trustworthy. Until then the sustainability "
        "sentence is a direction, not a tonne of CO2 avoided.",
    )
    add_h(doc, "14.8 Future impacts on people and skills", 2)
    add_p(
        doc,
        "Operators are not replaced by a GMM. They are given a shared colour and a number they can argue with. "
        "The future skill is to disagree productively: “the dashboard says C, the chips still look right, we "
        "will finish this pocket and measure.” That disagreement is healthier than silent tribal knowledge and "
        "healthier than blind obedience to a probability. Colleges that teach this skill send a different "
        "graduate into the market — one who can sit between a spindle and a model. That is a labour-market "
        "impact of the project even if no licence is sold.",
    )
    add_h(doc, "14.9 A ten-year industrial picture, kept honest", 2)
    add_p(
        doc,
        "In a cautious ten-year picture, teaching mills run a descendant of this dashboard as a standard lab. "
        "A fraction of MSMEs run an Arduino-class path and change tools when Regime C repeats. A fraction of "
        "tier plants use the named heads as acceptance tests when they buy commercial TCM. A few research "
        "groups replace the simulated labels and publish calibrated Ra-risk numbers for 6061, then for 7075, "
        "then for a steel. Machine builders still own safety. XRD still owns residual stress. Nobody calls a "
        "Python process an e-stop. That picture is enough. A louder picture — autonomous feed override on "
        "unguarded mills, residual stress from a cheap accelerometer, a student startup valued as if it were "
        "a safety PLC — is not a future impact this report is willing to advertise.",
    )
    add_fig(doc, "fig10_roadmap.png", "Figure 10. Honest industrialisation path — measurement before productisation.")
    add_fig(doc, "fig8_supervisor.png", "Figure 8. Supervisor logic: physical limits trip, risk informs.")


def ch15(doc, add_h, add_p, add_bullet, add_fig, add_table, set_run_font):
    doc.add_page_break()
    add_h(doc, "Chapter 15  Worked simulated campaign, economics and ethics", 1)
    add_h(doc, "15.1 A worked walk-through of one simulated cut", 2)
    add_p(
        doc,
        "Consider a default run: Al 6061, 10 mm four-flute, 3000 r/min, 0.12 mm/tooth, 1.0 mm depth, Ra spec "
        "1.6 µm, VB demo limit 0.30 mm. In the first seconds the simulator emits a relatively stationary "
        "vibration cloud, modest force, temperature still climbing toward its lagged steady state, and a small "
        "physics residual. The GMM assigns Regime A. Predicted Ra sits well below 1.6 µm. Tool health is near "
        "100 % because VB is a small land. The dashboard says STABLE. This is the cut a calendar-based shop "
        "would also accept. The difference is that the acceptance is now a recorded neighbourhood, not a habit.",
    )
    add_p(
        doc,
        "As accelerated wear grows, RMS, crest factor and chatter-band energy rise. The mixture weight shifts "
        "toward B and then C. The Ra head climbs. The risk head, looking thirty seconds ahead, is already "
        "high while current Ra is still legal. This is the early-warning interval the project exists to "
        "create. In a bad design the machine would hold here because a probability crossed 0.7. In this design "
        "the operator sees SURFACE RISK forming, sees ETA to the typed Ra or VB stop, and decides. If they "
        "have set a hard Ra or VB limit, the supervisor eventually requests Hold and the visualisation mill "
        "freezes at pose. If they have not, the demo will continue into Regime D so that the student can watch "
        "the cliff. Both behaviours are useful. Only the first is a model of a cautious shop.",
    )
    add_p(
        doc,
        "The same walk-through on a real mill will differ in clock time, in the shape of the wear curve, and "
        "in the meaning of the GMM components. It should not differ in the ethics of the walk-through: "
        "probability informs, millimetres trip, Hold is not e-stop, labels are declared.",
    )
    add_h(doc, "15.2 Default process window as a table", 2)
    add_table(
        doc,
        ["Quantity", "Symbol / name", "Default value", "Role in the monitor"],
        [
            ["Workpiece", "Al 6061", "T6 plate (assumed)", "Alloy the models and HMI speak"],
            ["Tool diameter", "D", "10 mm", "Sets cutting speed with rpm"],
            ["Teeth", "z", "4", "Tooth-passing frequency 200 Hz at 3000 r/min"],
            ["Spindle speed", "n", "3000 r/min", "Process window; also a training axis"],
            ["Feed per tooth", "fz", "0.12 mm/tooth", "Chip load; training axis 0.08–0.18"],
            ["Axial depth", "ap", "1.0 mm", "Finishing / semi-finishing story"],
            ["Ra specification", "Ra,lim", "1.6 µm", "B.Tech integrity proxy threshold"],
            ["VB demo limit", "VB,lim", "0.30 mm", "ISO 8688-style 100 % wear for demo"],
            ["Window length", "Tw", "0.25 s", "Feature frame"],
            ["Sample rate", "fs", "5000 Hz", "Simulator / Arduino target"],
            ["Horizon", "Δt", "30 s", "Risk head look-ahead"],
            ["Refresh", "—", "400 ms", "Dashboard loop"],
        ],
        add_p,
        set_run_font,
    )
    add_p(doc, "Table 1. Default process window used in the implemented system.", italic=True, align="center", first_line=False)
    add_h(doc, "15.3 Feature vector as a table", 2)
    add_table(
        doc,
        ["Feature", "Domain", "Why a manufacturing reader keeps it"],
        [
            ["Vibration RMS", "Time", "Energy of the cut; rises with chatter and wear"],
            ["Kurtosis", "Time", "Spikiness; early departure from a Gaussian rub"],
            ["Crest factor", "Time", "Peak-to-RMS; impacts and intermittent chatter"],
            ["Force RMS", "Time", "Load; related to chip thickness and dulling"],
            ["Force fluctuation", "Time", "Unsteady cutting, BUE, runout"],
            ["Chatter-band energy", "Frequency", "Energy away from tooth-passing line"],
            ["Spectral entropy", "Frequency", "Loss of a clean tonal cut"],
            ["Temperature", "Thermal", "Lagged bulk / sensor temperature"],
            ["Spindle power", "Energy", "What the motor is actually spending"],
            ["Physics residual", "Mechanics", "Disagreement of P with Fc · Vc + idle"],
        ],
        add_p,
        set_run_font,
    )
    add_p(doc, "Table 2. Feature vector used by GMM and HGB heads.", italic=True, align="center", first_line=False)
    add_h(doc, "15.4 Comparison of strategies as a table", 2)
    add_table(
        doc,
        ["Strategy", "When it knows the surface is lost", "Capital", "Explainable to a mechanical supervisor", "Safety honesty"],
        [
            ["Fixed-time tool change", "After the clock, often after the fail", "Low", "Yes (calendar)", "High — does not touch the interpolator"],
            ["Threshold TCM", "When a band exceeds a trip", "Medium–high", "Partial (one number)", "Good if hardware-rated"],
            ["Post-process Ra / vision", "After the pass", "Low–medium", "Yes", "High"],
            ["Deep PHM, no HMI", "When a score crosses a paper threshold", "Low software / high data", "Usually no", "Often over-claimed"],
            ["Commercial digital twin", "Vendor-defined", "High", "Vendor-dependent", "Vendor-dependent"],
            ["This project", "Short horizon before Ra/VB limit, if labels are real", "Low", "Yes (regimes, µm, mm)", "Explicit: Hold ≠ e-stop; sim ≠ lab"],
        ],
        add_p,
        set_run_font,
    )
    add_p(doc, "Table 3. Qualitative comparison of shop-floor strategies.", italic=True, align="center", first_line=False)
    add_h(doc, "15.5 Indicative economics for a two-VMC aluminium cell", 2)
    add_p(
        doc,
        "The following arithmetic is a teaching model, not a measured saving from this repository. Suppose a "
        "two-VMC aluminium cell scraps or reworks ₹40,000 of finish-related work in a month, wastes ₹15,000 "
        "of carbide on conservative change-out, and loses ₹25,000 of spindle time to unplanned tool events "
        "and metrology walks. That is ₹80,000 a month of integrity-adjacent leakage. A 20 % reduction — the "
        "sort of number TCM vendors put on slides and that this project does not claim — would be ₹16,000 a "
        "month. An Arduino-class installation plus a used PC is far below that. A commercial TCM installation "
        "may be far above it and must be justified on breakage and collision as well as on Ra. The point of "
        "the arithmetic is to show the order of the market the idea speaks to: a shop can think about this "
        "layer in tens of thousands of rupees per month, not only in millions of dollars of global CAGR.",
    )
    add_table(
        doc,
        ["Leakage", "Illustrative monthly cost (INR)", "What an early Ra/VB warning attacks"],
        [
            ["Finish scrap / rework", "40,000", "Hold before the cloudy pass is completed"],
            ["Conservative insert waste", "15,000", "Keep Regime A tools in the spindle"],
            ["Unplanned stop + walk time", "25,000", "ETA and regime instead of surprise"],
            ["Total leakage (model)", "80,000", "Not a measured result of this B.Tech build"],
        ],
        add_p,
        set_run_font,
    )
    add_p(doc, "Table 5. Indicative cost model for a two-VMC aluminium cell (teaching arithmetic only).", italic=True, align="center", first_line=False)
    add_h(doc, "15.6 Claims this report makes and refuses", 2)
    add_table(
        doc,
        ["Sentence", "Status in this report"],
        [
            ["A complete, runnable integrity-monitor stack was built", "Claimed"],
            ["GMM regimes and HGB heads run on a ten-dimensional multimodal vector", "Claimed"],
            ["A physics residual from P ≈ Fc · Vc is a first-class feature", "Claimed"],
            ["The dashboard can follow Cycle start / Hold on a bridged visualisation mill", "Claimed"],
            ["Ra is the B.Tech surface-integrity proxy", "Claimed"],
            ["Training labels in the present codebase are physics-simulated", "Claimed"],
            ["Software Hold is not a certified e-stop", "Claimed"],
            ["The supervisor is not a certified CNC safety authority", "Claimed"],
            ["Predicted Ra on the simulator equals laboratory profilometer Ra", "Refused"],
            ["GMM components on the simulator are the physical mill’s components", "Refused"],
            ["Residual stress / XRD maps were obtained", "Refused"],
            ["The Python process is a Category-0 or Category-1 stop", "Refused"],
            ["Global TCM CAGR is a revenue forecast for this repository", "Refused"],
            ["Table 5 savings were measured on a plant", "Refused"],
        ],
        add_p,
        set_run_font,
    )
    add_p(doc, "Table 6. Honest claims versus claims this report refuses.", italic=True, align="center", first_line=False)
    add_h(doc, "15.7 Ethics of demonstration", 2)
    add_p(
        doc,
        "A demonstration that looks more finished than it is is a form of academic harm. It teaches the next "
        "student to inflate, and it teaches a shop to trust a hold that is not rated. The ethical rule used "
        "here is symmetry: every impressive sentence in the title has a matching limitation sentence in the "
        "body. Physics-informed is matched by “not a residual-stress FEM.” Latent regime discovery is matched "
        "by “components named after clustering, to be renamed on real chips.” Early prediction is matched by "
        "“simulated labels until a campaign is booked.” Surface integrity is matched by “Ra proxy, not XRD.” "
        "CNC milling is matched by “visualisation mill plus optional serial DAQ.” Aluminium alloy is matched "
        "by “default 6061, not a catalogue of alloys.”",
    )
    add_p(
        doc,
        "A second ethical rule is operator dignity. The dashboard does not hide the override. The operator may "
        "type measured Ra, may type limits, may stop the run. The model is a colleague with a colour, not a "
        "hidden interlock. Shops that later want an interlock must do a safety review that this project "
        "explicitly does not complete.",
    )
    add_h(doc, "15.8 What “advanced research project” means at B.Tech scale", 2)
    add_p(
        doc,
        "Advanced does not mean a larger network. Advanced means a problem that sits on manufacturing science, "
        "statistics, software architecture and safety language at once, and that refuses the cheap exits "
        "(fake XRD, fake e-stop, fake lab RMSE). The research contribution appropriate to this degree is the "
        "formulation: integrity as short-horizon Ra-proxy risk in a latent regime, with a mechanics residual, "
        "delivered as a shop artefact, trained first on a structured simulator so that the experimental plan "
        "for real labels is already written. That formulation can be cited, attacked and improved. A lone "
        "accuracy number on synthetic wear cannot.",
    )
    add_h(doc, "15.9 Closing of the extended research discussion", 2)
    add_p(
        doc,
        "Chapters 12–15 were written so that a reader who asked for ideation, purpose, aim, future impact, "
        "industry effect, competitive advantage and market help would find those topics treated as research "
        "questions rather than as brochure paragraphs. The aim remains the sentence in Chapter 1: design, "
        "implement and demonstrate a physics-informed multimodal monitor for latent regime discovery and early "
        "surface-integrity degradation prediction in CNC end milling of aluminium alloy, packaged as a usable "
        "dashboard with optional mill and DAQ linkage. The reason the project is being done remains the gap "
        "between late inspection and an explainable early warning. The future impact remains conditional on "
        "measured Ra and VB. The industry is affected first as a teaching and MSME layer, later as a vendor "
        "brief. The work is better than calendars, late inspection and opaque scores for that layer, and not "
        "better than certified TCM at breakage. Markets are helped when buyers, vendors, colleges and "
        "graduates share that narrower, truer sentence.",
    )


def extra_literature(doc, add_h, add_p, add_bullet):
    doc.add_page_break()
    add_h(doc, "Chapter 2B  Extended literature placement", 1)
    add_p(
        doc,
        "Classical metal-cutting texts (Kalpakjian and Schmid; Altintas; Tlusty) already contain the quantities "
        "this monitor is allowed to see: cutting power, tool wear, chatter, tooth-passing frequency. Taylor’s "
        "1907 tool-life form is used only qualitatively in the simulator; no claim is made that the accelerated "
        "demo curve is an identified Taylor exponent for a named insert. ISO 8688 supplies the 0.3 mm milling "
        "wear conversation. ISO 4287 / 21920 supply the Ra conversation. Those standards are the mechanical "
        "backbone. The machine-learning backbone is narrower: Gaussian mixtures for unsupervised neighbourhoods, "
        "histogram gradient boosting for tabular heads, and a long literature of TCM surveys that, by 2025, "
        "treat wear classification, VB regression, chatter detection and roughness prediction as standard "
        "tasks and still call simultaneous roughness-and-wear monitoring early-stage.",
    )
    add_p(
        doc,
        "Digital-twin papers from 2025 add on-machine inspection and remaining-life models, and they report "
        "the familiar gap between offline and live error. This project cites that gap as a warning, not as a "
        "score to beat. Simultaneous monitoring papers show that shops want Ra and VB on one screen; the "
        "dashboard of this project is aligned with that want and more modest on proof. Market notes on TCM "
        "and predictive tool-wear analytics are used only as context for Chapter 9 and Chapter 14. They are "
        "not experimental citations.",
    )
    add_p(
        doc,
        "What the literature does not yet hand a B.Tech student is a complete, honest, runnable stack with a "
        "declared integrity proxy and a declared safety non-claim. Filling that systems-and-honesty gap is "
        "the literature justification for binding this report at thirty pages rather than as a ten-page lab "
        "handout.",
    )
    doc.add_page_break()
    add_h(doc, "Chapter 6B  Reproducibility and repository discipline", 1)
    add_p(
        doc,
        "Reproducibility in this project has two levels. Software reproducibility: an examiner with Python 3 "
        "and requirements.txt can train the simulated monitor, launch Streamlit, and optionally launch the "
        "bridge. Experimental reproducibility: not yet claimed, because labelled cuts do not exist in the "
        "repository. Confusing the two levels is the most likely way this report could be misread. The "
        "trained_on string, Chapter 7, Table 6 and the abstract are therefore repeated on purpose.",
    )
    add_p(
        doc,
        "Repository discipline that supports the research claim includes: a single SensorFrame; a single "
        "config.yaml process window; models stored beside a description of how they were fit; supervisor "
        "logic in one decide() path; bridge logic in one process bound to one port; and UI captions that "
        "state the three honesty sentences. A future student who breaks that discipline — for example by "
        "hard-coding a second Ra threshold inside the plotter — will have broken the research object, not "
        "only the style guide.",
    )
    doc.add_page_break()
    add_h(doc, "Chapter 10B  Experimental plan for the first labelled campaign", 1)
    add_p(
        doc,
        "The first campaign that would turn Chapter 7 into a results chapter is small and factorial. Material: "
        "Al 6061-T6 plates from one batch. Tool: one catalogue of 10 mm four-flute carbide end mills, new and "
        "pre-worn to two photographed VB lands. Speeds: 2400 and 3600 r/min. Feeds: 0.08 and 0.16 mm/tooth. "
        "Depth: 1.0 mm. Coolant: the laboratory’s normal flood or mist, held constant. For each cell, record "
        "vibration, current and temperature; measure Ra at three stylus locations after the pass; photograph "
        "VB. Repeat enough to estimate a false-alarm rate on the Ra-spec event. Retrain the heads. Report "
        "calibration plots for the probability head. Keep the GMM if the components still name; change the "
        "component count if they do not.",
    )
    add_p(
        doc,
        "Only after that campaign is it legitimate to discuss a second alloy, a residual-stress coupon, or a "
        "real interpolator bit. The order is part of the research design. Skipping it in order to print a "
        "more fashionable title would undo the ideation of Chapter 12.",
    )


def extra_closing_pages(doc, add_h, add_p, add_bullet):
    doc.add_page_break()
    add_h(doc, "Appendix I  Extended aim, objectives and success criteria", 1)
    add_p(
        doc,
        "Aim (repeated for the bound volume). Design, implement and demonstrate a physics-informed multimodal "
        "learning system for latent regime discovery and early surface-integrity degradation prediction in CNC "
        "end milling of aluminium alloy (default Al 6061), packaged as a shop-floor dashboard with optional "
        "linkage to a browser CNC and to serial DAQ hardware.",
    )
    add_p(doc, "Success criteria that this B.Tech volume can be marked against:", first_line=False)
    for s in [
        "A reader can state the integrity proxy (Ra > spec) and the three honesty sentences without looking them up.",
        "A reader can run the dashboard from the instructions in Appendix B.",
        "A reader can point to the file that implements SensorFrame, features, GMM/HGB, supervisor and bridge.",
        "A reader can explain why probability is not a hard-stop and why Stop is not Hold.",
        "A reader can explain why the project is better than a calendar and not better than a certified breakage TCM.",
        "A reader can state the first labelled experiment that would convert Chapter 7 into laboratory results.",
        "A reader can state who in industry is helped now (colleges, MSME architecture) and who is only briefed (tier vendors, machine builders).",
    ]:
        add_bullet(doc, s)
    doc.add_page_break()
    add_h(doc, "Appendix J  Notes on figures and market numbers", 1)
    add_p(
        doc,
        "Figures 2 and 3 are generated from the same qualitative shapes the simulator uses; they are explanatory "
        "drawings, not plots of a physical cut. Figure 5 is a qualitative bar chart, not a measured usefulness "
        "trial. Figure 6 compiles public TCM market talk into an indicative curve; it is not an econometric "
        "forecast and not a valuation of this software. Figure 9 is an index of where savings could appear "
        "after labelled TCM; the percentages are teaching targets, not results. Figure 10 is a roadmap of "
        "restraint. Anyone photocopying a figure into a pitch deck should keep the caption.",
        first_line=False,
    )
    doc.add_page_break()
    add_h(doc, "Appendix K  Suggested viva questions and short answers", 1)
    pairs = [
        "Q. Why Al 6061? A. It is the alloy the teaching mill cuts and the alloy whose drawing specifies Ra.",
        "Q. Why not residual stress? A. XRD was not booked; claiming it would be false.",
        "Q. Why GMM not a deep autoencoder? A. Four named neighbourhoods a supervisor can say aloud.",
        "Q. Why HGB not LSTM? A. Tabular engineered features, 0.25 s windows, laptop training, inspectable contributions.",
        "Q. Why a physics residual? A. So force and power cannot silently disagree.",
        "Q. Why is risk not a trip? A. Because it rose early while the cut was still useful and would train operators to disable the system.",
        "Q. Did you stop a real CNC? A. No. Software Hold on a visualisation mill is not an e-stop.",
        "Q. Are the plots laboratory results? A. No. They are simulated training and integration observations.",
        "Q. How does this help the market? A. It trains buyers and colleges on a minimum integrity layer; it does not capture the TCM TAM.",
        "Q. What will you do if you get the mill for a week? A. Factorial on speed and feed, measure Ra and VB, retrain, report calibration.",
    ]
    for p in pairs:
        add_bullet(doc, p)
    doc.add_page_break()
    add_h(doc, "Appendix L  Final statement of contribution", 1)
    add_p(
        doc,
        "The contribution of this B.Tech project is a complete, honest, physics-informed multimodal monitor "
        "for latent regime discovery and early Ra-proxy integrity warning in Al 6061 end milling, with a "
        "shop-floor HMI, operator-owned physical limits, optional serial DAQ, and a mill bridge that respects "
        "Hold-versus-Stop. The contribution is not a certified safety function, not an XRD study, and not a "
        "measured plant saving. Those non-contributions are listed so that the real contribution remains "
        "visible. If the volume is judged as research, it should be judged on the quality of that formulation, "
        "the quality of the artefact, and the quality of the refusals.",
        first_line=False,
    )
