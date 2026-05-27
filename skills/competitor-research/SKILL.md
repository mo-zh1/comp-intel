---
name: competitor-research
description: Deep research and continuous field updates for known competitors. Takes a list of companies from Google Sheets and performs comprehensive web scraping (official websites, LinkedIn, news, job boards) to extract and update fields: founders, investors, funding history, team size, core products, pricing models, customer types, recent hiring signals, partnerships, and major events. Performs automatic entity resolution with configurable merge logic—high-confidence matches (>0.95) auto-merge, medium confidence (0.85-0.95) use decision logic, low confidence (<0.85) retain all sources. Generates event logs (funding rounds, leadership changes, product launches) and raw signal archives for full provenance tracking. Use this skill daily to keep competitive profiles current with the latest market signals.
---

# Competitor Research Skill

## Overview

This skill performs deep, systematic research on each known competitor in your list. It:
- Scrapes official company websites, LinkedIn profiles, news articles, and job postings
- Extracts structured fields: founders, investors, team size, products, pricing, customers, recent events
- Automatically merges new data with historical records using configurable confidence thresholds
- Generates event logs (funding, hiring, partnerships) for timeline visualization
- Archives raw signals (source URLs, extracted values, timestamps) for full auditability

The skill is designed for **daily runs** to keep competitive intelligence current.

## When to Use

✅ **Use this skill when:**
- You have a curated list of competitors and want daily field updates
- You need to track funding rounds, leadership changes, product launches across multiple companies
- You want automatic merge logic (no human review required) with full source provenance
- You need event timelines and hiring signal tracking

❌ **Don't use this skill for:**
- One-off deep dives on a single company (use `probe` action in competitor-research directly)
- Discovering new competitors (use `competitor-discovery` skill instead)
- Visualization or dashboard generation (use `competitor-dashboard` skill)

## Input Schema

```json
{
  "action": "deep_research",
  "config": {
    "companies_source": "google_sheet",
    "sheet_id": "YOUR_SHEET_ID",
    "research_depth": "full",
    "scrape_targets": [
      "company_website",
      "linkedin_company_profile",
      "news_mentions",
      "job_postings",
      "team_pages"
    ],
    "merge_strategy": "auto",
    "merge_thresholds": {
      "auto_merge": 0.95,
      "decision_logic": 0.85,
      "discard": 0.70
    }
  }
}
```

**Parameters:**
- `action`: `"deep_research"` (for all known companies) or `"probe"` (single company)
- `companies_source`: `"google_sheet"` (reads from Google Sheets)
- `research_depth`: `"full"` (all fields) or `"incremental"` (only changed fields)
- `scrape_targets`: Which sources to scrape
- `merge_strategy`: `"auto"` (no human review) or `"staging"` (requires human approval)
- `merge_thresholds`: Confidence levels for different merge behaviors

## Process

### 1. Load Companies from Google Sheets

For each company in the `companies` tab with status `active` or `discovered`:
- Extract: name, website, linkedin_url, founders, investors, team_size, latest_round, etc.
- Note: all existing values for comparison with new data

### 2. Web Scraping & Field Extraction

For each company, scrape:

**Official Website:**
- /about, /team, /products, /pricing, /investors, /news pages
- Extract: description, founders, team size, products, pricing model

**LinkedIn Company Profile:**
- Followers, company size, description
- Extract: team size, recent hires (from follower activity if available)

**News & Announcements:**
- Search: "[Company Name] funding", "[Company Name] hiring", "[Company Name] partnership"
- Extract: funding announcements, leadership changes, partnerships, acquisitions

**Job Postings:**
- LinkedIn Jobs, Wellfound, company careers page
- Extract: open positions, hiring signals, team growth

### 3. Field Extraction via LLM

For each scraped page, use Claude to extract structured fields:

```json
{
  "company_id": "terra-ai",
  "extracted_fields": {
    "founders": [
      {
        "name": "John Merrill",
        "title": "CEO",
        "background": "Stanford PhD - SISL Lab",
        "extracted_from": "website/about",
        "confidence": 0.98
      }
    ],
    "team_size": {
      "value": 42,
      "source": "linkedin",
      "extracted_at": "2026-05-27",
      "confidence": 0.95
    },
    "latest_round": {
      "type": "Series A",
      "amount_usd": 15000000,
      "date": "2026-05-20",
      "source": "crunchbase",
      "confidence": 0.90
    },
    "events": [
      {
        "event_type": "funding_round",
        "date": "2026-05-20",
        "details": "Series A $15M led by Breakthrough Energy Ventures",
        "confidence": 0.92
      }
    ]
  }
}
```

### 4. Entity Resolution & Merge

For each field, compare new value with existing value:

**High Confidence (>= 0.95):**
- Automatically adopt new value
- Mark as `auto-merged`
- Preserve old value in raw_signals for audit

**Medium Confidence (0.85-0.95):**
- Apply decision logic:
  - If new source is more recent → adopt new value
  - If new source is more authoritative (official site > news) → adopt new value
  - If values differ but both credible → keep both in raw_signals, mark as `multi-sourced`
- No human intervention required

**Low Confidence (< 0.85):**
- Discard the low-confidence value
- Log in error log
- Keep existing value unchanged

### 5. Event Log Generation

Extract and categorize major events:

```json
{
  "events": [
    {
      "company_id": "terra-ai",
      "event_type": "funding_round",
      "date": "2026-05-20",
      "description": "Series A $15M from Breakthrough Energy Ventures",
      "amount_usd": 15000000,
      "source_urls": ["crunchbase.com/...", "techcrunch.com/..."],
      "confidence": 0.95
    },
    {
      "company_id": "terra-ai",
      "event_type": "hiring_surge",
      "date": "2026-05-27",
      "description": "12 new job openings posted (geology ML + product engineers)",
      "signal_strength": "medium",
      "source_urls": ["linkedin.com/company/terra-ai/jobs"]
    }
  ]
}
```

**Event Types:**
- `funding_round` — new funding announcement
- `acquisition` — company acquired or acquired another company
- `leadership_change` — founder/CXO departure or hire
- `product_launch` — new product or major feature
- `partnership` — new customer, supplier, or strategic partnership
- `hiring_surge` — cluster of new job postings
- `expansion` — new office, geographic expansion
- `news_mention` — press coverage

### 6. Raw Signals Archive

For every extracted value, create an entry in raw_signals:

```json
{
  "company_id": "terra-ai",
  "field": "team_size",
  "value": 42,
  "source_url": "linkedin.com/company/terra-ai",
  "source_type": "linkedin",
  "extracted_at": "2026-05-27T18:00:00Z",
  "confidence": 0.95,
  "raw_content_preview": "Employees at Terra AI on LinkedIn: 42 followers..."
}
```

### 7. Update Google Sheets

Write results to Sheets:
- **companies tab**: Update all fields with new data
- **events tab**: Append new events
- **update_log tab**: Create one row per field change (timestamp, company, field, old, new, source)
- **raw_signals tab**: Append all extracted values with URLs and confidence

## Output Schema

```json
{
  "run_date": "2026-05-27",
  "companies_processed": 12,
  "companies_updated": 9,
  "new_events_found": 47,
  "results": {
    "updated_companies": [
      {
        "name": "Terra AI",
        "fields_updated": ["team_size", "latest_round"],
        "events_new": 3,
        "timestamp": "2026-05-27T18:30:00Z"
      }
    ],
    "new_events": [
      {
        "company": "Terra AI",
        "event_type": "funding_round",
        "date": "2026-05-20",
        "details": "Series A $15M",
        "confidence": 0.95
      }
    ],
    "errors": [
      {
        "company": "Stealth Co",
        "error": "Website returned 403 Forbidden",
        "timestamp": "2026-05-27T18:15:00Z"
      }
    ]
  }
}
```

## Merge Logic (Key Design)

This skill does **NOT** require human review for merges. All decisions are automatic:

1. **Timestamp-based**: Newer values generally override older ones
2. **Source authority**: Official website > LinkedIn > News > Social media
3. **Confidence scoring**: Based on extraction reliability and source credibility
4. **Multi-source retention**: If values conflict but both are credible, keep both in raw_signals

**Example merge scenarios:**
- LinkedIn says 25 employees, website says 35 → Keep both, mark as `multi-sourced`, use website as primary (more authoritative)
- Press release says $50M funding, Crunchbase says $45M → Use press release (more recent source), note discrepancy
- Wikipedia says founded 2020, company website says 2019 → Use company website (more authoritative)

## Scheduling

Designed for **daily execution** at 18:00 UTC. For larger company lists (50+ companies), may take 30-90 minutes depending on site responsiveness.

## Error Handling

- Timeouts on individual company pages → log error, continue with next company
- API rate limits → implement exponential backoff
- Missing fields → don't error, just leave blank with note "data unavailable"
- Malformed data → log and skip that extraction, preserve old value

