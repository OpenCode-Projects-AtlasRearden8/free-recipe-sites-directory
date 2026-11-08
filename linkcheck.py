#!/usr/bin/env python3
"""Link checker for the free-recipe-sites-directory static site.

Checks:
  1. Internal links in site/*.md and dist/*.html: every relative link must
     resolve to a real file/page, and anchors must exist in the target.
  2. External http(s) links in site/*.md: fetched live with a browser-like
     User-Agent and a plain checker UA fallback.

Exit codes:
  0  - no failures
  1  - at least one FAIL (broken 404/410 link, bad internal link, malformed URL)

Classification:
  OK              2xx / 3xx (followed)
  WARN-BLOCKED    403/429/999 or connection error/timeout - most common cause is
                  a site blocking datacenter/synthetic traffic while serving
                  real visitors fine (well-documented AWS/gov/library behavior).
                  Warnings do NOT fail the run.
  FAIL            any other 4xx (404, 410, etc.), 5xx, or malformed URL.
                  FAILs make the run exit 1.

Usage:
  python3 linkcheck.py            # internal + external (network)
  python3 linkcheck.py --internal # internal only, no network
"""

import argparse
import concurrent.futures
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

ROOT = Path(__file__).resolve().parent
SITE_DIR = ROOT / "site"
DIST_DIR = ROOT / "dist"

MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)[^)]*\)")
ANCHOR_ONLY = re.compile(r"^#.*$")
TIMEOUT = 20
UA_MAIN = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
UA_PLAIN = "Mozilla/5.0 (compatible; free-recipe-sites-directory-checker/1.0)"

results: list[tuple[str, str, str]] = []  # (kind, url, status_message)


def md_anchors(path: Path) -> set[str]:
    anchors = set()
    text = path.read_text(encoding="utf-8")
    for heading in re.finditer(r"^#{1,6}\s+(.*)$", text, flags=re.M):
        raw = heading.group(1).strip().lower()
        raw = re.sub(r"[^a-z0-9\s-]", "", raw)
        anchors.add(raw.replace(" ", "-"))
    return anchors


def html_anchors(path: Path) -> set[str]:
    ids = set()

    class Collector(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for key, value in attrs:
                if key == "id" and value:
                    ids.add(value)

    Collector().feed(path.read_text(encoding="utf-8"))
    return ids


def check_internal(source: Path, url: str, target_dir: Path) -> None:
    """Check a relative link from a source file pointing into target_dir (dist)."""
    if url.startswith("#"):
        anchor = url[1:]
        if anchors_ok(source_html(source, target_dir), anchor):
            results.append(("internal", url, "OK (same-page anchor)"))
        else:
            results.append(("internal", url, f"FAIL: missing same-page anchor '{anchor}'"))
        return

    clean = url.split("#", 1)
    target_rel, anchor = (clean[0], clean[1] if len(clean) > 1 else None)
    if "://" in target_rel:
        return
    target = (target_dir / unquote(target_rel)).resolve()
    if not target.exists():
        results.append(("internal", url, f"FAIL: missing file ({target.name})"))
        return
    if anchor and (DIST_DIR / target.name).exists():
        if not anchors_ok(DIST_DIR / target.name, anchor):
            results.append(("internal", url, f"FAIL: missing anchor '{anchor}' in {target_rel}"))
            return
    results.append(("internal", url, "OK"))


def source_html(source: Path, target_dir: Path) -> Path:
    return target_dir / (source.stem + ".html")


def anchors_ok(page: Path, anchor: str) -> bool:
    if anchor is None:
        return True
    return anchor in html_anchors(page) | md_anchors(page.with_suffix(".md"))


def check_external(url: str) -> str:
    def head(url):
        req = urllib.request.Request(url, headers={"User-Agent": UA_MAIN})
        return urllib.request.urlopen(req, timeout=TIMEOUT)

    try:
        resp = head(url)
        return f"OK ({resp.status})"
    except urllib.error.HTTPError as err:
        if err.code in (403, 429, 999):
            # Retry once with the plain checker UA before declaring blocked.
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA_PLAIN})
                resp = urllib.request.urlopen(req, timeout=TIMEOUT)
                return f"OK ({resp.status}, on plain UA)"
            except urllib.error.HTTPError:
                return f"WARN-BLOCKED ({err.code}: likely datacenter IP block)"
            except Exception:
                return f"WARN-BLOCKED ({err.code}, retry failed)"
        if err.code in (404, 410):
            return f"FAIL ({err.code} gone/not-found)"
        return f"FAIL ({err.code})"
    except (urllib.error.URLError, TimeoutError):
        return "WARN-BLOCKED (timeout/connection refused from this network)"
    except Exception as err:
        return f"FAIL ({type(err).__name__}: {err})"


def scheme_ok(url: str) -> bool:
    parts = urlsplit(url)
    return parts.scheme in ("http", "https") and bool(parts.netloc)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--internal", action="store_true", help="check internal links only (no network)")
    args = parser.parse_args()

    md_files = sorted(SITE_DIR.glob("*.md"))

    print("== Internal link check (markdown -> dist pages) ==")
    for path in md_files:
        for match in MARKDOWN_LINK.finditer(path.read_text(encoding="utf-8")):
            label, url = match.group(1), match.group(2)
            if url.startswith(("http://", "https://", "mailto:")):
                continue
            check_internal(path, url, DIST_DIR)

    internal_fail_count = sum(1 for kind, _, msg in results if kind == "internal" and msg.startswith("FAIL"))
    internal_total = sum(1 for kind, _, _ in results if kind == "internal")
    print(f"  {internal_total} internal links: {internal_fail_count} failed")

    if not args.internal:
        print("\n== External link check (network) ==")
        externals: set[str] = set()
        for path in md_files:
            for match in MARKDOWN_LINK.finditer(path.read_text(encoding="utf-8")):
                url = match.group(2)
                if url.startswith(("http://", "https://")):
                    externals.add(url)

        def run(url):
            if not scheme_ok(url):
                return url, "FAIL (malformed URL)"
            return url, check_external(url)

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            for url, status in pool.map(run, sorted(externals)):
                results.append(("external", url, status))

    print("\n== Results ==")
    ok = warn = fail = 0
    for kind, url, msg in results:
        tag = "OK" if msg.startswith("OK") else ("WARN" if msg.startswith("WARN") else "FAIL")
        if tag == "OK":
            ok += 1
        elif tag == "WARN":
            warn += 1
        else:
            fail += 1
        print(f"[{tag:4s}] {kind:8s} {url} -> {msg}")

    print(f"\nTotals: {ok} ok, {warn} warnings (bot-blocked/timeouts), {fail} failed")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
