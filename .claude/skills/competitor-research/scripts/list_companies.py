#!/usr/bin/env python3
"""
List the companies currently in the tracker so the agent knows what to research.

Reads the sheet and prints a JSON array, one object per company, with the current
value of every column plus a "missing_fields" list (columns that are still empty).
Use this to decide which companies / fields still need deep research.

Usage:
    python scripts/list_companies.py
    python scripts/list_companies.py --missing-only   # only rows with empty fields
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from google_sheet_api import sheet_api


def main() -> int:
    missing_only = "--missing-only" in sys.argv

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
            if not val and col != "Company Name":
                missing.append(col)
        record["missing_fields"] = missing
        if missing_only and not missing:
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
