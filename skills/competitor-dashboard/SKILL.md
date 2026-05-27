---
name: competitor-dashboard
description: Generate static HTML dashboard and export CSV snapshots from Google Sheets competitive intelligence data. Reads current company list, funding events, and update history from Sheets, renders an interactive single-page HTML dashboard with company search, timeline visualization, investor relationship mapping, and update log viewer. Automatically exports companies, events, and update_log as CSV files for archival to GitHub. Use this skill daily (typically as final step after competitor-discovery and competitor-research) to publish current competitive landscape snapshot and maintain historical CSV record in version control.
---

# Competitor Dashboard Skill

## Overview

This skill generates shareable, visual representations of your competitive intelligence data. It:
- Reads the latest snapshot from Google Sheets (companies, events, update_log)
- Generates an interactive HTML dashboard with search, filters, and timeline visualization
- Exports CSV snapshots for GitHub archival and version control
- Supports offline viewing (all data embedded in HTML)

The skill is designed as the **final step** in your daily intelligence pipeline, executed after discovery and research are complete.

## When to Use

✅ **Use this skill when:**
- You want to publish a current snapshot of the competitive landscape
- You need to share competitive intel with stakeholders via a shareable HTML file
- You want to maintain historical CSV backups in GitHub
- You're ready to finalize a day's research into a consumable format

❌ **Don't use this skill for:**
- Running discovery or research (use competitor-discovery and competitor-research skills)
- Real-time or multi-user collaborative editing (use Google Sheets directly)
- Custom analytics beyond basic timeline/search (export CSV and build custom dashboards)

## Input Schema

```json
{
  "action": "export_dashboard",
  "config": {
    "sheet_id": "YOUR_SHEET_ID",
    "include_tabs": [
      "companies",
      "events",
      "update_log"
    ],
    "dashboard_features": [
      "company_search",
      "investor_timeline",
      "funding_heatmap",
      "update_log_viewer"
    ],
    "export_formats": ["html", "csv"],
    "github_push": true,
    "github_config": {
      "repo": "mohan-competitive-intelligence",
      "branch": "main",
      "commit_message_template": "[auto] daily dashboard update — {date}"
    }
  }
}
```

**Parameters:**
- `action`: `"export_dashboard"`
- `sheet_id`: Google Sheet ID containing competitive data
- `include_tabs`: Which sheets to export (companies, events, update_log)
- `dashboard_features`: Visual components to render (search, timeline, heatmap, etc.)
- `export_formats`: Output file types (`html`, `csv`, or both)
- `github_push`: Whether to auto-commit to GitHub
- `github_config`: Repo details and commit message template

## Process

### 1. Load Data from Google Sheets

Fetch data from multiple tabs:

**Companies Tab:**
- company_id, canonical_name, website, linkedin_url, founders, investors, team_size, latest_round_type, latest_round_amount_usd, latest_round_date, core_product, pricing_model, target_customer, business_status, last_updated, confidence_score, discovered_source

**Events Tab:**
- company_id, event_type, event_date, description, amount_usd (if applicable), source_urls, confidence

**Update Log Tab:**
- timestamp, company_name, field, old_value, new_value, source_url, confidence, status

### 2. HTML Dashboard Generation

Build an interactive single-page app (SPA) with sections:

#### **Header & Metadata**
- Dashboard title: "Mohan Competitive Intelligence"
- Last updated timestamp
- Total companies tracked
- Recent events count

#### **Company Search & Directory**
```
[ Search box (name, website, founder) ]

Results displayed as:
  | Company Name | Founders | Investors | Latest Round | Team Size | Updated |
  | Terra AI     | John M.  | Khosla    | Series B $?  | 42        | 2h ago  |
  | GeologicAI   | Grant S. | Venture X | Series B $44M| 89        | 1d ago  |
  ...
```

Features:
- Case-insensitive search across company name, founder names, investor names
- Filter by status (active, acquired, stealth, related)
- Sort by columns (last_updated, team_size, funding_amount)
- Click to expand company detail view

#### **Investor Timeline**
Horizontal timeline showing funding events chronologically:
```
2023  |----Seed-----|
2024  |------Series A------|------Series B------|
2025  |-----Series C-----|
```
- X-axis: time
- Each bar represents a funding round
- Color-coded by round type (Seed → Blue, Series A → Green, etc.)
- Hover for details

#### **Funding Heatmap**
Matrix visualization:
```
        2023    2024    2025
Seed     3       5       2
A        2       7       4
B        1       4       3
C        0       1       2
```
Cell color intensity = number of rounds in that period

#### **Update Log Viewer**
Recent field changes:
```
Date       Company      Field         Old Value    New Value       Source
2026-05-27 Terra AI     team_size     40           42              LinkedIn
2026-05-27 GeologicAI   latest_round  Series A     Series B $44M   Crunchbase
...
```

#### **Company Detail View**
When user clicks on a company:
```
TERRA AI
Website: terraai.com | LinkedIn: linkedin.com/company/terra-ai

Founders:
  • John Merrill (CEO) — Stanford PhD
  • Anthony Corso (CTO) — Stanford

Team Size: 42 (last updated 2026-05-27 via LinkedIn)

Latest Round: Series A $15M (2026-05-20)
  Lead: Breakthrough Energy Ventures
  Investors: [Khosla Ventures, ...]

Products: Subsurface mapping with generative models

Pricing Model: Enterprise B2B SaaS

Target Customers: Mining majors (Rio Tinto, BHP)

Recent Events:
  • 2026-05-20 — Series A $15M funding
  • 2026-05-15 — Hired Chief Product Officer
  • 2026-05-10 — Partnership with Rio Tinto

Signal Sources:
  team_size: LinkedIn (confidence 0.95) | Website (confidence 0.90)
  latest_round: Crunchbase (confidence 0.92) | TechCrunch (confidence 0.88)
```

### 3. CSV Export

Generate three CSV files with current snapshots:

**competitors.csv**
```
Company Name,Website,Founders,Investors,Team Size,Latest Round Type,Latest Round Amount USD,Latest Round Date,Core Product,Pricing Model,Target Customer,Business Status,Last Updated,Confidence Score
Terra AI,terraai.com,"John Merrill, Anthony Corso","Khosla Ventures, Breakthrough Energy",42,Series A,15000000,2026-05-20,Subsurface mapping SaaS,Enterprise B2B SaaS,Mining majors,active,2026-05-27,0.92
...
```

**events.csv**
```
Company ID,Company Name,Event Type,Event Date,Description,Amount USD,Source URLs,Confidence
terra-ai,Terra AI,funding_round,2026-05-20,Series A $15M from Breakthrough Energy,15000000,crunchbase.com/...|techcrunch.com/...,0.95
terra-ai,Terra AI,hiring_surge,2026-05-27,12 job openings for ML engineers,0,linkedin.com/company/terra-ai/jobs,0.88
...
```

**update_log.csv**
```
Timestamp,Company Name,Field,Old Value,New Value,Source URL,Confidence,Status
2026-05-27T18:30:00Z,Terra AI,team_size,40,42,linkedin.com/company/terra-ai,0.95,auto_merged
2026-05-27T18:25:00Z,Terra AI,latest_round,Series A $?M,Series A $15M,crunchbase.com,0.92,decision_merged
...
```

### 4. GitHub Push (Optional)

If `github_push: true`, automatically:
1. Commit CSVs to repo:`/data/competitors.csv`, `/data/events.csv`, `/data/update_log.csv`
2. Push HTML to repo:`/dashboard/index.html`
3. Archive old CSVs to:`/data/archive/competitors_YYYY-MM-DD.csv`
4. Commit message: `[auto] daily dashboard update — 2026-05-27`

## HTML Output Structure

Single-page HTML file with embedded data (no external files needed):

```html
<!DOCTYPE html>
<html>
<head>
    <title>Mohan Competitive Intelligence</title>
    <style>/* CSS for dashboard styling */</style>
</head>
<body>
    <div id="app">
        <nav>Search | Timeline | Heatmap | Updates | Download</nav>
        <section id="company-search">...</section>
        <section id="funding-timeline">...</section>
        <section id="update-log">...</section>
        <footer>Last updated: 2026-05-27 | Export date: CSV links</footer>
    </div>
    <script>
        // Data embedded as JSON
        const companiesData = [{...}];
        const eventsData = [{...}];
        
        // Search, filter, render functions
        function search(query) {...}
        function renderTimeline(events) {...}
    </script>
</body>
</html>
```

## Dashboard Features

### Search
- Real-time search across company name, founder name, investor name
- Case-insensitive, partial matching
- Filter results by status (active, acquired, stealth, related)

### Timeline
- Chronological view of all funding rounds
- Color-coded by round type
- Hover for round details

### Heatmap
- 2D matrix of funding activity by year and round type
- Shows distribution of capital across time periods

### Update Log
- Recent field changes, sorted by timestamp
- Shows before/after values and source
- Filter by company or field type

### Export
- Download buttons for CSV files
- Copy company data to clipboard
- Share dashboard URL

## Output Files

**Primary:**
- `index.html` — Complete interactive dashboard (self-contained, offline-readable)
- `competitors.csv` — Companies snapshot
- `events.csv` — Events snapshot
- `update_log.csv` — Update history snapshot

**Secondary (if GitHub push enabled):**
- Commit to GitHub with timestamped message
- Archive previous day's CSV in `/data/archive/`

## Error Handling

- If Google Sheet is unreachable, use cached data from last successful export
- Missing fields render as "Data unavailable"
- Malformed dates are skipped and logged
- If GitHub push fails, export still succeeds (Sheets data is primary)

## Performance Notes

- For 50+ companies, HTML generation takes ~5-10 seconds
- CSV export is <1 second
- GitHub push takes ~2-5 seconds (depends on network)
- Total runtime: typically 10-20 seconds

## Customization

The HTML dashboard can be customized post-generation:
- Change color scheme (CSS)
- Add/remove columns from company table
- Modify visualization types (timeline, heatmap, etc.)
- Add custom filters or groupings

