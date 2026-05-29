#!/usr/bin/env python3
"""
Skill 1 tool — append newly-discovered competitors to the Google Sheet.

The agent (Claude) performs the web search and decides which companies are new.
This script is a thin, deterministic writer: it takes that result as JSON on
stdin and appends genuinely-new rows. It invents nothing.

Usage:
    echo '[{"Company Name": "Earth AI", "Website": "https://earthai.ai"}]' \
        | python run.py

Input: a JSON list of objects (or {"companies": [...]}). Object keys should match
the sheet header (e.g. "Company Name", "Website"). Aliases accepted:
name -> Company Name, company -> Company Name, url -> Website.

Behaviour:
  - reads the current header and rows from the sheet
  - skips companies already present (case-insensitive "Company Name" match)
  - appends the rest as rows aligned to the current header; unknown fields blank
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from google_sheet_api import sheet_api

ALIASES = {
    "name": "Company Name",
    "company": "Company Name",
    "company name": "Company Name",
    "website": "Website",
    "url": "Website",
}


def normalize(obj: dict) -> dict:
    out = {}
    for key, value in obj.items():
        out[ALIASES.get(str(key).strip().lower(), str(key).strip())] = value
    return out


def main() -> int:
    raw = sys.stdin.read().strip()
    if not raw:
        print("No input. Pipe a JSON list of companies via stdin.")
        return 1

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return 1

    items = payload.get("companies", []) if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        print("Input must be a JSON list of company objects.")
        return 1

    header = sheet_api.header()
    if not header or "Company Name" not in header:
        print("Sheet header missing 'Company Name'. Set up the header row first.")
        return 1
    name_idx = header.index("Company Name")

    rows = sheet_api.read_rows()
    existing = {
        str(r[name_idx]).strip().lower()
        for r in rows[1:]
        if len(r) > name_idx and str(r[name_idx]).strip()
    }

    appended, skipped, failed = [], [], []
    for obj in items:
        if not isinstance(obj, dict):
            continue
        obj = normalize(obj)
        name = str(obj.get("Company Name", "")).strip()
        if not name:
            continue
        if name.lower() in existing:
            skipped.append(name)
            continue
        row = [str(obj.get(col, "")).strip() for col in header]
        if sheet_api.append(row):
            appended.append(name)
            existing.add(name.lower())
        else:
            failed.append(name)

    print(json.dumps(
        {"appended": appended, "skipped_existing": skipped, "failed": failed},
        ensure_ascii=False,
    ))
    return 0 if not failed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
