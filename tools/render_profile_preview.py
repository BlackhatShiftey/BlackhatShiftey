#!/usr/bin/env python3
"""Render local GitHub-like desktop and mobile previews of README.md."""

from __future__ import annotations

import subprocess
from pathlib import Path

from markdown_it import MarkdownIt
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
HTML_OUT = PREVIEW / "profile.html"

CSS = """
:root { color-scheme: dark; }
* { box-sizing: border-box; }
html, body { margin: 0; background: #0d1117; color: #f0f6fc; }
body { font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.shell { max-width: 1072px; margin: 0 auto; padding: 24px 30px 56px; }
.local-label { color: #7dcfff; font: 11px ui-monospace, monospace; letter-spacing: .12em; margin-bottom: 18px; }
.markdown-body h2 { border-bottom: 1px solid #30363d; padding-bottom: .3em; margin: 34px 0 16px; }
.markdown-body h3 { margin: 22px 0 10px; }
.markdown-body a { color: #7dcfff; text-decoration: none; }
.markdown-body img { max-width: 100%; height: auto; }
.markdown-body p { margin: 0 0 16px; }
.markdown-body li + li { margin-top: .35em; }
.markdown-body blockquote { margin: 18px 0; padding: 0 1em; color: #a9b1d6; border-left: .25em solid #e478d0; }
.markdown-body pre { overflow: auto; padding: 16px; border: 1px solid #30363d; border-radius: 8px; background: #161b22; color: #c0caf5; }
.markdown-body code { font-family: "DejaVu Sans Mono", ui-monospace, monospace; }
.markdown-body :not(pre) > code { padding: .18em .4em; border-radius: 6px; background: #1a1b26; color: #c4a7e7; }
.markdown-body table { display: table; width: 100%; border-spacing: 0; border-collapse: collapse; margin: 16px 0; }
.markdown-body td { border: 1px solid #30363d; padding: 14px 16px; background: #0f131b; }
#preview-end { width: 100%; height: 2px; background: #ff0000; margin-top: 30px; }
@media (max-width: 600px) {
  .shell { padding: 14px 12px 36px; }
  .markdown-body { font-size: 14px; }
  .markdown-body h2 { font-size: 18px; }
  .markdown-body h3 { font-size: 15px; }
  .markdown-body td { min-width: 190px; padding: 10px; }
  .markdown-body table { display: block; overflow-x: auto; }
}
"""


def build_html() -> str:
    renderer = MarkdownIt("commonmark", {"html": True, "linkify": True})
    body = renderer.render((ROOT / "README.md").read_text(encoding="utf-8"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="../">
  <title>Local profile preview</title>
  <style>{CSS}</style>
</head>
<body>
  <main class="shell">
    <div class="local-label">LOCAL DRAFT / GITHUB-LIKE RENDER</div>
    <article class="markdown-body">{body}</article>
    <div id="preview-end"></div>
  </main>
</body>
</html>
"""


def crop_to_sentinel(path: Path) -> None:
    image = Image.open(path).convert("RGB")
    pixels = image.load()
    sentinel_rows = []
    for y in range(image.height):
        for x in range(0, image.width, 2):
            red, green, blue = pixels[x, y]
            if red > 245 and green < 12 and blue < 12:
                sentinel_rows.append(y)
                break
    if sentinel_rows:
        bottom = min(image.height, max(sentinel_rows) + 22)
        image.crop((0, 0, image.width, bottom)).save(path, optimize=True)


def render(name: str, width: int, height: int, *, reduced_motion: bool = False) -> Path:
    output = PREVIEW / f"profile-{name}.png"
    command = [
        "/usr/bin/google-chrome",
        "--headless",
        "--disable-gpu",
        "--disable-background-networking",
        "--disable-extensions",
        "--disable-sync",
        "--hide-scrollbars",
        "--no-sandbox",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=1800",
        f"--window-size={width},{height}",
        f"--screenshot={output}",
    ]
    if reduced_motion:
        command.append("--force-prefers-reduced-motion")
    command.append(HTML_OUT.resolve().as_uri())
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    crop_to_sentinel(output)
    return output


def main() -> int:
    PREVIEW.mkdir(exist_ok=True)
    HTML_OUT.write_text(build_html(), encoding="utf-8")
    desktop = render("desktop", 1280, 5200)
    mobile = render("mobile", 430, 7600)
    # A near-document viewport keeps Chrome from leaving static offscreen tiles unpainted.
    mobile_reduced = render("mobile-reduced-motion", 430, 4200, reduced_motion=True)
    print(f"rendered {desktop.relative_to(ROOT)} {Image.open(desktop).size}")
    print(f"rendered {mobile.relative_to(ROOT)} {Image.open(mobile).size}")
    print(f"rendered {mobile_reduced.relative_to(ROOT)} {Image.open(mobile_reduced).size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
