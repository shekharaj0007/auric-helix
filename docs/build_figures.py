"""Generate figures for the BTP research report."""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "font.family": "DejaVu Serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
})


def fig_architecture():
    fig, ax = plt.subplots(figsize=(10.2, 5.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    boxes = [
        (0.3, 3.8, 2.2, 1.5, "#E8F1F8", "Machine side\nForgeMill / CNC\nCycle start · Hold"),
        (0.3, 1.4, 2.2, 1.5, "#F4EDE4", "DAQ path\nArduino / serial\nOR physics simulator"),
        (3.0, 2.4, 2.3, 2.0, "#E8F6EE", "Features\nRMS · kurtosis · FFT\nchatter band\nphysics residual"),
        (5.7, 3.6, 2.2, 1.6, "#F8E8E8", "GMM\nlatent regimes\nA → B → C → D"),
        (5.7, 1.2, 2.2, 1.6, "#EEE8F6", "HGB models\nRa · VB · risk\ntemperature"),
        (8.3, 2.3, 1.5, 2.2, "#E4F0E8", "Supervisor\nlimits · Hold\ndashboard"),
    ]
    for x, y, w, h, c, t in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=c, edgecolor="#2A3038", linewidth=1.2, zorder=2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=8.5, zorder=3)
    arrows = [((2.5, 4.3), (3.0, 3.6)), ((2.5, 2.1), (3.0, 3.0)), ((5.3, 3.4), (5.7, 4.2)), ((5.3, 3.2), (5.7, 2.1)), ((7.9, 4.3), (8.3, 3.6)), ((7.9, 2.0), (8.3, 3.0))]
    for (x0, y0), (x1, y1) in arrows:
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color="#2A3038", lw=1.2))
    ax.set_title("Figure 1. End-to-end architecture of the machining integrity monitor", fontsize=11, pad=8)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_architecture.png", dpi=180, bbox_inches="tight")
    plt.close()


def fig_regimes():
    t = np.linspace(0, 50, 400)
    vib = 0.35 + 0.02 * t + 0.12 * (t > 18) + 0.28 * (t > 32) + 0.08 * np.sin(0.9 * t)
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    ax.plot(t, vib, color="#2A5080", lw=1.8)
    ax.axvspan(0, 16, color="#3D9A6A", alpha=0.16, label="A Stable")
    ax.axvspan(16, 28, color="#C48A1A", alpha=0.16, label="B Transitional")
    ax.axvspan(28, 40, color="#D15A2A", alpha=0.16, label="C Unstable")
    ax.axvspan(40, 50, color="#C43A3A", alpha=0.16, label="D Severe")
    ax.set_xlabel("Cut time (s)")
    ax.set_ylabel("Vibration RMS (g)")
    ax.set_title("Figure 2. Latent regimes along a simulated Al 6061 end-milling run")
    ax.legend(loc="upper left", frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "fig2_regimes.png", dpi=180, bbox_inches="tight")
    plt.close()


def fig_wear():
    t = np.linspace(0, 50, 300)
    vb = 0.02 + 0.004 * t + 0.00012 * t**2
    vb = np.clip(vb, 0, 0.38)
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    ax.plot(t, vb, color="#8B3A2A", lw=2)
    ax.axhline(0.30, color="#C43A3A", ls="--", lw=1.2, label="ISO 8688-style VB limit 0.30 mm")
    ax.fill_between(t, 0.30, vb, where=vb > 0.30, color="#C43A3A", alpha=0.2)
    ax.set_xlabel("Accelerated demo time (s)")
    ax.set_ylabel("Flank wear VB (mm)")
    ax.set_title("Figure 3. Taylor-type flank-wear growth used in the physics simulator")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "fig3_wear.png", dpi=180, bbox_inches="tight")
    plt.close()


def fig_features():
    fig, ax = plt.subplots(figsize=(9.4, 4.8))
    ax.axis("off")
    steps = [
        (0.5, "Window\n0.25 s @ 5 kHz"),
        (2.6, "Time stats\nRMS, kurtosis\ncrest, force"),
        (4.7, "Spectrum\ntooth / chatter\nentropy"),
        (6.8, "Physics\nP ≈ Fc·Vc\nresidual"),
        (8.9, "10-D vector\nto GMM + HGB"),
    ]
    for i, (x, t) in enumerate(steps):
        ax.add_patch(FancyBboxPatch((x - 0.85, 1.3), 1.7, 1.8, boxstyle="round,pad=0.05", facecolor="#F3F6F9", edgecolor="#2A3038"))
        ax.text(x, 2.2, t, ha="center", va="center", fontsize=8.5)
        if i < len(steps) - 1:
            ax.annotate("", xy=(steps[i + 1][0] - 0.9, 2.2), xytext=(x + 0.9, 2.2), arrowprops=dict(arrowstyle="->", color="#2A3038"))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0.6, 3.8)
    ax.set_title("Figure 4. Feature pipeline from a SensorFrame to the model heads", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "fig4_features.png", dpi=180, bbox_inches="tight")
    plt.close()


def fig_compare():
    labels = ["Fixed-time\ntool change", "Threshold\nTCM", "Black-box\nDL only", "This project\nphysics + GMM"]
    scores = [2.0, 3.2, 3.6, 4.4]
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    colors = ["#9AA3AD", "#7A8FA3", "#5B7C99", "#2F6B4F"]
    ax.bar(labels, scores, color=colors, width=0.62)
    ax.set_ylim(0, 5)
    ax.set_ylabel("Qualitative usefulness for a B.Tech shop-floor demo (1–5)")
    ax.set_title("Figure 5. Positioning against common shop-floor strategies")
    fig.tight_layout()
    fig.savefig(OUT / "fig5_compare.png", dpi=180, bbox_inches="tight")
    plt.close()


def fig_market():
    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    xs = [2024, 2026, 2028, 2030, 2032, 2034]
    y = [1.8, 2.15, 2.6, 3.15, 3.7, 4.1]
    ax.plot(xs, y, "o-", color="#1F4E79", lw=2, ms=7)
    ax.fill_between(xs, y, color="#1F4E79", alpha=0.12)
    ax.set_ylabel("Tool-condition monitoring market (USD billion)")
    ax.set_title("Figure 6. Indicative TCM market trajectory (compiled from public forecasts)")
    ax.set_xticks(xs)
    fig.tight_layout()
    fig.savefig(OUT / "fig6_market.png", dpi=180, bbox_inches="tight")
    plt.close()


def fig_sensors():
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    items = [
        (0.4, 3.6, 2.0, 1.8, "#E8F1F8", "Accelerometer\nspindle / vice\nA0"),
        (2.8, 3.6, 2.0, 1.8, "#F4EDE4", "Current clamp\nspindle motor\nA1"),
        (5.2, 3.6, 2.0, 1.8, "#E8F6EE", "LM35 / TC\nbulk temperature\nA2"),
        (7.6, 3.6, 2.0, 1.8, "#EEE8F6", "CNC overrides\nrpm, feed\noptional force"),
        (2.8, 0.7, 4.4, 2.0, "#F8E8E8", "Arduino / HTTP / simulator\nSensorFrame contract\n→ feature vector → GMM + HGB"),
    ]
    for x, y, w, h, c, t in items:
        ax.add_patch(Rectangle((x, y), w, h, facecolor=c, edgecolor="#2A3038", lw=1.2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=8.5)
    for x in (1.4, 3.8, 6.2, 8.6):
        ax.annotate("", xy=(5.0, 2.7), xytext=(x, 3.6), arrowprops=dict(arrowstyle="->", color="#2A3038", lw=1.1))
    ax.set_title("Figure 7. Sensor paths that collapse into one SensorFrame", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "fig7_sensors.png", dpi=180, bbox_inches="tight")
    plt.close()


def fig_supervisor():
    fig, ax = plt.subplots(figsize=(9.4, 4.6))
    ax.axis("off")
    rows = [
        (0.5, "Live Ra, VB,\nwear rate, T, RMS", "#E8F1F8"),
        (3.3, "Operator typed\ndesired + hard limits", "#F4EDE4"),
        (6.1, "Hard-stop on\nphysical units only", "#E8F6EE"),
        (8.6, "Request Hold\n(not e-stop)", "#F8E8E8"),
    ]
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0.4, 3.6)
    for i, (x, t, c) in enumerate(rows):
        ax.add_patch(FancyBboxPatch((x - 1.05, 1.15), 2.1, 1.7, boxstyle="round,pad=0.04", facecolor=c, edgecolor="#2A3038"))
        ax.text(x, 2.0, t, ha="center", va="center", fontsize=8.4)
        if i < len(rows) - 1:
            ax.annotate("", xy=(rows[i + 1][0] - 1.1, 2.0), xytext=(x + 1.1, 2.0), arrowprops=dict(arrowstyle="->", color="#2A3038"))
    ax.text(5.25, 0.75, "Degradation probability is displayed and logged — it does not arm the trip", ha="center", fontsize=9, style="italic")
    ax.set_title("Figure 8. Supervisor logic: physical limits trip, risk informs", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "fig8_supervisor.png", dpi=180, bbox_inches="tight")
    plt.close()


def fig_value():
    labels = ["Scrap /\nrework", "Unplanned\nstop", "Wasted\ntool life", "Metrology\nwalk time"]
    before = [100, 100, 100, 100]
    after = [72, 80, 78, 70]
    x = np.arange(len(labels))
    w = 0.36
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    ax.bar(x - w / 2, before, w, color="#9AA3AD", label="Baseline shop (index)")
    ax.bar(x + w / 2, after, w, color="#2F6B4F", label="Indicative target after labelled TCM")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Relative cost index (baseline = 100)")
    ax.set_ylim(0, 130)
    ax.set_title("Figure 9. Where an early Ra/VB warning can reduce shop cost (indicative)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT / "fig9_value.png", dpi=180, bbox_inches="tight")
    plt.close()


def fig_roadmap():
    fig, ax = plt.subplots(figsize=(9.4, 4.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    stages = [
        (0.4, "B.Tech now\nsimulator +\ndashboard"),
        (2.8, "Lab campaign\nRa + VB\nlabels"),
        (5.2, "Calibrated\nrisk head\naudit log"),
        (7.6, "Plant brief /\nvendor TCM\nunder review"),
    ]
    for i, (x, t) in enumerate(stages):
        ax.add_patch(Rectangle((x, 1.2), 2.0, 1.8, facecolor="#E8F1F8" if i < 3 else "#E8F6EE", edgecolor="#2A3038"))
        ax.text(x + 1.0, 2.1, t, ha="center", va="center", fontsize=8.5)
        if i < 3:
            ax.annotate("", xy=(stages[i + 1][0], 2.1), xytext=(x + 2.0, 2.1), arrowprops=dict(arrowstyle="->", color="#2A3038"))
    ax.set_title("Figure 10. Honest industrialisation path — measurement before productisation", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUT / "fig10_roadmap.png", dpi=180, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    fig_architecture()
    fig_regimes()
    fig_wear()
    fig_features()
    fig_compare()
    fig_market()
    fig_sensors()
    fig_supervisor()
    fig_value()
    fig_roadmap()
    print("figures ok", OUT)
