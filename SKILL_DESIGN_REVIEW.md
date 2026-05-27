# Skills Design Review — 6 Key Questions

## 📋 Overview

Three skills form the competitive intelligence pipeline:
1. **competitor-discovery** — Daily scanning for new competitors
2. **competitor-research** — Deep research + auto-merge field updates
3. **competitor-dashboard** — HTML dashboard + CSV exports

---

## ✅ Questions — Confirmed & Implemented

### 1️⃣ Data Sources — CONFIRMED ✅

**Original 7 sources:**
- mining.com
- mining-weekly.com
- discoveryalert.com.au
- USGS Periodicals
- Canada Natural Resources
- LinkedIn Mining AI search
- arXiv papers

**Added (as requested):**
- ✅ Crunchbase (mining, geology, AI, critical minerals)
- ✅ PitchBook (mining, minerals, exploration tech)
- ✅ Y Combinator database
- ✅ BHP Ventures (corporate venture)
- ✅ Rio Tinto Ventures (corporate venture)

**Total: 12+ sources across mining news, investor portfolios, and academic research**

---

### 2️⃣ Google Sheet Fields — CONFIRMED ✅

**companies tab (added `valuation`):**
```
id, canonical_name, website, linkedin_url, founded_year, hq_city, hq_country,
founders, team_size, investors, latest_round_type, latest_round_amount_usd, 
latest_round_date, valuation, business_model, technical_stage, core_product, 
pricing_model, target_customer, status, last_updated, confidence_score, discovered_source
```

**events tab:**
```
company_id, event_type, event_date, description, amount_usd, source_urls, confidence
```

**update_log tab:**
```
timestamp, company_name, field, old_value, new_value, source_url, confidence, status
```

**raw_signals tab:**
```
company_id, field, value, source_url, source_type, extracted_at, confidence, raw_content_preview
```

✅ **Valuation field added** to capital section

---

### 3️⃣ Event Types — CONFIRMED ✅

**Event types (8 total, keeping as-is):**
- funding_round
- acquisition
- leadership_change
- product_launch
- partnership
- hiring_surge
- expansion
- news_mention

✅ **No changes needed**

---

### 4️⃣ Merge Logic — CONFIRMED ✅ (Cross-Validation Strategy)

**New policy (NO confidence thresholds, NO human review):**
- **2+ trusted sources AGREE** → AUTO-MERGE immediately
- **Single trusted source** → Accept if authoritative
- **Unverifiable sources** → DISCARD, leave field EMPTY

**Trusted sources (absolutely verifiable):**
- Official company website
- LinkedIn company profile
- Official investor/VC announcements
- Press releases
- SEC filings

**CRITICAL: NO HALLUCINATION**
- Every value MUST have verifiable source
- Unknown fields → leave EMPTY, do not guess

**Example scenarios:**
- LinkedIn says 42 employees, website says 40 → 2 trusted sources → AUTO-MERGE (use average or website as primary)
- Official press release $15M Series B, Crunchbase $15M → 2 trusted sources, both agree → AUTO-MERGE
- Random blog post says "raising Series C" → DISCARD (no trusted source)
- No source for valuation → LEAVE EMPTY (do not estimate or infer)

✅ **No human review needed. Cross-validation-based merging only.**

---

### 5️⃣ GitHub Auto-Push — CONFIRMED ✅

**Enabled:**
- CSVs to `/data/`
- HTML to `/dashboard/`
- Old CSVs archived to `/data/archive/`
- Commit message: `[auto] daily update — YYYY-MM-DD`

✅ **Auto-push enabled. No manual review required.**

---

### 6️⃣ Daily Cron Schedule — CONFIRMED ✅

**Schedule (18:00 EST / UTC-5, or UTC-4 during EDT):**
```
18:00 EST → Skill 1: competitor-discovery (~15 min)
18:15 EST → Skill 2: competitor-research (~30-60 min, varies with # companies)
19:15 EST → Skill 3: competitor-dashboard (~5-10 min)
19:25 EST → Complete
```

**Run frequency:**
- Daily for all 3 skills
- Sequential execution (no parallelization)

✅ **18:00 EST (America/New_York timezone). Daily for all skills.**

---

## ✅ All Confirmed & Implemented

1. ✅ Data sources: 12+ sources (added Crunchbase, PitchBook, Y Combinator, BHP/Rio Tinto Ventures)
2. ✅ Google Sheet fields: Added `valuation` field
3. ✅ Event types: Keep current 8 types
4. ✅ Merge logic: Cross-validation (2+ trusted sources), NO human review, NO hallucination
5. ✅ GitHub auto-push: Enabled
6. ✅ Cron schedule: 18:00 EST daily

## 📝 Next Steps

1. ✅ Feedback from mo.zh incorporated
2. 🧪 Ready for Skill testing (Anthropic skill-creator)
3. 📊 Show test results to mo.zh
4. 🚀 Create Google Sheet + set up daily cron

---

## 📍 Files Structure

```
competitor-intel/
├── README.md (overview)
├── config.yaml (configuration)
├── SKILL_DESIGN_REVIEW.md (this file)
└── skills/
    ├── competitor-discovery/
    │   ├── SKILL.md
    │   └── evals.json
    ├── competitor-research/
    │   ├── SKILL.md
    │   └── evals.json
    └── competitor-dashboard/
        ├── SKILL.md
        └── evals.json
```

---

Reply with answers to all 6 questions, and I'll proceed with implementation.

