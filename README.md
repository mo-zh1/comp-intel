# Mohan Competitive Intelligence

Automated daily competitive intelligence pipeline for mining & AI sectors. Discovers new competitors, deep-researches known companies, and generates interactive dashboards.

## 3-Stage Pipeline

1. **competitor-discovery** — Daily source scanning for new competitors + related companies
2. **competitor-research** — Deep field updates on known competitors (auto-merge, no human review)
3. **competitor-dashboard** — Static HTML dashboard + CSV exports for GitHub archival

## Quick Start

### Run Skill 1: Discovery
```bash
# Scan data sources for new competitors
# Input: existing companies list from Google Sheets
# Output: new_competitors, new_related_companies, existing_with_signals
```

### Run Skill 2: Research
```bash
# Deep research all active companies
# Input: companies list from Google Sheets
# Output: merged fields + events + raw signals
```

### Run Skill 3: Dashboard
```bash
# Generate HTML dashboard + export CSVs
# Input: Google Sheets snapshot
# Output: index.html + competitors.csv + events.csv + update_log.csv
```

## Architecture

```
Skills (Anthropic format)
  ├── competitor-discovery/
  │   ├── SKILL.md
  │   └── evals.json
  ├── competitor-research/
  │   ├── SKILL.md
  │   └── evals.json
  └── competitor-dashboard/
      ├── SKILL.md
      └── evals.json

Data (version controlled)
  ├── data/
  │   ├── competitors.csv (latest snapshot)
  │   ├── events.csv
  │   ├── update_log.csv
  │   └── archive/
  │       └── competitors_YYYY-MM-DD.csv (historical)
  └── dashboard/
      └── index.html (latest)

Config
  └── config.yaml (data sources, merge thresholds, etc.)
```

## Daily Workflow (18:00 UTC)

```
18:00 → Skill 1: competitor-discovery (~15 min)
  ↓ (new discoveries → Google Sheets)
18:15 → Skill 2: competitor-research (~30-60 min)
  ↓ (field updates + events → Google Sheets)
19:15 → Skill 3: competitor-dashboard (~5-10 min)
  ↓ (HTML + CSVs → GitHub)
19:25 → Complete
```

## Setup

1. Create Google Sheet with these tabs:
   - `companies` — main company list
   - `events` — funding/hiring/partnership events
   - `update_log` — field change history
   - `raw_signals` — source URLs and extracted values

2. Configure data sources in `config.yaml`

3. Deploy skills via Anthropic Claude or OpenClaw

4. Schedule daily cron at 18:00

## Key Design Decisions

- **Auto-merge, no human review** — Skill 2 uses confidence thresholds (0.95/0.85) for automatic merge
- **Multi-source data retention** — All sources preserved in raw_signals for auditability
- **CSV version control** — Daily snapshots archived in GitHub for history tracking
- **Self-contained dashboard** — Single HTML file, works offline, all data embedded
- **Modular skills** — Each skill does one thing well; can be run independently or as pipeline

## Merge Logic (Skill 2)

- **>= 0.95 confidence** → Auto-merge, no questions asked
- **0.85-0.95 confidence** → Decision logic applied (timestamp, source authority)
- **< 0.85 confidence** → Discard, log reason

## Event Types (Tracked)

- funding_round
- acquisition
- leadership_change
- product_launch
- partnership
- hiring_surge
- expansion
- news_mention

## References

- Anthropic skill-creator: https://github.com/anthropics/skills
- Mohan Technologies: https://mohan.tech

