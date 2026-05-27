# Skills Design Review — 6 Key Questions

## 📋 Overview

Three skills form the competitive intelligence pipeline:
1. **competitor-discovery** — Daily scanning for new competitors
2. **competitor-research** — Deep research + auto-merge field updates
3. **competitor-dashboard** — HTML dashboard + CSV exports

---

## 🤔 Questions Requiring Your Confirmation

### 1️⃣ Data Sources — Complete?

**Current sources (7 total):**
- mining.com
- mining-weekly.com
- discoveryalert.com.au
- USGS Periodicals (copper, mineral production data)
- Canada Natural Resources
- LinkedIn Mining AI search
- arXiv papers (geology + AI)

**Questions:**
- Are these 7 sources sufficient for initial run?
- Should we add: Crunchbase, PitchBook, Y Combinator database, specific VC firm websites (BHP Ventures, Rio Tinto Ventures)?
- Any sources to remove or de-prioritize?

**Reference:** See `config.yaml` for full source list.

---

### 2️⃣ Google Sheet Fields — Complete?

**Assumed field structure:**

**companies tab:**
```
id, canonical_name, website, linkedin_url, founded_year, hq_city, hq_country,
founders, team_size, investors, latest_round_type, latest_round_amount_usd, 
latest_round_date, business_model, technical_stage, core_product, pricing_model, 
target_customer, status, last_updated, confidence_score, discovered_source
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

**Questions:**
- Are these fields sufficient?
- Should we add: valuation, headcount, customer_count, revenue_signals, etc.?
- Any fields to rename or restructure?

---

### 3️⃣ Event Types — Sufficient?

**Current event types (8 total):**
- funding_round
- acquisition
- leadership_change
- product_launch
- partnership
- hiring_surge
- expansion
- news_mention

**Questions:**
- Are these 8 types enough?
- Should we add: patent_filing, regulatory_approval, customer_win, customer_loss, rebrand?
- Any to remove?

---

### 4️⃣ Merge Logic Thresholds — Appropriate?

**Current thresholds (Skill 2 — competitor-research):**
- **>= 0.95 confidence** → Auto-merge (no human review)
- **0.85-0.95 confidence** → Decision logic (prefer recent, prefer authoritative source)
- **< 0.85 confidence** → Discard

**Example merge scenarios:**
- LinkedIn says 42 employees, website says 40 → 0.92 confidence → Use decision logic (website is authoritative, check timestamp) → Result: use website if recent, else LinkedIn
- Press release says Series B $15M, news says Series B $14.8M → 0.98 confidence → Auto-merge → Result: $15M (press release is primary)
- Tweet says founder hired → 0.60 confidence → Discard (too low signal)

**Questions:**
- Are the thresholds 0.95/0.85 reasonable, or should they be higher/lower?
- Is the decision logic (source authority + timestamp) appropriate?
- Do you want human review for any confidence range?

---

### 5️⃣ GitHub Auto-Push — Enable?

**Current design (Skill 3):**
- After dashboard generation, automatically push to GitHub
- CSVs to `/data/`
- HTML to `/dashboard/`
- Old CSVs archived to `/data/archive/`
- Commit message: `[auto] daily update — YYYY-MM-DD`

**Questions:**
- Enable auto-push, or require manual review before commit?
- Commit message format OK?
- Any other files to track (logs, metrics)?

---

### 6️⃣ Daily Cron Schedule — Feasible?

**Current plan (18:00 UTC):**
```
18:00 → Skill 1: competitor-discovery (~15 min)
18:15 → Skill 2: competitor-research (~30-60 min, varies with # companies)
19:15 → Skill 3: competitor-dashboard (~5-10 min)
19:25 → Complete
```

**Questions:**
- Is 18:00 UTC a good time, or prefer different timezone/time?
- Expected company list size for daily research: 12, 25, 50+?
- OK if research phase sometimes takes 60+ min for large lists?
- Should we implement staggered scheduling (e.g., discovery daily, research every 2 days)?

---

## 📝 Next Steps (After Your Answers)

1. ✅ You answer these 6 questions
2. 🔄 I adjust SKILL.md files and config.yaml based on feedback
3. 🧪 Run Skill 1 test (source scanning)
4. 📊 Show results, gather feedback
5. ✅ Proceed to Skill 2 and 3 testing
6. 🚀 Create Google Sheet + set up cron

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

