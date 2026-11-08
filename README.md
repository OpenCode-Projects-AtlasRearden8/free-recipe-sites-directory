# free-recipe-sites-directory

A curated, human-friendly directory of **genuinely free** recipe sources:

- **Library & free-culture archives** — public-domain cookbooks and digital library collections
- **Government & extension nutrition sites** — USDA, NHLBI, and university SNAP-Ed recipe hubs
- **Budget-cooking blogs** — real people cooking on real grocery money
- **No-photo, fast-loading collections** — text-first sites that render instantly
- **Tonight helpers** — fridge-search and substitution tools
- **The Tonight Page** — a built-in, zero-photo list of dinner formulas you can cook without opening another tab

Every entry carries a two-line friendly blurb so you can flip to dinner fast.

## What this is (and is not)

- It is a links directory: short, salty, plain-English blurbs over deep research.
- It is **not** printables — see the sister project **free-kitchen-cheatsheet-pack** for that.
- It is **not** a planning method — see **meal-planning-with-ai-guide** for step-by-step meal planning.

## How to build

Requirements: Python 3.8+ and [pandoc](https://pandoc.org/installing.html).

```sh
make build      # or: python3 build.py
```

Static HTML is generated into `dist/`. Each page inlines a small stylesheet — no JavaScript, no external assets, no analytics, no trackers of any kind.

## How to check links

```sh
make check      # or: python3 linkcheck.py
```

The checker validates that every internal link resolves to a real page, then fetches every external URL. Stripe-soft rules: `404`/`410`/URL-scheme errors **fail the run**; datacenter-IP blocks (`403`/`429`) and network timeouts are reported as warnings because several libraries (MyPlate.gov, CDC-hosted domains) block synthetic traffic while serving real visitors fine.

## Verify everything

```sh
make all        # build, then link-check, then confirm output exists
```

## Privacy

This project makes no requests that are not the link check itself, ships no scripts, and collects nothing. Host it anywhere that serves static files.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Asdale Dynamics, LLC.

Brought to you by **[Asdale Dynamics, LLC]** — beginner-friendly AI education, books, and practical tools. Learn more at the whole customer hub: **dylanasdale.github.io**.

By **Dylan Asdale**, author of *The Massive AI Manual*.
