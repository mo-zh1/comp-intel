---
name: competitor-dashboard-simple
description: Render the competitor tracker into a black-gold HTML dashboard. Use when the user wants to generate or refresh the dashboard-simple view. Reads the live Google Sheet and writes dashboard-simple/index.html plus a timestamped archive copy. Uses agent (LLM) to clean investor names before rendering.
---

# Competitor Dashboard (Simple)

## What this does

Two-step pipeline: you (the agent) clean the investor data first, then the Python renderer produces a self-contained black-gold HTML dashboard at `dashboard-simple/index.html`.

Features: KPI summary (tracked / active / stealth / acquired), status filter pills, company table with HQ / ROUND / AMOUNT / DATE columns, D3.js force-directed investor network with charge + distance sliders, funding-stage bar chart, shared-investor list.

D3.js is bundled locally at `dashboard-simple/d3.min.js` — works offline.

## Workflow

### Step 1 — You extract clean investor lists

Run `list_companies.py` to get the current Investors field for all companies:

```bash
python .claude/skills/competitor-research/scripts/list_companies.py 2>&1
```

For each company, read the raw Investors text and identify **only actual investor / fund / VC names**. Exclude:
- Dollar amounts (`~$1.22B+`, `$163-280M`)
- Prose descriptions (`"lead not publicly disclosed"`, `"Individual angels:"`)
- Totals / summaries (`"Total: 21+ investors across 5 rounds"`)
- Negations (`"no external VC"`, `"no notable institutional VC backers identified"`)
- Status notes (`"~$1.22B+ raised"`)

Write the result to `/tmp/investor_overrides.json` as:

```json
{
  "KoBold Metals": [
    {"name": "Andreessen Horowitz", "lead": false},
    {"name": "Breakthrough Energy Ventures", "lead": false},
    {"name": "T. Rowe Price", "lead": true},
    {"name": "Durable Capital Partners", "lead": true},
    {"name": "Jeff Bezos", "lead": false}
  ],
  "Veracio": [
    {"name": "Boart Longyear", "lead": false}
  ]
}
```

**Only include companies whose Investors field contains noise.** Companies with clean, already-structured data can be omitted — the renderer falls back to its own parser for those.

### Step 2 — Run the renderer

```bash
python .claude/skills/competitor-dashboard-simple/scripts/render_dashboard.py \
  --overrides /tmp/investor_overrides.json
```

Without `--overrides`, the renderer uses its built-in regex parser (less accurate for noisy fields).

Open `dashboard-simple/index.html` in any browser.
