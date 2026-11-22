"""Schematic figures for the 10-minute IITP BTP talk."""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUT = Path(__file__).resolve().parent / "slides_assets"
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def box(ax, x, y, w, h, text, fc, ec="#0B1F3A", fs=9.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
                                facecolor=fc, edgecolor=ec, linewidth=1.3))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", color="#0B1F3A", wrap=True)


def arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color="#0B1F3A", lw=1.6))


def fig_two_paths():
    fig, ax = plt.subplots(figsize=(13.2, 4.4))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 4.4)
    ax.axis("off")
    ax.text(6.6, 4.15, "Existing shop loop is late. Proposed loop warns while the cut is still useful.",
            ha="center", fontsize=12, color="#5A6673")

    ax.text(0.25, 3.55, "EXISTING", fontsize=11, fontweight="bold", color="#9B2C2C")
    steps_e = [(0.2, "Machine"), (2.3, "Cut"), (4.15, "Finish"), (6.15, "Measure Ra"), (8.7, "Detect failure")]
    for i, (x, t) in enumerate(steps_e):
        box(ax, x, 2.45, 1.85, 0.85, t, "#F8E8E8", fs=10, bold=True)
        if i < len(steps_e) - 1:
            arrow(ax, x + 1.85, 2.87, steps_e[i + 1][0], 2.87)
    ax.text(11.0, 2.75, "TOO LATE", fontsize=12, fontweight="bold", color="#9B2C2C")

    ax.text(0.25, 1.85, "PROPOSED", fontsize=11, fontweight="bold", color="#1F6B4A")
    steps_p = [(0.2, "Machine"), (2.15, "Sensors"), (4.15, "ML + Physics"), (6.55, "Early warning"), (8.95, "Operator acts")]
    for i, (x, t) in enumerate(steps_p):
        box(ax, x, 0.55, 1.95, 0.95, t, "#E4F3EA", fs=10, bold=True)
        if i < len(steps_p) - 1:
            arrow(ax, x + 1.95, 1.02, steps_p[i + 1][0], 1.02)
    ax.text(11.15, 0.9, "IN TIME", fontsize=12, fontweight="bold", color="#1F6B4A")
    fig.tight_layout()
    fig.savefig(OUT / "talk_paths.png", dpi=200, bbox_inches="tight")
    plt.close()


def fig_drivers():
    fig, ax = plt.subplots(figsize=(13.0, 2.6))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 2.6)
    ax.axis("off")
    items = [
        ("Tool wear VB", "#F4EDE4"),
        ("Chatter", "#F8E8E8"),
        ("Temperature", "#EEE8F6"),
        ("Force", "#E8F1F8"),
        ("Vibration", "#E8F6EE"),
        ("Surface Ra", "#FFF4D6"),
    ]
    for i, (t, c) in enumerate(items):
        box(ax, 0.25 + i * 2.12, 0.55, 1.95, 1.45, t, c, fs=12, bold=True)
        if i < len(items) - 1:
            arrow(ax, 0.25 + i * 2.12 + 1.95, 1.27, 0.25 + (i + 1) * 2.12, 1.27)
    fig.tight_layout()
    fig.savefig(OUT / "talk_drivers.png", dpi=200, bbox_inches="tight")
    plt.close()


def fig_pipeline():
    fig, ax = plt.subplots(figsize=(13.2, 6.4))
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    rows = [
        [(0.3, 5.2, 2.4, 0.95, "#E8F1F8", "Sensors /\nSimulator"),
         (3.15, 5.2, 2.4, 0.95, "#F4EDE4", "SensorFrame"),
         (6.0, 5.2, 2.5, 0.95, "#E8F6EE", "0.25 s window"),
         (9.0, 5.2, 3.8, 0.95, "#EEE8F6", "Feature extraction\n10-D vector")],
        [(0.3, 3.35, 4.0, 1.15, "#FFF4D6", "Physics residual\nP ≈ Pidle + Fc · Vc"),
         (4.8, 3.35, 3.7, 1.15, "#E4F3EA", "GMM  →  Regime\nA  B  C  D"),
         (8.95, 3.35, 3.85, 1.15, "#E8F1F8", "Hist. Gradient Boosting\nRa  VB  rate  T  risk")],
        [(0.3, 1.15, 5.9, 1.35, "#F3F6F9", "Supervisor\nPhysical limits trip   ·   Probability warns"),
         (6.7, 1.15, 6.1, 1.35, "#E4F0E8", "Dashboard + operator decision\nSTABLE  ·  WATCH  ·  SURFACE RISK")],
    ]
    for row in rows:
        for x, y, w, h, c, t in row:
            box(ax, x, y, w, h, t, c, fs=11, bold=True)
    arrow(ax, 2.7, 5.67, 3.15, 5.67)
    arrow(ax, 5.55, 5.67, 6.0, 5.67)
    arrow(ax, 8.5, 5.67, 9.0, 5.67)
    arrow(ax, 4.3, 5.2, 2.3, 4.5)
    arrow(ax, 6.6, 5.2, 6.6, 4.5)
    arrow(ax, 10.9, 5.2, 10.9, 4.5)
    arrow(ax, 2.3, 3.35, 3.2, 2.5)
    arrow(ax, 10.8, 3.35, 9.7, 2.5)
    fig.tight_layout()
    fig.savefig(OUT / "talk_pipeline.png", dpi=200, bbox_inches="tight")
    plt.close()


def fig_physics():
    fig, ax = plt.subplots(figsize=(12.8, 3.6))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 3.6)
    ax.axis("off")
    items = [
        (0.3, "Measured\npower  Pmeas"),
        (3.3, "Force × speed\nPidle + Fc·Vc"),
        (6.5, "Physics residual\nR = |Pmeas − Ppred|\n/ max(Pmeas, 1)"),
        (10.0, "ML feature\nto GMM + HGB"),
    ]
    cols = ["#E8F1F8", "#F4EDE4", "#FFF4D6", "#E4F3EA"]
    for i, ((x, t), c) in enumerate(zip(items, cols)):
        box(ax, x, 0.7, 2.7, 2.15, t, c, fs=12, bold=True)
        if i < 3:
            arrow(ax, x + 2.7, 1.77, items[i + 1][0], 1.77)
    fig.tight_layout()
    fig.savefig(OUT / "talk_physics.png", dpi=200, bbox_inches="tight")
    plt.close()


def fig_regimes_cards():
    fig, ax = plt.subplots(figsize=(13.0, 3.4))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 3.4)
    ax.axis("off")
    regs = [
        ("A", "STABLE", "Leave the tool.\nCut is healthy.", "#3D9A6A", "#E4F3EA"),
        ("B", "TRANSITIONAL", "Watch the next\n30 seconds.", "#C48A1A", "#FFF4D6"),
        ("C", "UNSTABLE", "Surface risk.\nInspect / finish.", "#D15A2A", "#F8E8E8"),
        ("D", "SEVERE", "Hold.\nChange the tool.", "#C43A3A", "#F3D6D6"),
    ]
    for i, (let, name, desc, ec, fc) in enumerate(regs):
        x = 0.35 + i * 3.2
        box(ax, x, 0.45, 2.95, 2.5, f"{let}\n{name}\n\n{desc}", fc, ec=ec, fs=12, bold=True)
        if i < 3:
            arrow(ax, x + 2.95, 1.7, x + 3.2, 1.7)
    fig.tight_layout()
    fig.savefig(OUT / "talk_regimes.png", dpi=200, bbox_inches="tight")
    plt.close()


def fig_early():
    fig, ax = plt.subplots(figsize=(12.6, 4.2))
    t = np.linspace(0, 50, 300)
    ra = 0.55 + 0.018 * t + 0.00035 * t**2
    risk = 1 / (1 + np.exp(-(t - 22) / 4.2))
    ax.plot(t, ra, color="#143D66", lw=2.4, label="Predicted Ra (µm)")
    ax.axhline(1.6, color="#9B2C2C", ls="--", lw=1.5, label="Ra limit 1.6 µm")
    ax2 = ax.twinx()
    ax2.plot(t, risk, color="#C48A1A", lw=2.4, label="P(degrade in 30 s)")
    ax.axvspan(18, 32, color="#C48A1A", alpha=0.12)
    ax.text(25, 0.75, "EARLY-WARNING\nWINDOW", ha="center", fontsize=11, color="#8A5A10", fontweight="bold")
    ax.set_xlabel("Cut time (s)", fontsize=11)
    ax.set_ylabel("Ra (µm)", fontsize=11)
    ax2.set_ylabel("Degradation probability", fontsize=11)
    ax.set_ylim(0.4, 2.2)
    ax2.set_ylim(0, 1.05)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False)
    ax.set_title("Current Ra can still be legal while 30-second risk is already high", fontsize=13, pad=8)
    ax.spines["top"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "talk_early.png", dpi=200, bbox_inches="tight")
    plt.close()


def fig_decision():
    fig, ax = plt.subplots(figsize=(12.8, 3.2))
    ax.set_xlim(0, 12.8)
    ax.set_ylim(0, 3.2)
    ax.axis("off")
    box(ax, 0.3, 0.7, 3.5, 1.8, "Physical limit\nRa · VB · T · RMS · Force", "#F8E8E8", fs=12, bold=True)
    box(ax, 4.6, 0.7, 3.5, 1.8, "Degradation\nprobability", "#FFF4D6", fs=12, bold=True)
    box(ax, 8.95, 0.7, 3.5, 1.8, "Software Hold\n≠ emergency stop", "#E8F1F8", fs=12, bold=True)
    arrow(ax, 3.8, 1.6, 4.6, 1.6)
    arrow(ax, 8.1, 1.6, 8.95, 1.6)
    ax.text(2.05, 0.28, "TRIPS", ha="center", fontsize=11, fontweight="bold", color="#9B2C2C")
    ax.text(6.35, 0.28, "WARNS ONLY", ha="center", fontsize=11, fontweight="bold", color="#C48A1A")
    ax.text(10.7, 0.28, "DEMO ACTION", ha="center", fontsize=11, fontweight="bold", color="#143D66")
    fig.tight_layout()
    fig.savefig(OUT / "talk_decision.png", dpi=200, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    fig_two_paths()
    fig_drivers()
    fig_pipeline()
    fig_physics()
    fig_regimes_cards()
    fig_early()
    fig_decision()
    print("talk figures ok", OUT)
