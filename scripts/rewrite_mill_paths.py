from pathlib import Path
import re

root = Path(__file__).resolve().parents[1] / "mill-public"
n = 0
for p in root.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in {".html", ".js", ".css", ".json", ".txt", ".map"}:
        continue
    t = p.read_text(encoding="utf-8", errors="replace")
    u = t.replace("/_next/", "/auric-helix/_next/").replace("/favicon.ico", "/auric-helix/favicon.ico")
    if u != t:
        p.write_text(u, encoding="utf-8")
        n += 1
print("rewritten", n)

idx = root / "index.html"
html = idx.read_text(encoding="utf-8")
bar = (
    '<div id="auric-bar" style="position:sticky;top:0;z-index:9999;background:#0B1F3A;color:#F3E6B8;'
    "font:12px/1.4 Times New Roman,serif;padding:8px 14px;display:flex;gap:16px;align-items:center;"
    'border-bottom:2px solid #C9A227">'
    '<b style="color:#C9A227">AuricHelix</b>'
    "<span>Mill</span>"
    '<a href="https://github.com/shekharaj0007/auric-helix" style="color:#C9A227">GitHub</a>'
    '<a id="auric-monitor-link" href="#" style="color:#C9A227">Integrity monitor</a>'
    '<span style="margin-left:auto;opacity:.8">IIT Patna · Al 6061 · Hold is not an e-stop</span>'
    "</div>"
)
if "auric-bar" not in html:
    html = re.sub(r"(<body[^>]*>)", r"\1" + bar, html, count=1)
    idx.write_text(html, encoding="utf-8")
    print("banner injected")
