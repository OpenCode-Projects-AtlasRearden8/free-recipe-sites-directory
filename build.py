#!/usr/bin/env python3
"""Build the static HTML site from the Markdown sources in site/.

Output goes to dist/. Each page inlines the stylesheet; no JavaScript,
no external assets, no tracking of any kind.

Requires pandoc on PATH.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE_DIR = ROOT / "site"
DIST_DIR = ROOT / "dist"

SITE_NAME = "Free Recipe Sites Directory"

CSS = """\
:root {
  --accent: #b0492f;
  --text: #22272a;
  --muted: #5c6a70;
  --bg: #fdfcf8;
  --card: #ffffff;
  --line: #e4ded2;
}
* { box-sizing: border-box; }
html { font-size: 17px; }
body {
  margin: 0 auto;
  max-width: 44rem;
  padding: 0 1.25rem 4rem;
  background: var(--bg);
  color: var(--text);
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.65;
}
h1, h2, h3, h4 { font-family: "Helvetica Neue", Arial, sans-serif; line-height: 1.25; }
h1 { font-size: 1.9rem; margin: 2.4rem 0 0.8rem; color: var(--accent); }
h2 { font-size: 1.35rem; margin-top: 2.2rem; border-bottom: 2px solid var(--line); padding-bottom: 0.3rem; }
h3 { font-size: 1.08rem; margin-top: 1.6rem; }
a { color: var(--accent); text-decoration-color: rgba(176, 73, 47, 0.35); }
a:hover { color: #8a3a24; }
header.masthead { border-top: 6px solid var(--accent); margin-top: 1.2rem; padding-top: 0.4rem; }
header.masthead .masthead-title {
  font-family: "Helvetica Neue", Arial, sans-serif;
  font-weight: 700; font-size: 1.05rem; color: var(--accent);
  background: none; border: none;
}
nav.crumbs { font-size: 0.85rem; color: var(--muted); margin-top: 0.4rem; font-family: "Helvetica Neue", Arial, sans-serif; }
nav.crumbs a { color: var(--muted); }
nav.catback {
  margin-top: 3rem; padding: 1rem 1.2rem; background: var(--card);
  border: 1px solid var(--line); border-radius: 8px;
  font-family: "Helvetica Neue", Arial, sans-serif; font-size: 0.92rem;
}
nav.catback strong { display: block; margin-bottom: 0.35rem; }
ul { padding-left: 1.4rem; }
li { margin: 0.25rem 0; }
blockquote {
  margin: 1.2rem 0; padding: 0.2rem 1.1rem; color: var(--muted);
  border-left: 4px solid var(--line); font-style: italic;
}
hr { border: none; border-top: 1px solid var(--line); margin: 2rem 0; }
footer { margin-top: 2.5rem; color: var(--muted); font-family: "Helvetica Neue", Arial, sans-serif; font-size: 0.8rem; }
code { background: #f2efe6; border-radius: 4px; padding: 0.1em 0.35em; font-size: 0.9em; }
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - {site}</title>
<meta name="description" content="{description}">
<style>
{css}
</style>
</head>
<body>
<header class="masthead">
  <a class="masthead-title" href="{home}">{site}</a>
  <nav class="crumbs"><a href="{home}">home</a> &rsaquo; {crumbs}</nav>
</header>
{body}
<footer>
  No JavaScript. No ads. No trackers. A free recipe links directory
  maintained by Asdale Dynamics, LLC &middot; MIT License.
</footer>
</body>
</html>
"""

NAV_PAGES = [
    ("index.html", "Index"),
    ("library-archives.html", "Library & archives"),
    ("government-nutrition.html", "Gov & nutrition"),
    ("budget-blogs.html", "Budget blogs"),
    ("no-photo-fast.html", "No-photo & fast"),
    ("tonight-helpers.html", "Tonight helpers"),
    ("tonight.html", "The Tonight page"),
]


def build_page(path: Path) -> None:
    rel = path.relative_to(ROOT)
    stem = path.stem
    rel_html = f"{stem}.html"

    result = subprocess.run(
        ["pandoc", "--from", "markdown+smart", "--to", "html5", str(path)],
        capture_output=True,
        text=True,
        check=True,
    )
    body = result.stdout

    # Append the standard "back to the directory" nav for every page but the
    # index (category pages already list it, but keep it uniform and simple
    # by ensuring it exists once).
    if rel_html != "index.html":
        items = "\n".join(
            f'<a href="{href}">{label}</a>' for href, label in NAV_PAGES
        )
        nav = (
            '\n<nav class="catback"><strong>Back to the directory</strong>\n'
            f'{items}\n</nav>\n'
        )
        body += nav

    # Page title: first markdown H1 line.
    title = stem.replace("-", " ").title()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("# "):
                title = line[2:].strip()
                break

    meta_desc = (
        "A curated directory of genuinely free recipe sites: library archives, "
        "government nutrition pages, budget blogs, and fast no-photo collections."
    )

    html = TEMPLATE.format(
        title=title,
        site=SITE_NAME,
        description=meta_desc,
        css=CSS,
        home="index.html",
        crumbs=title,
        body=body,
    )

    out = DIST_DIR / rel_html
    out.write_text(html, encoding="utf-8")
    print(f"  built dist/{rel_html}")


def main() -> None:
    pandoc = shutil.which("pandoc")
    if not pandoc:
        sys.exit("error: pandoc not found on PATH - install it (https://pandoc.org/installing.html)")

    if not SITE_DIR.is_dir():
        sys.exit(f"error: site/ directory not found at {SITE_DIR}")

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir()

    pages = sorted(SITE_DIR.glob("*.md"))
    if not pages:
        sys.exit("error: no markdown pages found in site/")
    print(f"Building {len(pages)} pages with pandoc...")
    for page in pages:
        build_page(page)
    print(f"Done -> {DIST_DIR}/ ({len(pages)} pages, inline CSS, no scripts)")


if __name__ == "__main__":
    main()
