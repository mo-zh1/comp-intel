---
name: competitor-discovery
description: Find NEW mining + AI competitor companies and add them to the tracker Google Sheet. Use this whenever the user wants to discover newly emerged competitors, scan the mining-tech / mineral-exploration-AI landscape for new entrants, expand or refresh the competitor list, or "see what's new in the space" — even if they don't say the word "discovery". This is step 1 of the discovery → research → dashboard pipeline. It searches the web broadly, verifies each candidate by fetching its site, de-duplicates against the existing sheet, and appends only genuinely new companies (name + website).
---

# Competitor Discovery

## What this does and why

This is **step 1 of 3** in the competitor-intel pipeline (discovery → research → dashboard). Its only job is to find companies that are **not yet in the tracker** and append them with their name and website. The deep profile fields are filled later by `competitor-research`, so do not try to research funding/founders here — just find real, in-scope companies and confirm they exist.

The tracker lives in one Google Sheet. The shared client (`google_sheet_api.py`) and the append script handle all writes, so you never touch the sheet directly.

## Tools you use

- **WebSearch** — broad discovery across the source library.
- **WebFetch** — open a candidate's site or the announcing article to confirm it's a real, in-scope company and read its canonical name + homepage URL.
- **`scripts/append_companies.py`** — the only way to write to the sheet.

## Workflow

1. **Load context.** Read `references/data-sources.md` for where to look, the search angles, and the scope filter. Skim the current tracker so you don't rediscover known companies — the append script also de-dupes, but knowing the existing names makes your searches sharper. (You can get the current list from the `competitor-research` skill's `list_companies.py`, or just rely on the append script's `skipped_existing` report.)

2. **Search broadly (WebSearch).** Work through the source library and search angles. Collect candidate company names plus the URL where you saw them.

3. **Verify each candidate (WebFetch).** Open the company site or the source article. Keep a candidate only if you can confirm:
   - it is a real, currently-operating company (or freshly announced startup), and
   - it fits the scope (mining + AI / mineral-exploration AI / geoscience ML, etc.), and
   - you have its canonical name and homepage URL.
   If you cannot confirm a real company with a real URL, **drop it** — never invent a company or a website.

4. **Append the confirmed new companies.** Pipe them as JSON to the script:

```bash
echo '[{"Company Name": "Earth AI", "Website": "https://earthai.ai"},
       {"Company Name": "Fleet Space Technologies", "Website": "https://www.fleetspace.com/"}]' \
  | python scripts/append_companies.py
```

The script reads the sheet header, skips any company already present (case-insensitive name match), appends the rest, and prints `{"appended": [...], "skipped_existing": [...], "failed": [...]}`.

5. **Report.** Tell the user which companies were added and which were skipped as already-tracked. Suggest running `competitor-research` next to fill in their details.

## What to put in each row

Discovery only supplies two fields; leave everything else for `competitor-research`:

- **Company Name** — the canonical company name (what they call themselves).
- **Website** — the official homepage URL (prefer the real site over an aggregator page).

The sheet's full column set (managed elsewhere) is: Company Name, Website, Founders, Founded Year, Business Model, Technical, stage, Latest Round, Funding Trajectory, Investors, Valuation, source：.

## Rules that matter

- **No hallucination.** Every appended company must be backed by a real URL you actually fetched. When unsure, drop it.
- **New only.** Don't re-add companies already in the sheet; the script enforces this but aim for it in your search too.
- **Stay in scope.** Use the scope filter in `references/data-sources.md`.
