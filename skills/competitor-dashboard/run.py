#!/usr/bin/env python3
"""
Skill 3 tool — render a dashboard from the live Google Sheet.

Reads the current sheet (header + rows), then writes:
  data/competitors.csv      CSV snapshot of the sheet
  dashboard/index.html      self-contained searchable HTML table

Columns are taken from the sheet header at runtime — nothing is hardcoded.
"""

import csv
import html
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from google_sheet_api import sheet_api

ROOT = Path(__file__).resolve().parents[2]


def non_empty(row):
    return any(str(c).strip() for c in row)


def build_html(header, rows):
    updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    thead = "".join(f"<th>{html.escape(str(h))}</th>" for h in header)
    body_rows = []
    for r in rows:
        cells = []
        for i, _ in enumerate(header):
            val = str(r[i]).strip() if i < len(r) else ""
            cells.append(f"<td>{html.escape(val)}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")
    tbody = "\n".join(body_rows)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Competitive Landscape</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         margin: 0; padding: 24px; background: #0f172a; color: #e2e8f0; }}
  h1 {{ margin: 0 0 4px; font-size: 20px; }}
  .meta {{ color: #94a3b8; font-size: 13px; margin-bottom: 16px; }}
  input {{ width: 100%; max-width: 420px; padding: 10px 12px; border-radius: 8px;
          border: 1px solid #334155; background: #1e293b; color: #e2e8f0; margin-bottom: 16px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; background: #1e293b;
          border-radius: 10px; overflow: hidden; }}
  th {{ background: #334155; text-align: left; padding: 10px; position: sticky; top: 0; }}
  td {{ padding: 10px; border-top: 1px solid #334155; vertical-align: top; }}
  tr:hover td {{ background: #243449; }}
</style>
</head>
<body>
  <h1>Competitive Landscape</h1>
  <div class="meta">{len(rows)} companies · updated {updated}</div>
  <input id="q" type="search" placeholder="Filter companies…" oninput="filt()">
  <table>
    <thead><tr>{thead}</tr></thead>
    <tbody id="tb">
{tbody}
    </tbody>
  </table>
<script>
function filt() {{
  const q = document.getElementById('q').value.toLowerCase();
  for (const tr of document.querySelectorAll('#tb tr')) {{
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
  }}
}}
</script>
</body>
</html>
"""


def main() -> int:
    rows = sheet_api.read_rows()
    if not rows:
        print("Sheet is empty or unreachable.")
        return 1

    header = [str(c).strip() for c in rows[0]]
    data = [r for r in rows[1:] if non_empty(r)]

    data_dir = ROOT / "data"
    dash_dir = ROOT / "dashboard"
    data_dir.mkdir(exist_ok=True)
    dash_dir.mkdir(exist_ok=True)

    csv_path = data_dir / "competitors.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for r in data:
            writer.writerow([str(r[i]).strip() if i < len(r) else "" for i in range(len(header))])

    html_path = dash_dir / "index.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(header, data))

    print(f"Rendered {len(data)} companies -> {csv_path.relative_to(ROOT)}, {html_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
