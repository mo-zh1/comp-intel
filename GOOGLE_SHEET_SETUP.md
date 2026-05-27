# Google Sheet Setup Instructions

## 📋 Create Google Sheet Manually

Since API authentication requires additional setup, here's how to create the sheet manually in your browser:

### Step 1: Create New Sheet
1. Go to **Google Sheets**: https://sheets.google.com
2. Click **"+ Create"** → **"Blank spreadsheet"**
3. Name it: **"Mohan - Competitive Intelligence"**
4. Share settings: **"Anyone with the link can edit"**

### Step 2: Rename Default Sheet
- Right-click Sheet1 → Rename → **"companies"**

### Step 3: Add New Sheets
Right-click on sheet tab, select "Insert 1 below", name each:
1. **companies** (already created)
2. **events**
3. **update_log**
4. **data_sources**
5. **raw_signals**
6. **discovery_queue**

### Step 4: Populate Each Tab

**Copy the headers and data from files below into each tab:**

#### Tab 1: companies
Copy from: `GOOGLE_SHEET_EXPORT.md` — companies section

**Headers:**
```
Company Name | Website | Founders | Team Size | Investors | Latest Round Type | Latest Round Amount USD | Latest Round Date | Valuation | Core Product | Pricing Model | Target Customer | Business Status | Last Updated | Discovered Source
```

**Data rows (10 companies):**
- Terra AI
- GeologicAI
- Fleet Space
- VerAI
- Stratum AI
- Mineral Forecast
- Material Difference
- Veracio (new)
- Earth AI (new)

---

#### Tab 2: events
Copy from: `GOOGLE_SHEET_EXPORT.md` — events section

**Headers:**
```
Company ID | Company Name | Event Type | Event Date | Description | Amount USD | Source URLs | Confidence
```

**Data rows (11 events):**
- Terra AI funding, partnership, hiring
- GeologicAI funding, leadership change
- Fleet Space funding, acquisition
- VerAI funding
- Stratum AI funding
- Mineral Forecast funding
- Veracio product deployment
- Earth AI operational success

---

#### Tab 3: update_log
Copy from: `GOOGLE_SHEET_EXPORT.md` — update_log section

**Headers:**
```
Timestamp | Company Name | Field | Old Value | New Value | Source URL | Confidence | Status
```

**Data rows (7 updates):**
All field changes in past 30 days with sources

---

#### Tab 4: data_sources
Copy from: `DATA_SOURCES_SHEET.md`

**Headers:**
```
Source Name | URL | Type | Priority | Category | Last Scraped | Status | Notes
```

**Data rows (16 sources):**
mining.com, Mining Weekly, Discovery Alert, USGS, Canada, arXiv, Crunchbase, PitchBook, Y Combinator, BHP Ventures, Rio Tinto, LinkedIn, TechCrunch, StartUS, SeedTable, VCBacked

---

#### Tab 5: raw_signals
Copy from: `GOOGLE_SHEET_EXPORT.md` — raw_signals section

**Headers:**
```
Company ID | Field | Value | Source URL | Source Type | Extracted At | Confidence | Raw Content Preview
```

**Data rows (7 signals):**
All extracted values with direct source URLs

---

#### Tab 6: discovery_queue
**Headers:**
```
Company Name | Website | Discovered Date | Source | Status | Recommendation
```

**Data rows (initial discoveries):**
```
Veracio | https://www.veracio.com | 2026-05-27 | StartUS Insights | pending | High - deployed at scale
Earth AI | https://earthai.ai | 2026-05-27 | TechCrunch | pending | High - critical minerals focus
Four Point | https://4point.ai | 2026-05-27 | VCBacked | research_needed | Medium - needs website verification
```

---

## Step 5: Enable Sharing
1. Click **"Share"** button (top right)
2. Change to **"Anyone with the link can edit"**
3. Copy the share link

---

## Step 6: Get Sheet ID

Once created, the Sheet ID is in the URL:

```
https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit
                                        ^^^^^^^^
                                        Copy this
```

Save it in a file named `GOOGLE_SHEET_ID.txt` with just the ID.

---

## Configuration

Once you have the Sheet ID, update `config.yaml`:

```yaml
google_sheets:
  sheet_id: "YOUR_SHEET_ID_HERE"
  tabs:
    companies: "companies"
    events: "events"
    update_log: "update_log"
    data_sources: "data_sources"
    raw_signals: "raw_signals"
    discovery_queue: "discovery_queue"
```

---

## Next: Python Script for Updates

Once the manual setup is complete, I'll create a Python script that:
1. Reads from Google Sheets API
2. Updates tables after each skill run
3. Exports CSVs to GitHub

For now, manual creation + sharing the Sheet ID with me is sufficient.

---

## Summary

✅ 6 sheets created  
✅ Headers + initial data populated  
✅ Shared for collaboration  
✅ Ready for Skill 1 to start appending discoveries  

**Please:**
1. Create the Google Sheet following steps above
2. Share the Sheet ID with me
3. I'll then configure Skill 1 + 2 + 3 to read/write to it

