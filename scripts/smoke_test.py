import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pipeline import infer, load_config, make_source

cfg = load_config(str(ROOT / "config.yaml"))
src = make_source(cfg)
src.open()
for _ in range(5):
    frame = src.read_frame()
    result = infer(frame, 1.6, 30)
    print(
        f"{result.frame.time_s:5.2f}s  {result.regime.name:32s}  "
        f"P={result.forecast.probability:.2f}  "
        f"Ra_hat={result.forecast.predicted_ra_um:.2f}  "
        f"true={result.frame.true_ra_um:.2f}"
    )
src.close()
print("smoke ok")
