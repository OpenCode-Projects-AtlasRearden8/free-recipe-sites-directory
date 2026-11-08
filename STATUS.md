# STATUS

## What was built

**free-recipe-sites-directory** — a curated, link-check-tested directory of genuinely free recipe sources, as both Markdown sources and generated static HTML. Distinct from the printables project (free-kitchen-cheatsheet-pack) and the planning-method project (meal-planning-with-ai-guide); those relationships are referenced in the site copy, not duplicated.

### Site contents (7 pages, each entry has a two-line friendly blurb)

| Page | What you get |
|---|---|
| `index.html` | Front door: how to flip to dinner in under a minute, category jump list, editorial rules |
| `tonight.html` | "The Tonight page": 10 no-photo dinner formulas you can cook without opening another tab |
| `tonight-helpers.html` | Fridge/pantry search (SuperCook) + substitution encyclopedia (Cook's Thesaurus) |
| `library-archives.html` | 5 entries: Project Gutenberg cookbook shelf, Open Library subject, Internet Archive full-text search, Wikibooks Cookbook, NYPL "What's on the Menu?" |
| `government-nutrition.html` | 6 entries: MyPlate Kitchen, USDA SNAP-Ed recipe search, Nutrition.gov, Food Hero / Spend Smart (Extension), NHLBI DASH |
| `budget-blogs.html` | 6 entries: Budget Bytes, Frugal Feeding, Cheap Recipe Blog, Good Cheap Eats, $5 Dinners, Cooking on a Bootstrap |
| `no-photo-fast.html` | 3 entries: Wikibooks Cookbook, Recipeland, Cooking for Engineers — plus why text-first pages load fast |

Total external picks: 20 entries across 5 categories.

### Privacy posture (the requirement was "no tracking")

- No JavaScript, `<script>`, `<img>` from the site, iframes, or external assets (verified below).
- No analytics, affiliate links, or sponsored picks; each page inlines its own ~2 KB CSS.
- All 7 built pages are under 8 KB each.

### Repo layout

```
README.md            how to build/check, licensing, credit
LICENSE              MIT, Copyright (c) 2026 Asdale Dynamics, LLC
Makefile             build / check / all targets
build.py             pandoc markdown -> dist/ static HTML
linkcheck.py         internal + external link verification
site/*.md            7 markdown sources (single source of truth)
dist/*.html          7 built pages (committed, deployable anywhere static)
```

## How to run it

```sh
make build      # python3 build.py  -> regenerates dist/, needs pandoc
python3 -m http.server --directory dist 8000
# then open http://localhost:8000/ in a browser
```

(The built pages need no server at all — you can open `dist/index.html` directly in a file browser.)

## Verification results

Run on 2026-11-08 with Python 3.13.5 / pandoc 3.13:

| Check | Command | Result |
|---|---|---|
| Build | `python3 build.py` | 7/7 pages built, 0 errors |
| Trackers | grep `<script>` / `<img>` / `<iframe>` over dist/ | 0 / 0 / 0 |
| Internal links | `python3 linkcheck.py --internal` | 45/45 OK |
| External links (network) | `python3 linkcheck.py` | 63 OK, 3 WARN-BLOCKED, 0 FAIL, exit code 0 |

The 3 warnings are deliberate, documented, and bounded: MyPlate.gov and SNAP-Ed (USDA `fns.usda.gov`) refuse or time out non-browser datacenter traffic from this network while serving real visitors, and Cooking on a Bootstrap returns 403 to bot-flagged requests. They are real, long-established sites — the checker treats them as warnings, and only genuine `404`/`410`/5xx/malformed-URL findings make the run fail (non-zero exit).

MIT license verified present at `LICENSE` with the exact required line: `Copyright (c) 2026 Asdale Dynamics, LLC` (verbatim, no leading "the").

## Known gaps

- **Warnings, not entries-risk-free:** the three WARN-BLOCKED sites above can't be content-verified from datacenter networks; they were validated by reputation and structure, not HTTP 200, and could change hosting in future.
- **No CI:** link checks run locally (`make check`); wiring them to a scheduled job is a natural next step since external link rot is the main ongoing risk for a links directory.
- **No sitemap/RSS**; adding `sitemap.xml` and an RSS feed of "new picks" would help future discoverability.
- **Recipe content drift** at the picks is normal (blogs rebrand/restructure); the checker catches dead links but not silently-gated content, e.g. a site quietly adding a paywall mid-article.
- **UK weights** in Cooking on a Bootstrap are metric-first; a reader in the US has to convert.
