#!/usr/bin/env python3
"""
List the companies currently in the tracker so the agent knows what to research.

Reads the sheet and prints a JSON array, one object per company, with the current
value of every column plus a "missing_fields" list (columns that are still empty).
Use this to decide which companies / fields still need deep research.

Usage:
    python scripts/list_companies.py
    python scripts/list_companies.py --missing-only   # only rows with empty fields
    python scripts/list_companies.py --stale-only     # only rows not researched in 90+ days
"""

import json
import os
import sys
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from google_sheet_api import sheet_api

STALE_DAYS = 90


def _is_stale(last_researched_val: str) -> bool:
    """True if never researched or researched more than STALE_DAYS ago."""
    if not last_researched_val:
        return True
    try:
        # Sheet may return a full ISO datetime (e.g. "2026-05-31T04:00:00.000Z");
        # take only the date portion before any "T".
        date_part = last_researched_val.split("T")[0]
        last = date.fromisoformat(date_part)
        return (date.today() - last).days > STALE_DAYS
    except ValueError:
        return True


def main() -> int:
    missing_only = "--missing-only" in sys.argv
    stale_only = "--stale-only" in sys.argv

    rows = sheet_api.read_rows()
    if not rows:
        print("[]")
        return 1
    header = [str(c).strip() for c in rows[0]]
    if "Company Name" not in header:
        print("Sheet header missing 'Company Name'.")
        return 1
    name_idx = header.index("Company Name")

    out = []
    for r in rows[1:]:
        if len(r) <= name_idx or not str(r[name_idx]).strip():
            continue
        record, missing = {}, []
        for i, col in enumerate(header):
            val = str(r[i]).strip() if i < len(r) else ""
            record[col] = val
            if not val and col not in ("Company Name", "last_researched"):
                missing.append(col)
        record["missing_fields"] = missing
        record["stale"] = _is_stale(record.get("last_researched", ""))
        if missing_only and not missing:
            continue
        if stale_only and not record["stale"]:
            continue
        out.append(record)

    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
