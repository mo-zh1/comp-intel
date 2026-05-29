---
name: competitor-research
description: Deep-research the mining + AI competitors already in the tracker and update their profile fields in the Google Sheet. Use this whenever the user wants to refresh or update competitor profiles, fill in missing details (founders, funding, investors, valuation, business model, technical stage), research the companies in the tracker, or run an "update pass" — even if they don't say "research". This is step 2 of the discovery → research → dashboard pipeline. For each company it runs web search + page fetches, extracts the agreed fields, and writes clean updates (never blanking existing values, never inventing data).
---

# Competitor Research

## What this does and why

This is **step 2 of 3** (discovery → research → dashboard). `competitor-discovery` adds companies with just a name + website; this skill fills in the rest of their profile and keeps it current. Quality and trust matter more than speed: a profile is only useful if every value is real and sourced, so **leave a field empty rather than guess**.

The tracker is one Google Sheet. You read it and write to it only through the bundled scripts.

## Tools you use

- **`scripts/list_companies.py`** — get the current companies and which fields are still empty.
- **WebSearch** — find the latest facts about each company.
- **WebFetch** — open the official site, Crunchbase/PitchBook, press releases, or news to confirm a value (prefer 2+ independent sources).
- **`scripts/upsert_research.py`** — the only way to write field updates.

## Workflow

1. **See what needs work.** Run:

```bash
python scripts/list_companies.py --missing-only
```

This prints each company with its current values and a `missing_fields` list. Prioritise empty fields, but you may also re-verify stale ones.

2. **Research each company (WebSearch → WebFetch).** For each company, search for the fields below, then fetch a primary source to confirm. Cross-check at least two independent sources for funding/valuation where possible. Capture the value only when a real source supports it.

3. **Write clean updates.** Pipe the results as JSON to the upsert script:

```bash
echo '[{"company": "Terra AI",
        "fields": {
          "Founders": "John Mern (CEO, Stanford PhD), Anthony Corso (CTO, Stanford PhD)",
          "Founded Year": "2023",
          "Business Model": "Enterprise B2B AI platform (SaaS) for mining & energy majors",
          "Technical stage": "Diffusion/generative subsurface models + reasoning agent for campaign planning",
          "Latest Round": "Seed · $3.39M · Oct 2023",
          "Funding Trajectory": "NSF grants -> Seed $3.39M (2023, Khosla) -> Rio Tinto strategic (2025) -> Series A announced",
          "Investors": "Khosla Ventures (lead), Rio Tinto (strategic), Plug and Play, Climate Capital, NSF",
          "Valuation": ""
        }}]' \
  | python scripts/upsert_research.py
```

The script matches by Company Name, **never overwrites a non-empty value with an empty one**, skips unchanged values, creates the row if the company is missing, and prints `{"updated": [...], "created": [...], "skipped_fields": [...], "failed": [...]}`.

4. **Report.** Summarise which companies/fields you updated and which fields you left empty because you couldn't confirm them. Suggest running `competitor-dashboard` to refresh the view.

## Field guide (the sheet's columns)

Fill these with confirmed, concise values. Match the style of the examples.

- **Company Name** — canonical name (the match key; don't change it).
- **Website** — official homepage URL.
- **Founders** — names + role/background, e.g. `Grant Sanden (CEO, U Calgary), Yannai Segal (CSO)`.
- **Founded Year** — founding year (+ location if useful), e.g. `2013` or `2019 (Toronto, Canada)`.
- **Business Model** — how they make money / GTM, e.g. `B2B SaaS sold to mining majors via direct sales`.
- **Technical stage** — the core technology and where in the mining lifecycle it applies, e.g. `CNN on multi-sensor core scans; resource definition stage`.
- **Latest Round** — most recent round, amount, date, e.g. `Series B · $44M · Jul 2025 (led by Blue Earth Capital)`.
- **Funding Trajectory** — the funding history in one line, e.g. `Seed -> Series A $30M (2023) -> Series B $44M (2025); ~$74M total`.
- **Investors** — notable investors, leads marked, e.g. `Breakthrough Energy Ventures (lead), BHP Ventures, Rio Tinto`.
- **Valuation** — only if publicly reported; otherwise leave empty, e.g. `USD $525M (Series D Dec 2024)` or ``.

## Rules that matter

- **No hallucination.** Only write a value you confirmed from a real source you fetched. Unknown → leave empty (the script will keep any existing value).
- **Don't blank good data.** Sending `""` for a field is a no-op on existing values by design — use it freely as a placeholder when you don't have an update.
- **Concise but informative.** One tight line per field, matching the examples; this is a tracker, not a report.
