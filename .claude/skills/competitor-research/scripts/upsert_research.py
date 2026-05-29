#!/usr/bin/env python3
"""
Apply deep-research field updates to the tracker Google Sheet.

This is a thin, deterministic writer. The agent does the web research and decides
the field values; this script writes them cleanly. It invents nothing.

Usage:
    echo '[{"company": "Earth AI",
            "fields": {"Founders": "Roman Teslyuk",
                       "Latest Round": "Series B $24M",
                       "Valuation": ""}}]' \
        | python scripts/upsert_research.py

Input: a JSON list of {"company": <name>, "fields": {<column>: <value>}}.

Clean-update behaviour:
  - matches an existing row by "Company Name" (case-insensitive)
  - creates a new row if the company is not present yet
  - only writes fields whose column exists in the header
  - never overwrites a non-empty existing value with an empty one
  - skips writes where the value is unchanged
  - prints a JSON summary {updated, created, skipped_fields, failed}
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from google_sheet_api import sheet_api


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        print("No input. Pipe a JSON list of company updates via stdin.")
        return 1

    try:
        updates = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return 1

    if isinstance(updates, dict):
        updates = updates.get("updates", [updates])
    if not isinstance(updates, list):
        print("Input must be a JSON list of updates.")
        return 1

    header = sheet_api.header()
    if not header or "Company Name" not in header:
        print("Sheet header missing 'Company Name'. Set up the header row first.")
        return 1
    name_idx = header.index("Company Name")
    col_of = {h.strip().lower(): i for i, h in enumerate(header)}

    rows = sheet_api.read_rows()
    index = {}
    for i, r in enumerate(rows[1:], start=2):  # sheet rows are 1-indexed; data starts at row 2
        if len(r) > name_idx and str(r[name_idx]).strip():
            index[str(r[name_idx]).strip().lower()] = (i, r)

    summary = {"updated": [], "created": [], "skipped_fields": [], "failed": []}

    for upd in updates:
        if not isinstance(upd, dict):
            continue
        name = str(upd.get("company", "")).strip()
        fields = upd.get("fields", {}) or {}
        if not name:
            continue

        clean = {}
        for k, v in fields.items():
            ci = col_of.get(str(k).strip().lower())
            if ci is None:
                summary["skipped_fields"].append(f"{name}:{k} (no such column)")
                continue
            clean[ci] = "" if v is None else str(v).strip()

        key = name.lower()
        if key not in index:
            row = ["" for _ in header]
            row[name_idx] = name
            for ci, val in clean.items():
                row[ci] = val
            if sheet_api.append(row):
                summary["created"].append(name)
            else:
                summary["failed"].append(name)
            continue

        sheet_row, current = index[key]
        changed = []
        for ci, val in clean.items():
            old = str(current[ci]).strip() if len(current) > ci else ""
            if val == "" or val == old:
                continue  # never blank out an existing value; skip unchanged
            if sheet_api.update_cell(sheet_row, ci + 1, val):
                changed.append(header[ci])
            else:
                summary["failed"].append(f"{name}:{header[ci]}")
        if changed:
            summary["updated"].append({"company": name, "fields": changed})

    print(json.dumps(summary, ensure_ascii=False))
    return 0 if not summary["failed"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
