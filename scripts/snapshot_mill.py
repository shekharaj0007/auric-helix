"""Mirror the ForgeMill web CNC into mill-public/ for a static host."""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mill-public"
ORIGIN = "https://temporary-speedy-azure-d4iojfc.vercel.app"

ASSET_RE = re.compile(
    r"""(?:src|href|content)=["'](/_next/[^"']+|/?favicon[^"']*)["']"""
    r"""|(?:url\(|["'`])(/_next/[^"'`) ]+)"""
)


def fetch(path: str) -> tuple[bytes, str]:
    url = ORIGIN + path if path.startswith("/") else urljoin(ORIGIN + "/", path)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "AuricHelix-snapshot/1.0", "Accept-Encoding": "identity"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        ctype = (resp.headers.get("Content-Type") or "application/octet-stream").split(";")[0]
        return resp.read(), ctype


def save(rel: str, data: bytes) -> Path:
    rel = unquote(rel.split("?")[0])
    if rel.startswith("/"):
        rel = rel[1:]
    dest = OUT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return dest


def discover(text: str) -> set[str]:
    found: set[str] = set()
    for m in ASSET_RE.finditer(text):
        p = m.group(1) or m.group(2)
        if p:
            found.add(p.split("?")[0])
    for m in re.finditer(r"/_next/static/[A-Za-z0-9._/-]+", text):
        found.add(m.group(0).split("?")[0])
    return found


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    html, _ = fetch("/")
    text = html.decode("utf-8", "replace")
    text = text.replace("<title>ForgeMill — Online CNC</title>", "<title>AuricHelix Mill — Online CNC</title>")
    save("index.html", text.encode("utf-8"))
    try:
        ico, _ = fetch("/favicon.ico")
        save("favicon.ico", ico)
    except Exception:
        pass
    queue = discover(text)
    seen = {"/", "/index.html"}
    while queue:
        path = queue.pop()
        if path in seen:
            continue
        seen.add(path)
        try:
            raw, ctype = fetch(path)
        except Exception as exc:
            print("skip", path, exc)
            continue
        save(path, raw)
        if "javascript" in ctype or path.endswith((".js", ".css", ".html", ".map")):
            try:
                extra = discover(raw.decode("utf-8", "replace"))
                queue |= extra - seen
            except Exception:
                pass
        print("saved", path, len(raw))
    print("files", len(list(OUT.rglob('*'))), "dir", OUT)


if __name__ == "__main__":
    main()
