---
name: competitor-discovery
description: Discover new competitors and related companies in mining & AI sectors. Scans curated mining industry data sources (mining.com, discoveryalert.com.au, USGS, Mining Weekly) and public web search to identify emerging startups, established mining companies, and AI-in-mining firms. Performs fuzzy matching against known competitor list to classify results as new competitors, related companies (investors, suppliers, customers), or existing companies with new signals. Use this skill when you need to expand the competitive landscape, track industry movements, or identify potential partnerships and supplier relationships in mining tech and mineral discovery space.
---

# Competitor Discovery Skill

## Overview

This skill automates the discovery phase of competitive intelligence. It scans predefined mining industry data sources plus public web search to identify:
- **New competitors** — previously unknown companies in mining exploration AI, mining software, or mineral tech
- **Related companies** — investors (VCs, corporate venture arms), suppliers, customers, partners, and acquirers  
- **Existing companies with new signals** — known competitors mentioned in new contexts (funding, hiring, partnerships, news)

The skill handles entity resolution (fuzzy matching) to avoid duplicates and provides structured output ready for Google Sheets ingestion.

## When to Use

✅ **Use this skill when:**
- Running daily/weekly discovery scans to expand the competitive landscape
- You want to systematically track new entrants in mining AI and related sectors
- You need to identify investor relationships and supply chain connections
- You're building a curated list of players across mining exploration, critical minerals, and mineral tech

❌ **Don't use this skill for:**
- Deep research into existing competitors (use `competitor-research` skill instead)
- Analyzing market dynamics or strategy (use `competitor-dashboard` skill for visualization)

## Input Schema

```json
{
  "action": "discovery",
  "config": {
    "include_sources": [
      "mining_industry_news",
      "web_search",
      "investor_portfolios"
    ],
    "target_categories": ["mining_ai", "mineral_tech", "exploration_tech", "related_companies"],
    "existing_companies": [
      {
        "name": "Terra AI",
        "website": "terraai.com"
      }
    ],
    "fuzzy_match_threshold": 0.85
  }
}
```

**Parameters:**
- `action`: Always `"discovery"`
- `include_sources`: Array of source types to scan (see Data Sources section below)
- `target_categories`: Which types of companies to surface
- `existing_companies`: List of known competitors for fuzzy matching (to avoid rediscoveries)
- `fuzzy_match_threshold`: Confidence level for matching (0.0-1.0, default 0.85)

## Process

### 1. Source Scanning

Scan each configured source for company mentions, funding announcements, partnerships, acquisitions:

**Mining Industry News:**
- mining.com (articles, news, deals)
- mining-weekly.com (news, funding rounds)
- discoveryalert.com.au (exploration discoveries)
- USGS periodicals (US mineral production data)
- Canada Natural Resources reports (Canadian mining stats)

**Web Search:**
- "mining AI startup funding 2026"
- "mineral exploration software"
- "lithium mining technology"
- Related keywords from discovered companies

**Investor Portfolios:**
- LinkedIn searches for "mining ventures" posts
- Crunchbase/PitchBook searches (if available)
- arXiv papers on geology + AI (academic researchers becoming founders)

### 2. Entity Extraction

For each source mention:
1. Extract company name, website (if mentioned), description/context
2. Classify company type: mining_company / ai_startup / investor / supplier / related_player
3. Extract signals: funding round, hiring, partnership, acquisition, news mention
4. Source URL for traceability

### 3. Deduplication & Fuzzy Matching

For each extracted entity:
1. Fuzzy match against existing_companies list (Levenshtein distance, threshold 0.85)
2. If match found: classify as `existing_mention` with new signals
3. If no match: classify as `new_candidate`
4. For related companies (investors, partners), extract relationship type

### 4. Output Assembly

Return structured JSON ready for Google Sheets:

```json
{
  "run_date": "2026-05-27",
  "scan_sources_completed": [
    "mining.com",
    "mining-weekly.com",
    "discoveryalert.com.au"
  ],
  "discovery_results": {
    "new_competitors": [
      {
        "name": "EarthGrid AI",
        "website": "earthgrid.io",
        "description": "AI platform for mineral targeting in South Africa",
        "company_type": "ai_startup",
        "signals": [
          {
            "type": "product_launch",
            "date": "2026-05-15",
            "source_url": "mining-weekly.com/article/earthgrid-launch",
            "headline": "EarthGrid launches AI exploration platform"
          }
        ],
        "confidence": 0.92
      }
    ],
    "new_related_companies": [
      {
        "name": "Precision Capital",
        "website": "precisioncapital.vc",
        "relationship_type": "investor",
        "related_company": "Terra AI",
        "context": "Led $50M Series B round",
        "source_url": "..."
      }
    ],
    "existing_with_new_signals": [
      {
        "name": "Terra AI",
        "new_signals": [
          {
            "type": "hiring_surge",
            "detail": "Posted 12 job openings for geology ML engineers",
            "source_url": "linkedin.com/company/terra-ai/jobs"
          }
        ]
      }
    ]
  },
  "statistics": {
    "new_candidates_found": 7,
    "new_related_companies_found": 12,
    "existing_companies_with_signals": 3,
    "sources_scanned": 8,
    "total_mentions_processed": 47
  }
}
```

## Google Sheets Integration

After discovery, the skill pushes results to Google Sheets:

1. **New competitors** → Add rows to `companies` tab (status: `discovered`)
2. **New related companies** → Add rows to `companies` tab (status: `related`, marked with relationship type)
3. **Existing with signals** → Mark companies as `needs_deep_research` for Skill 2 to prioritize

## Error Handling

- If a source is unreachable, log the error and continue with other sources
- If web search API fails, skip that section but don't block the run
- Malformed entries are logged but don't halt execution
- Return partial results with error summary

## Output Files

Skill produces:
- Structured JSON (as above) for Google Sheets API ingestion
- CSV backup of new_competitors and new_related_companies
- Log file with sources scanned, errors encountered, and statistics

## Notes

- **Fuzzy matching** prevents re-discovery of known competitors with name variations
- **Related companies** expand the competitive landscape beyond direct competitors
- **Confidence scores** help prioritize which discoveries deserve deep research
- All sources and URLs are preserved for traceability (raw_signals)

