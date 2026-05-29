---
name: competitor-dashboard
description: Turn the competitor tracker Google Sheet into a CSV snapshot and an interactive HTML dashboard. Use this whenever the user wants to see, visualize, export, or share the competitive landscape, generate the dashboard, produce a snapshot/report of the tracked companies, or as the final step after discovery and research. This is step 3 of the discovery → research → dashboard pipeline. It reads the live sheet and renders everything with no hardcoded data.
---

# Competitor Dashboard

## What this does and why

This is **step 3 of 3** (discovery → research → dashboard). It reads the current state of the tracker Google Sheet and produces two artifacts so the landscape is easy to consume and version:

- `data/competitors.csv` — a flat snapshot (good for git history / spreadsheets).
- `dashboard/index.html` — a self-contained, searchable table (open in any browser, works offline).

Columns come from the sheet header at runtime, so the dashboard automatically matches whatever fields the tracker currently has — there is nothing to keep in sync.

## Workflow

1. Run the renderer:

```bash
python scripts/render_dashboard.py
```

2. It prints how many companies it rendered and the output paths. Point the user to `dashboard/index.html` (and mention `data/competitors.csv`).

That's it — this step is fully deterministic, so there's no web search or judgement involved. If the sheet looks empty, run `competitor-discovery` and `competitor-research` first.

## Notes

- The renderer reads through the shared `google_sheet_api.py` client; you don't access the sheet directly.
- Output files are written at the project root (`data/`, `dashboard/`), created if missing.
- Safe to run repeatedly — it overwrites the previous snapshot with the latest sheet contents.
