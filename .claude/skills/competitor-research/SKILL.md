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

2. **Research each company (WebSearch → WebFetch).** For each company, search broadly, then fetch the primary sources to confirm each field. Cross-check **2+ independent sources** for funding/valuation. Capture a value only when a real source supports it, and keep the URLs you actually used — they go in the `source：` field.

   **For `Investors` and `Funding Trajectory` specifically — mandatory extra step:** always fetch the company's Crunchbase funding page (`crunchbase.com/organization/<slug>/funding_rounds`) and Tracxn funding page (`tracxn.com/d/companies/<slug>/…/funding-and-investors`). These databases enumerate every round with every investor — news articles only cover the latest round and routinely omit early-round backers (often the most notable VCs). Do not write the Investors field until you have checked at least one of these two sources.

3. **Self-check before writing.** Before piping to upsert, verify investor completeness: count the number of distinct funding rounds named in `Funding Trajectory`. Confirm you have at least one named investor per round. If any round is missing investors, run one more search (`"<company> Series A investors"`, `"<company> Series B investors"`, etc.) before writing. This catches the common failure mode where only the latest-round investors are captured.

4. **Write clean updates.** Pipe the results as JSON to the upsert script. Write everything in **English** (search and content are English-only — do not translate or mix in other languages). Field values should be **rich and analytical** (see depth note below):

```bash
echo '[{"company": "Terra AI",
        "fields": {
          "Founders": "John Mern (CEO, Stanford PhD - SISL), Anthony Corso (CTO, Stanford PhD)",
          "Founded Year": "2023",
          "Business Model": "Enterprise B2B AI platform (SaaS) — sold via direct sales + strategic partnerships to mining & energy majors",
          "Technical": "Diffusion / generative models (confirmed, multiple sources). Generates millions of possible 3D subsurface models conditioned to match the signal + a reasoning agent for campaign planning. Data = real multimodal: drill cores + geophysics + geochemistry (synthetic data is only model output, not training input)",
          "stage": "Multi-stage: Target Screening (greenfield/undercover) + Survey Design + Dynamic Drilling (resource definition)",
          "Latest Round": "Seed · $3.39M · Oct 2023 (publicly announced 2025 when emerging from stealth)",
          "Funding Trajectory": "NSF grants → Seed $3.39M (2023, led by Khosla Ventures) → Rio Tinto strategic investment (2025) → Series A upcoming (announced intent, not closed)",
          "Investors": "Khosla Ventures (lead), Rio Tinto (strategic, 2025), Storyhouse Ventures, Plug and Play, Climate Capital, US NSF",
          "Valuation": "Undisclosed (Seed $3.4M 2023, led by Khosla; no valuation disclosed)",
          "source：": "https://www.choppingblock.ai/companies/terra-ai\nhttps://www.terraai.com/minerals\nhttps://www.khoslaventures.com/portfolio"
        }}]' \
  | python scripts/upsert_research.py
```

The script matches by Company Name, **never overwrites a non-empty value with an empty one**, skips unchanged values, creates the row if the company is missing, and prints `{"updated": [...], "created": [...], "skipped_fields": [...], "failed": [...]}`.

5. **Report.** Summarise which companies/fields you updated and which fields you left empty because you couldn't confirm them. Suggest running `competitor-dashboard` to refresh the view.

## Field guide (the sheet's columns)

Fill these with confirmed values. The tracker favours **depth over brevity** — match the style of the example above.

- **Company Name** — canonical name (the match key; don't change it).
- **Website** — official homepage URL.
- **Founders** — names + role + background, e.g. `Grant Sanden (CEO, Co-founder, U Calgary), Yannai Segal (CSO, Co-founder)`.
- **Founded Year** — founding year + location + any pivot history, e.g. `2013 (originally Enersoft, oil & gas; pivoted to mining 2021)`.
- **Business Model** — how they make money + GTM + positioning, a full descriptive sentence.
- **Technical** — the core technology in depth: model architecture, data types, what's confirmed vs claimed. This is the richest field; note diffusion / CNN / GNN / foundation-model claims and real vs synthetic data.
- **stage** — where in the mining lifecycle it applies, e.g. `Multi-stage: Target Screening (greenfield) + Survey Design + resource definition` or `Production-stage mines + brownfield (NOT greenfield)`.
- **Latest Round** — most recent round, amount, date, lead, e.g. `Series B · $44M USD · Jul 2025 (led by Blue Earth Capital)`.
- **Funding Trajectory** — the full funding history in one cell, with totals, e.g. `Seed → Series A $30M (2023) → Series B $44M (2025); ~$74M total`.
- **Investors** — list investors **by round** (e.g. `Series A: a16z, Breakthrough Energy Ventures; Series B: T. Rowe Price (lead), CPP Investments, BHP Ventures; Series C: Durable Capital (co-lead), T. Rowe Price (co-lead)…`). Mark round leads. Include notable individual angels separately. Aim for completeness across **all rounds**, not just the latest — early-round investors (often top VCs) frequently appear only in older news or Crunchbase, not in the most recent press coverage.
- **Valuation** — only if publicly reported; otherwise note `Undisclosed` with brief reason, e.g. `Undisclosed (Series B $44M, declined to disclose)` or `USD $525M (Series D Dec 2024)`.
- **source：** — **all** the source URLs you used, newline-separated: be broad and complete, list every relevant page you consulted (official site, Crunchbase/PitchBook/Tracxn, press releases, news, filings), not just one or two. This is the provenance trail a human uses to verify, so err on the side of including more. Never leave it empty for a researched company.

## Depth and style

Write everything in **English only** — no translation, no mixed languages. Unlike a one-line tracker, this landscape favours **dense, analytical cells** — full sentences, several clauses. Mark confidence and provenance inline, e.g. `(confirmed, multiple sources)`, `⚠️ N/A`, `(per PitchBook)`. The `Technical` and `Business Model` cells in particular should read like a short analyst note, not a tag.

## Rules that matter

- **No hallucination.** Only write a value you confirmed from a real source you fetched, and record that source in `source：`. Unknown → leave empty (the script keeps any existing value).
- **Don't blank good data.** Sending `""` for a field is a no-op on existing values by design — use it freely as a placeholder when you don't have an update.
- **Depth over brevity, but stay sourced.** Rich analysis is good; unsourced speculation is not. Every claim must trace to a URL in `source：`.
