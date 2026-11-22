# AuricHelix

**Physics-informed multimodal learning for latent regime discovery and early surface-integrity degradation prediction in CNC milling of Al 6061.**

IIT Patna · Department of Mechanical Engineering · B.Tech project  
Rajshekhar · Piyush Jatoliya · Supervisor: Dr. Mahavir Singh

## Live sites

| Site | Platform | URL |
|---|---|---|
| **AuricHelix Mill** | GitHub Pages | https://shekharaj0007.github.io/auric-helix/ |
| **AuricHelix Monitor** | Binder (MyBinder) | https://mybinder.org/v2/gh/shekharaj0007/auric-helix/main?urlpath=monitor/ |

The mill is the browser CNC (Cycle start, Hold, DRO, G-code). The monitor is the early surface-integrity warning dashboard from the project report. The first Binder launch can take a few minutes while the environment builds; later launches are faster.

Streamlit Community Cloud one-click (if you sign in with GitHub):  
https://share.streamlit.io/deploy?repository=shekharaj0007/auric-helix&branch=main&mainModule=dashboard/app.py

Report (this description follows it): [`docs/Machining_Integrity_Monitor_Project_Report.pdf`](docs/Machining_Integrity_Monitor_Project_Report.pdf)

## Abstract

Arithmetic roughness (Ra) and flank wear (VB) decide whether a milled aluminium face is acceptable and whether an end mill is still serviceable, yet both are normally measured after the pass, by stylus and microscope. AuricHelix estimates them **during** the cut.

Every 0.25 s the system reads a multimodal window of vibration, cutting force, spindle power, temperature and the commanded speed and feed. It reduces the window to a **16-dimensional feature vector** that includes a physics residual \(P \approx P_\mathrm{idle}+F_c V_c\), assigns the window to one of four **latent cutting regimes** with a Gaussian mixture model, and predicts Ra, VB and the probability of surface-integrity degradation inside a chosen horizon (default 30 s) with histogram gradient-boosting models. An Isolation Forest scores novelty. A rule-based supervisor compares the estimates with limits typed by the operator and, when a hard limit is crossed, holds the machine pose and writes an incident PDF.

The integrity event is **D = 1** when Ra ≥ 1.6 µm or VB ≥ 0.30 mm. Models were trained on a physics-based simulator of Al 6061 end milling (2880 windows, 12 speed/feed conditions). Reported errors measure agreement with the simulator and are **not** laboratory profilometer or microscope results. The same `SensorFrame` contract can be retrained on measured labels without redesign.

**Keywords:** CNC milling, Al 6061, surface roughness, tool wear, chatter, Gaussian mixture model, gradient boosting, condition monitoring, physics-informed features.

## Scope of claims

- The surface-integrity proxy is a roughness specification, not residual-stress or metallurgical measurement.
- Software Hold is decision support, not a certified Category 0/1 emergency stop.
- Training labels are simulated until a laboratory campaign replaces `label_ra_um` / `label_vb_mm`.

## Working principle (STAR)

| | |
|---|---|
| **Situation** | Al 6061 is finished with a 10 mm, 4-flute end mill. Ra is measured after the pass, so scrap is already cut. |
| **Task** | Warn before Ra or VB crosses its limit; name the latent regime; keep the pose on screen; hold and report at a typed hard stop. |
| **Action** | SensorFrame → 16-D features → GMM, HGB heads and Isolation Forest → typed-limit supervisor → incident PDF. |
| **Result** | A shop-floor page showing status, early-warning risk, held DRO position and an incident report. |

## What you see on the two sites

**Mill** — G-code editor, 3D toolpath, Cycle start / Hold / Stop, DRO X Y Z, feed override.

**Monitor** — machine status, regimes A–D, predicted Ra / Rq / Rz / Rt, VB, wear rate, RUL, temperature, 30 s degradation probability, physics residual, contribution bars, typed hard-stops, downloadable stop-incident PDF.

## Pipeline and algorithms

1. Window (0.25 s) of vibration, force, power, temperature, rpm, feed  
2. 16-D features: RMS, kurtosis, crest, skewness, FFT tooth/chatter bands, entropy, MRR, specific energy, physics residual  
3. **Gaussian mixture** (4 full-covariance components) → regimes A–D  
4. **Histogram gradient boosting** heads → Ra family, chatter Hz, VB, wear rate, temperature, RUL, 30 s risk  
5. **Isolation Forest** → anomaly  
6. **Permutation importance** → why the alarm fired  
7. Rule supervisor → reduce feed / reduce rpm / Hold  

Default process card: 10 mm, 4 flutes, 3000 r/min, 0.12 mm/tooth, 1.0 mm depth, Al 6061.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Mill hook (CNC laptop):

```powershell
python scripts/cnc_bridge.py
```

Then open `http://127.0.0.1:8766/` (mill) and `http://127.0.0.1:8501` (monitor).

## Layout

| Path | Role |
|---|---|
| `dashboard/app.py` | Shop-floor monitor |
| `src/acquisition/` | Simulator, Arduino serial, HTTP mill |
| `src/processing/features.py` | 16-D vector + physics residual |
| `src/ml/model.py` | GMM + HGB + Isolation Forest |
| `src/control/` | Supervisor, stop log, incident PDF |
| `scripts/cnc_bridge.py` | Local mill reverse proxy |
| `mill-public/` | Static mill snapshot for hosting |
| `docs/Machining_Integrity_Monitor_Project_Report.pdf` | Full concept report |

## Licence of claims vs code

Software Hold ≠ certified e-stop. Simulated MAE ≠ laboratory results. The academic supervisor is not a certified CNC emergency-stop authority.
