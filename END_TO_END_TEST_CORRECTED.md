# End-to-End Pipeline Test — CORRECTED DATES

## Important Fix

Found and corrected date errors in the initial test. Here are the **CORRECT** funding dates from your original Google Sheet:

| Company | Event | Old Date (Wrong) | Correct Date | Note |
|---------|-------|------------------|--------------|------|
| GeologicAI | Series B | 2026-07-17 | **2025-07-17** | From your sheet: "Jul 17, 2025" |
| VerAI | Series B | 2026-02-26 | **2025-02-26** | From your sheet: "Feb 26, 2025" |
| Fleet Space | Series D | 2026-05-12 | **2024-12-11** | From your sheet: "Dec 11-12, 2024" |

---

## Corrected Events List

| Date | Company | Type | Title | Amount |
|------|---------|------|-------|--------|
| **2025-07-17** | GeologicAI | funding_round | Series B $44M from Blue Earth Capital | $44M |
| 2026-05-22 | Terra AI | hiring_surge | 8 new positions posted for ML/geology engineers | — |
| 2025-06-03 | Fleet Space | acquisition | Acquires HiSeis (seismic sensors) | — |
| 2026-05-20 | Terra AI | funding_round | Series A $15M from Breakthrough Energy | $15M |
| 2026-05-18 | Terra AI | partnership | Partnership with Rio Tinto announced | — |
| 2026-05-15 | EarthGrid AI | product_launch | Product launch - public beta | — |
| **2024-12-11** | Fleet Space | funding_round | Series D $150M from Teachers Venture Growth | $150M |
| **2025-02-26** | VerAI | funding_round | Series B $24M first closing from Insight Partners | $24M |
| 2023-09-12 | Mineral Forecast | funding_round | Seed round $3.31M from Techstars | $3.31M |
| 2020-08-26 | Stratum AI | funding_round | Seed round $150K from Y Combinator | $150K |

---

## Files Updated with Correct Dates

✅ **GOOGLE_SHEET_EXPORT.md** — Updated 3 rows
✅ **dashboard/index.html** — Updated event dates + company data
✅ **END_TO_END_TEST_CORRECTED.md** — This file

---

## Source of Truth

All dates now match your original Google Sheet exactly:
- https://docs.google.com/spreadsheets/d/1qcip_vIHGET_OG5y5h0R8XEdMYOuK3ezYhT8vOOn5x8

---

## Next Steps for Production

1. ✅ All date errors corrected
2. ✅ Google Sheet export verified against source data
3. ⏳ Ready to create new Google Sheet in your account
4. ⏳ Deploy daily cron at 18:00 EST

