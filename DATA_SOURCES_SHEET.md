# Data Sources Management Sheet

This should be a separate Google Sheet tab named `data_sources` to manage all discovery sources dynamically.

## Structure

| Source Name | URL | Type | Priority | Category | Last Scraped | Status | Notes |
|---|---|---|---|---|---|---|---|
| mining.com | https://mining.com | news | 1 | mining_industry | 2026-05-27 | active | Daily mining news, funding announcements |
| Mining Weekly | https://miningweekly.com | news | 1 | mining_industry | 2026-05-27 | active | Weekly mining industry updates |
| Discovery Alert | https://discoveryalert.com.au | news | 1 | mining_industry | 2026-05-27 | active | Exploration discoveries (Australia-focused) |
| USGS Periodicals | https://pubs.usgs.gov/periodicals/ | regulatory | 2 | mineral_production | 2026-05-27 | active | US mineral production data |
| Canada Natural Resources | https://natural-resources.canada.ca | regulatory | 2 | mining_data | 2026-05-27 | active | Canadian mining statistics |
| arXiv (geo-ph + cs.LG) | https://arxiv.org | academic | 3 | academic | 2026-05-27 | active | Academic papers on geology + AI |
| Crunchbase | https://crunchbase.com | investor_portfolio | 1 | startup_funding | 2026-05-27 | active | Startup funding database, mining tech filter |
| PitchBook | https://pitchbook.com | investor_portfolio | 1 | startup_funding | 2026-05-27 | active | VC funding data, mining/minerals filter |
| Y Combinator | https://www.ycombinator.com | accelerator | 2 | startup_funding | 2026-05-27 | active | YC-backed startups (mining, earth tech) |
| BHP Ventures | https://bhpventures.com | corporate_vc | 1 | investor_portfolio | 2026-05-27 | active | BHP corporate venture portfolio |
| Rio Tinto Ventures | https://riotinto.com | corporate_vc | 1 | investor_portfolio | 2026-05-27 | active | Rio Tinto innovation/VC investments |
| LinkedIn Mining Ventures | https://linkedin.com | social | 2 | investor_portfolio | 2026-05-27 | active | Search: "mining ventures", "mineral tech" |
| TechCrunch | https://techcrunch.com | news | 2 | startup_news | 2026-05-27 | active | Tech/startup news, mining AI focus |
| StartUS Insights | https://www.startus-insights.com | analyst | 2 | market_analysis | 2026-05-27 | active | Startup trend reports (updated quarterly) |
| SeedTable | https://www.seedtable.com | database | 1 | startup_funding | 2026-05-27 | active | Startup database with mining filter |
| VCBacked | https://www.vcbacked.co | database | 2 | startup_funding | 2026-05-27 | active | Recently funded mining tech companies |

---

## How to Use This Sheet

1. **Priority Levels:**
   - 1 = Primary sources (check daily)
   - 2 = Secondary sources (check weekly)
   - 3 = Tertiary sources (check monthly or as needed)

2. **Types:**
   - `news` — Breaking news, announcements
   - `regulatory` — Government/official data
   - `academic` — Research papers, institutional
   - `investor_portfolio` — VC, investor websites
   - `accelerator` — Accelerator programs
   - `corporate_vc` — Corporate venture arms
   - `social` — LinkedIn, Twitter, social media
   - `database` — Crunchbase, PitchBook, aggregators
   - `analyst` — Market analysis, trend reports

3. **Status:**
   - `active` — Currently being monitored
   - `deprecated` — No longer useful
   - `on_hold` — Temporarily paused
   - `new` — Newly added

4. **Last Scraped:**
   - Update after each Skill 1 run
   - Track success/failure
   - Identify sources with access issues

---

## Recent Discoveries (from real test)

### Added Sources

| Source | Type | Found | Example Result |
|--------|------|-------|-----------------|
| TechCrunch | news | Yes | Earth AI critical minerals discovery |
| StartUS Insights | analyst | Yes | Veracio mentioned in "10 Mining Startups to Watch" |
| SeedTable | database | Yes | 69 mining startups, $5.8B funding |
| VCBacked | database | Yes | Four Point / TerraEye satellite AI |
| Crunchbase | investor_portfolio | Yes | Q1 2026 funding records |

---

## Management Notes

- **Last Updated:** 2026-05-27
- **Total Active Sources:** 16
- **Coverage:** Mining news, mining tech startups, critical minerals AI, regulatory data, investor portfolios
- **Update Cadence:** Daily priority sources, weekly secondary sources
- **Monitoring Tool:** Skill 1 (competitor-discovery) runs daily at 18:00 EST

---

## Future Additions

Potential sources to add:

- **Energy Fuels Inc** (vanadium/rare earth company blog)
- **Rare Element Resources** (public company investor relations)
- **ITC Rare Earths** (private rare earth explorer)
- **Mining.com podcast** (weekly interviews)
- **IE Faculty** (Imperial College mining research)
- **Colorado School of Mines** (mining tech research)
- **CRU Group** (commodities research)

