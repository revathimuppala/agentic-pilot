#!/usr/bin/env python3
"""
Renders a spec-to-product markdown deliverable (spec.md / design.md /
implementation_plan.md) to a styled, standalone HTML file next to it, and
opens it in Chrome.

Usage:
    python3 render_md.py path/to/spec.md [--no-open]
"""
import argparse
import html
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("This script requires the 'markdown' package: pip install markdown")

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  :root {{
    --bg: #eef2f2; --surface: #ffffff; --surface-sunken: #f6f8f8;
    --ink: #142b30; --ink-muted: #5c7378; --ink-faint: #8aa0a4; --border: #dde5e6;
    --shell: #0d3a42; --shell-ink: #eaf3f2;
    --accent: #1c8c93; --accent-strong: #106169; --accent-warm: #e2963d;
    --warm-bg: #fbf0dc; --warm-ink: #8a5a10;
    --open-bg: #fde8e4; --open-ink: #a3401f;
    --font-display: "Manrope", system-ui, sans-serif;
    --font-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
    --font-mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", monospace;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font-body); line-height: 1.65; }}
  .masthead {{ background: var(--shell); color: var(--shell-ink); padding: 28px max(16px, calc((100% - 760px) / 2)); }}
  .masthead .eyebrow {{ font-family: var(--font-mono); font-size: .72rem; letter-spacing: .08em; text-transform: uppercase; color: #9fc0bd; margin: 0 0 8px; }}
  .masthead h1 {{ font-family: var(--font-display); font-weight: 800; font-size: clamp(1.4rem, 4vw, 2rem); margin: 0 0 6px; text-wrap: balance; }}
  .masthead .sub {{ color: #bcdad7; font-size: .88rem; margin: 0; }}
  main {{ max-width: 760px; margin: 0 auto; padding: 40px 16px 100px; }}
  h1, h2, h3 {{ font-family: var(--font-display); text-wrap: balance; }}
  h2 {{ font-weight: 800; font-size: 1.3rem; margin: 46px 0 16px; padding-bottom: 10px; border-bottom: 2px solid var(--border); }}
  main > h2:first-child {{ margin-top: 0; }}
  h3 {{ font-weight: 700; font-size: 1.02rem; margin: 30px 0 14px; }}
  p {{ margin: 0 0 14px; max-width: 68ch; }}
  ul, ol {{ padding-left: 1.3em; margin: 0 0 14px; }}
  li {{ margin-bottom: 8px; max-width: 66ch; }}
  li > ul, li > ol {{ margin-top: 8px; }}
  strong {{ color: var(--ink); }}
  h3 + p {{
    background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent);
    border-radius: 8px; padding: 14px 18px; font-size: .93rem; color: var(--ink-muted); max-width: none;
  }}
  h3 + p + ul {{ background: var(--surface-sunken); border-radius: 8px; padding: 16px 20px 16px 34px; }}
  h3 + p + ul li::marker {{ color: var(--accent-strong); }}
  code {{ font-family: var(--font-mono); font-size: .82em; background: var(--surface-sunken); color: var(--ink-muted); padding: 1px 7px; border-radius: 999px; }}
  code.is-flag {{ background: var(--warm-bg); color: var(--warm-ink); }}
  code.is-open {{ background: var(--open-bg); color: var(--open-ink); }}
  a {{ color: var(--accent-strong); }}
  table {{ border-collapse: collapse; width: 100%; margin: 0 0 16px; font-size: .9rem; }}
  th, td {{ border: 1px solid var(--border); padding: 6px 10px; text-align: left; }}
  th {{ background: var(--surface-sunken); }}
  footer {{ max-width: 760px; margin: 0 auto; padding: 0 16px 60px; color: var(--ink-faint); font-size: .78rem; }}
</style>
</head>
<body>
<header class="masthead">
  <p class="eyebrow">{eyebrow}</p>
  <h1>{title}</h1>
  <p class="sub">Rendered from <code style="background:rgba(255,255,255,.12);color:inherit">{source_name}</code> · auto-updated on every edit</p>
</header>
<main>
{body}
</main>
<footer>Regenerated {timestamp} by the spec-to-product workflow.</footer>
</body>
</html>
"""


def flag_inline_code(body_html: str) -> str:
    """Give (assumed ...) / (open ...) inline-code spans their own visual treatment."""
    def repl(m):
        inner = m.group(1)
        text = re.sub(r"<[^>]+>", "", inner)
        cls = ""
        if re.match(r"^\(?\s*assumed", text, re.I):
            cls = ' class="is-flag"'
        elif re.match(r"^\(?\s*open", text, re.I):
            cls = ' class="is-open"'
        return f"<code{cls}>{inner}</code>"

    return re.sub(r"<code>(.*?)</code>", repl, body_html, flags=re.S)


def render(md_path: Path) -> Path:
    text = md_path.read_text()
    body = markdown.markdown(text, extensions=["extra", "sane_lists", "toc"])
    body = flag_inline_code(body)

    title_match = re.search(r"^#\s+(.+)$", text, re.M)
    title = title_match.group(1).strip() if title_match else md_path.stem

    version_dir_name = md_path.parent.name
    version_match = re.match(r"^(\d+)(?:-(.+))?$", version_dir_name)
    if version_match:
        version_num, version_slug = version_match.group(1), version_match.group(2)
        eyebrow = f"spec-to-product · v{version_num}"
        if version_slug:
            eyebrow += f" ({version_slug.replace('-', ' ')})"
    else:
        eyebrow = version_dir_name or "spec-to-product"

    out_path = md_path.with_suffix(".html")
    out_path.write_text(
        TEMPLATE.format(
            title=html.escape(title),
            eyebrow=html.escape(eyebrow),
            source_name=html.escape(md_path.name),
            body=body,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
    )
    return out_path


def open_in_chrome(path: Path) -> None:
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", "Google Chrome", str(path)], check=False)
    elif sys.platform.startswith("linux"):
        subprocess.run(["google-chrome", str(path)], check=False)
    elif sys.platform == "win32":
        subprocess.run(["start", "chrome", str(path)], shell=True, check=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("md_path", type=Path)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()

    html_path = render(args.md_path)
    print(f"Rendered {html_path}")
    if not args.no_open:
        open_in_chrome(html_path)
