"""Train GMM + wear/temperature models on simulated milling runs."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.ml.model import MONITOR

if __name__ == "__main__":
    print("Training on the physics-simulated multimodal Al 6061 dataset...")
    MONITOR.train()
    print(MONITOR.trained_on)
    print("Metrics:", MONITOR.metrics)
    print("Dataset:", ROOT / "data" / "simulated_milling_dataset.csv")
    print("Saved models/advanced_monitor.pkl")
