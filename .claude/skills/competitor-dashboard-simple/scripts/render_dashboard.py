#!/usr/bin/env python3
"""
Black-gold competitor intelligence dashboard.

Reads the live Google Sheet and writes:
  data/competitors.csv                             latest CSV snapshot
  data/archive/competitors_<EST-ts>.csv            timestamped CSV archive
  dashboard-simple/index.html                      latest HTML dashboard
  dashboard-simple/archive/dashboard_<EST-ts>.html timestamped HTML archive

Usage:
    python scripts/render_dashboard.py [--overrides /path/to/investor_overrides.json]

The optional --overrides file is a JSON map of company name → list of
{"name": "Khosla Ventures", "lead": true} objects produced by the agent
in Step 1 of the SKILL.md workflow. When supplied, it replaces the
regex-based parse_investors() for those companies.
"""

import argparse
import csv
import html
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from google_sheet_api import sheet_api

ROOT = Path(__file__).resolve().parents[4]

WARN = "⚠"
SKIP_INVESTOR = (
    "undisclosed", "sole owner", "无外部", "per tracxn", "cbinsights",
    "列共", "existing investor", "returning investor", "n/a", "不适用", "无外部 vc",
)


# ── helpers ───────────────────────────────────────────────────────────────────

def col(header, name):
    low = [h.strip().lower() for h in header]
    return low.index(name.lower()) if name.lower() in low else -1


def cell(row, i):
    return str(row[i]).strip() if 0 <= i < len(row) else ""


def esc(x):
    return html.escape(str(x))


def is_core(row, idx):
    for key in ("Business Model", "Technical", "stage"):
        if WARN in cell(row, idx.get(key, -1)):
            return False
    return True


def split_top_level(s, sep=","):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "(（[":   depth += 1; cur += ch
        elif ch in ")）]": depth = max(0, depth - 1); cur += ch
        elif ch == sep and depth == 0: out.append(cur); cur = ""
        else: cur += ch
    if cur.strip():
        out.append(cur)
    return out


def parse_investors(raw):
    if not raw:
        return []
    s = re.sub(r"[.,;。]?\s*(series\s+[a-e][^:]*:|returning\s*:|earlier\s*:|seed\s*:|pre-?seed\s*:)",
               ",", raw, flags=re.I)
    s = s.replace("。", ",").replace("；", ",").replace(";", ",")
    out, seen = [], set()
    for tok in split_top_level(s):
        lead = "lead" in tok.lower()
        name = re.sub(r"[(（].*?[)）]", "", tok)
        for piece in re.split(r"\s\+\s|\s&\s", name):
            n = piece.split("—")[0].split("–")[0].split(" - ")[0]
            n = re.sub(r"^\s*(funds advised by)\s+", "", n, flags=re.I)
            n = re.sub(r"\s+", " ", n).strip().strip("⚠️✅·.,;")
            if not n or not re.search(r"[A-Za-z]", n):
                continue
            low = n.lower()
            if any(k in low for k in SKIP_INVESTOR) or low.startswith("+") or low in seen:
                continue
            seen.add(low)
            out.append((n, lead))
    return out


def funding_stage(lr):
    m = re.search(r"(pre-?seed|seed|series\s+[a-e])", lr, re.I)
    if m:
        return m.group(1).title()
    if "acquired" in lr.lower() or "收购" in lr:
        return "Acquired"
    return "Other / Grant"


def has_valuation(v):
    if not v:
        return False
    low = v.lower()
    return (not low.startswith("undisclosed") and "未公开" not in v and not v.startswith(WARN)
            and bool(re.search(r"\$|usd|a\$|cad|€|\d", low)))


def derive_status(lr, investors, trajectory, valuation):
    if "acquired" in lr.lower() or "收购" in lr:
        return "acquired"
    if not any([lr.strip(), investors.strip(), trajectory.strip(), valuation.strip()]):
        return "stealth"
    return "active"


def parse_hq(founded):
    m = re.search(r'\(([^)]+)\)', founded)
    if not m:
        return ""
    return re.split(r';|originally|pivoted', m.group(1), flags=re.I)[0].strip()


def parse_year(founded):
    m = re.match(r'\s*(\d{4})', founded)
    return m.group(1) if m else ""


def parse_round_name(lr):
    m = re.search(r'(pre-?seed|seed|series\s+[a-e]|grant|acquired)', lr, re.I)
    return re.sub(r'\s+', ' ', m.group(1)).title() if m else ""


def parse_amount(lr):
    m = re.search(r'\$[\d,.]+\s*[MBKmk]?', lr)
    return m.group(0).strip() if m else ""


def parse_date(lr):
    m = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*[\s,]+(\d{4})', lr, re.I)
    if m:
        return f"{m.group(2)}-{m.group(1)[:3]}"
    m = re.search(r'(\d{4})[-/](0[1-9]|1[0-2])', lr)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.search(r'\b(20\d{2})\b', lr)
    return m.group(1) if m else ""


# ── data layer ────────────────────────────────────────────────────────────────

def build_data(header, rows, overrides=None):
    idx = {h.strip(): i for i, h in enumerate(header)}
    get = lambda r, k: cell(r, idx.get(k, -1))
    overrides = overrides or {}

    companies = []
    for r in rows:
        nm = get(r, "Company Name")
        if not nm:
            continue
        lr  = get(r, "Latest Round")
        inv = get(r, "Investors")
        trj = get(r, "Funding Trajectory")
        val = get(r, "Valuation")
        # Agent-provided clean investor list takes priority over regex parser
        if nm in overrides:
            investors = [(d["name"], d.get("lead", False)) for d in overrides[nm]]
        else:
            investors = parse_investors(inv)
        companies.append({
            "name":     nm,
            "website":  get(r, "Website"),
            "core":     is_core(r, idx),
            "investors":investors,
            "stage":    funding_stage(lr),
            "valuation":has_valuation(val),
            "status":   derive_status(lr, inv, trj, val),
            "hq":       parse_hq(get(r, "Founded Year")),
            "founded":  parse_year(get(r, "Founded Year")),
            "round":    parse_round_name(lr),
            "amount":   parse_amount(lr),
            "date":     parse_date(lr),
        })

    core = [c for c in companies if c["core"]]
    adj  = [c for c in companies if not c["core"]]

    # investor ↔ company graph (core only)
    inv_map = {}
    nodes, links = [], []
    for c in core:
        nodes.append({"id": f"C::{c['name']}", "label": c["name"], "type": "company", "deg": 0})
        for inv, lead in c["investors"]:
            k = inv.lower()
            inv_map.setdefault(k, {"label": inv, "cos": set()})["cos"].add(c["name"])
            links.append({"source": f"C::{c['name']}", "target": f"I::{k}", "lead": lead})
    for k, v in inv_map.items():
        nodes.append({"id": f"I::{k}", "label": v["label"], "type": "investor", "deg": len(v["cos"])})

    shared = sorted(
        ({"investor": v["label"], "cos": sorted(v["cos"])}
         for v in inv_map.values() if len(v["cos"]) >= 2),
        key=lambda x: (-len(x["cos"]), x["investor"].lower()),
    )

    order  = ["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Series D", "Acquired", "Other / Grant"]
    counts = {k: 0 for k in order}
    for c in core:
        counts[c["stage"]] = counts.get(c["stage"], 0) + 1
    stages = [(k, counts[k]) for k in order if counts.get(k)]

    return {
        "companies": companies, "core": core, "adj": adj,
        "graph": {"nodes": nodes, "links": links},
        "shared": shared, "stages": stages,
        "status_counts": {s: sum(1 for c in companies if c["status"] == s)
                          for s in ("active", "stealth", "acquired")},
    }


# ── render ────────────────────────────────────────────────────────────────────

SKIP_COLS = set()  # show all columns; source and last_researched are rendered with special handling
SOURCE_COLS = {"source：", "source："}  # columns that contain newline-separated URLs


def render_html(d, header, data_rows, d3_src="./d3.min.js"):
    updated = datetime.now(__import__('datetime').timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sc = d["status_counts"]
    n  = len(d["companies"])

    kpi_html = "".join(
        f'<div class="kpi"><div class="kpi-n">{v}</div><div class="kpi-l">{k}</div></div>'
        for k, v in [("TRACKED", n), ("ACTIVE", sc.get("active", 0)),
                     ("STEALTH", sc.get("stealth", 0)), ("ACQUIRED", sc.get("acquired", 0))]
    )

    rows_parts = []
    for c in d["companies"]:
        adj_tag = '' if c["core"] else '<span class="adj-tag">adj</span>'
        domain  = re.sub(r'https?://(www\.)?', '', c["website"]).rstrip('/') if c["website"] else ''
        site    = (f'<a class="site" href="{esc(c["website"])}" target="_blank">{esc(domain)}</a>'
                   if c["website"] else '')
        rows_parts.append(
            f'<tr data-status="{c["status"]}">'
            f'<td class="co-cell"><div class="co-name">{esc(c["name"])}{adj_tag}</div>{site}</td>'
            f'<td><span class="badge {c["status"]}">{c["status"]}</span></td>'
            f'<td class="dim-txt">{esc(c["hq"]) or "—"}</td>'
            f'<td class="dim-txt">{esc(c["founded"]) or "—"}</td>'
            f'<td><span class="round-lbl">{esc(c["round"]) or "—"}</span></td>'
            f'<td class="dim-txt">{esc(c["amount"]) or "—"}</td>'
            f'<td class="dim-txt">{esc(c["date"]) or "—"}</td>'
            f'</tr>'
        )
    rows_html = "\n".join(rows_parts)

    maxc = max((n for _, n in d["stages"]), default=1)
    stage_html = "".join(
        f'<div class="bar-row"><span class="bar-lab">{esc(k)}</span>'
        f'<span class="bar"><span class="fill" style="width:{int(v/maxc*100)}%"></span></span>'
        f'<span class="bar-n">{v}</span></div>'
        for k, v in d["stages"]
    )

    shared_html = (
        "".join(
            f'<li><span class="s-name">{esc(s["investor"])}</span>'
            f'<span class="cnt">×{len(s["cos"])}</span>'
            f'<span class="cos">{esc(" · ".join(s["cos"]))}</span></li>'
            for s in d["shared"]
        ) or "<li>No shared investors yet.</li>"
    )

    # ── full detail table ──────────────────────────────────────────────────
    show = [(i, h) for i, h in enumerate(header) if h.strip() not in SKIP_COLS]
    name_i = next((i for i, h in show if h.strip() == "Company Name"), -1)
    web_i  = next((i for i, h in show if h.strip() == "Website"), -1)

    dt_head = "".join(f"<th>{esc(h)}</th>" for _, h in show)
    dt_body_parts = []
    for r in data_rows:
        tds = []
        for i, h in show:
            val = cell(r, i)
            if i == name_i:
                tds.append(f'<td class="dt-name">{esc(val)}</td>')
            elif i == web_i and val:
                tds.append(f'<td><a class="site-lnk" href="{esc(val)}" target="_blank">site</a></td>')
            elif h.strip() in ("source：", "source") and val:
                links = "".join(
                    f'<a class="src-lnk" href="{esc(u.strip())}" target="_blank">[{j+1}]</a>'
                    for j, u in enumerate(val.split("\n")) if u.strip()
                )
                tds.append(f'<td class="src-cell">{links}</td>')
            else:
                tds.append(f'<td>{esc(val)}</td>')
        dt_body_parts.append(f"<tr>{''.join(tds)}</tr>")
    detail_html = "\n".join(dt_body_parts)

    return (TEMPLATE
            .replace("__D3_SRC__", d3_src)
            .replace("__UPDATED__", updated)
            .replace("__N_CORE__", str(len(d["core"])))
            .replace("__KPIS__", kpi_html)
            .replace("__ROWS__", rows_html)
            .replace("__STAGES__", stage_html)
            .replace("__SHARED__", shared_html)
            .replace("__GRAPH__", json.dumps(d["graph"]))
            .replace("__DT_HEAD__", dt_head)
            .replace("__DT_ROWS__", detail_html))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Competitor Intel</title>
<script src="__D3_SRC__"></script>
<style>
:root {
  --bg:#0f0f0f; --surface:#1a1a1a; --border:#2a2a2a;
  --gold:#C9A442; --gold-dim:#7a6028;
  --text:#e5e5e5; --muted:#6b6b6b;
  --green:#4ade80; --green-bg:#0d2b1a;
  --purple:#a78bfa; --purple-bg:#1e1030;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}

/* header */
header{display:flex;justify-content:space-between;align-items:center;
  padding:16px 40px;border-bottom:1px solid var(--border)}
.brand{color:var(--gold);font-size:17px;font-weight:600;letter-spacing:.4px}
.ts{color:var(--muted);font-size:12px}

/* main */
main{max-width:1200px;margin:0 auto;padding:48px 40px}
h1{font-size:44px;font-weight:700;line-height:1.1;margin-bottom:10px}
.subtitle{color:var(--muted);font-size:14px;margin-bottom:44px}
h2{font-size:11px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);font-weight:600;margin-bottom:16px}

/* kpi */
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);background:var(--border);
  gap:1px;border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:36px}
.kpi{background:var(--surface);padding:24px 28px}
.kpi-n{font-size:38px;font-weight:700;color:var(--gold);line-height:1}
.kpi-l{font-size:11px;letter-spacing:1.5px;color:var(--muted);margin-top:10px}

/* filter pills */
.filters{display:flex;align-items:center;gap:8px;margin-bottom:20px}
.f-label{font-size:11px;letter-spacing:1px;color:var(--muted);margin-right:4px}
.pill{background:transparent;border:1px solid var(--border);color:var(--muted);
  padding:5px 16px;border-radius:20px;font-size:13px;cursor:pointer;transition:.15s}
.pill:hover{border-color:var(--gold-dim);color:var(--text)}
.pill.active{border-color:var(--gold);color:var(--gold)}

/* table */
.tbl-wrap{border:1px solid var(--border);border-radius:12px;overflow:hidden;margin-bottom:52px}
table{width:100%;border-collapse:collapse;font-size:13px}
thead th{background:var(--surface);padding:13px 16px;text-align:left;
  font-size:10px;letter-spacing:1.2px;color:var(--muted);font-weight:600;white-space:nowrap}
tbody tr{border-top:1px solid var(--border);transition:.1s}
tbody tr:hover{background:#1f1f1f}
tbody tr.adj{opacity:.45}
td{padding:14px 16px;vertical-align:middle}
.co-cell .co-name{font-weight:600;display:flex;align-items:center;gap:6px}
.site{color:var(--muted);font-size:11px;text-decoration:none;display:block;margin-top:3px}
.site:hover{color:var(--gold)}
.dim-txt{color:var(--muted)}
.adj-tag{font-size:9px;color:#666;border:1px solid #333;border-radius:3px;padding:1px 5px;flex-shrink:0}
.round-lbl{color:var(--gold);font-size:12px}
.badge{display:inline-block;padding:3px 9px;border-radius:4px;font-size:11px;font-weight:500}
.badge.active  {background:var(--green-bg);color:var(--green)}
.badge.acquired{background:var(--purple-bg);color:var(--purple)}
.badge.stealth {background:#222;color:#888}

/* graph */
.graph-header{margin-bottom:12px}
#net-wrap{background:var(--surface);border:1px solid var(--border);border-radius:12px;
  overflow:hidden;margin-bottom:52px}
#net{width:100%;display:block;cursor:grab}
#net:active{cursor:grabbing}
.legend{padding:12px 20px;border-top:1px solid var(--border);
  display:flex;gap:20px;flex-wrap:wrap;font-size:11px;color:var(--muted)}
.legend span{display:flex;align-items:center;gap:5px}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0}
.n-link{stroke:#333;stroke-opacity:.5;stroke-width:1}
.n-link.lead{stroke:var(--gold);stroke-opacity:.8;stroke-width:1.5}
.n-lbl{font-size:10px;fill:var(--muted);pointer-events:none}
.n-lbl.company{fill:var(--text);font-size:11px;font-weight:600}
.n-lbl.shared{fill:#f43f5e}
.dimmed{opacity:.07}

/* analysis */
.analysis{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-bottom:32px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px}
.bar-row{display:flex;align-items:center;gap:10px;margin:8px 0;font-size:12px}
.bar-lab{width:90px;color:var(--muted);text-align:right;white-space:nowrap;flex-shrink:0}
.bar{flex:1;background:#111;border-radius:4px;height:11px;overflow:hidden}
.fill{display:block;height:100%;background:linear-gradient(90deg,var(--gold),var(--gold-dim));border-radius:4px}
.bar-n{width:22px;color:var(--text);font-weight:600}
ul.shared{list-style:none;max-height:420px;overflow:auto}
ul.shared li{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px;
  padding:10px 0;border-bottom:1px solid var(--border);font-size:13px}
ul.shared li:last-child{border-bottom:none}
.s-name{font-weight:600}
.cnt{color:var(--gold);font-weight:700;font-size:12px}
.cos{color:var(--muted);font-size:11.5px;width:100%;margin-top:2px}

/* detail table */
.detail-section{margin-top:52px}
.dt-filter{width:320px;max-width:100%;padding:8px 12px;border-radius:8px;
  border:1px solid var(--border);background:#111;color:var(--text);
  font-size:13px;margin-bottom:14px}
.dt-scroll{overflow-x:auto;border:1px solid var(--border);border-radius:12px}
#dt{width:100%;border-collapse:collapse;font-size:12px;min-width:1400px}
#dt thead th{background:var(--surface);padding:11px 14px;text-align:left;
  font-size:10px;letter-spacing:1.1px;color:var(--muted);font-weight:600;
  white-space:nowrap;position:sticky;top:0;z-index:1}
#dt tbody tr{border-top:1px solid var(--border)}
#dt tbody tr:hover{background:#1f1f1f}
#dt td{padding:12px 14px;vertical-align:top;max-width:300px;line-height:1.5;word-break:break-word}
#dt .dt-name{font-weight:700;white-space:nowrap;color:var(--text)}
.site-lnk{color:var(--gold);text-decoration:none;font-size:12px}
.site-lnk:hover{text-decoration:underline}
.src-cell{white-space:nowrap}
.src-lnk{color:var(--muted);text-decoration:none;margin-right:3px;font-size:11px}
.src-lnk:hover{color:var(--gold)}

@media(max-width:900px){
  header,main{padding-left:20px;padding-right:20px}
  .kpi-grid{grid-template-columns:repeat(2,1fr)}
  .analysis{grid-template-columns:1fr}
  h1{font-size:32px}
}
</style>
</head>
<body>

<header>
  <div class="brand">Competitor Intel</div>
  <div class="ts">Updated __UPDATED__</div>
</header>

<main>
  <h1>Tracked Companies</h1>
  <p class="subtitle">Mining &amp; subsurface AI startups under watch &mdash; __N_CORE__ core AI+mining companies.</p>

  <div class="kpi-grid">__KPIS__</div>

  <div class="filters">
    <span class="f-label">STATUS</span>
    <button class="pill active" data-f="all"      onclick="filter('all')">All</button>
    <button class="pill"        data-f="active"   onclick="filter('active')">Active</button>
    <button class="pill"        data-f="stealth"  onclick="filter('stealth')">Stealth</button>
    <button class="pill"        data-f="acquired" onclick="filter('acquired')">Acquired</button>
  </div>

  <div class="tbl-wrap">
    <table id="tbl">
      <thead><tr>
        <th>COMPANY</th><th>STATUS</th><th>HQ</th><th>FOUNDED</th>
        <th>ROUND</th><th>AMOUNT</th><th>DATE</th>
      </tr></thead>
      <tbody>__ROWS__</tbody>
    </table>
  </div>

  <div class="graph-header" style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
    <h2 style="margin:0">Investor &rarr; Company Network</h2>
    <div style="display:flex;gap:24px;align-items:center;font-size:12px;color:var(--muted)">
      <label style="display:flex;align-items:center;gap:8px">Charge
        <input type="range" id="sl-charge" min="-1500" max="-50" value="-500" style="width:100px;accent-color:var(--gold)">
        <span id="v-charge" style="min-width:36px">-500</span>
      </label>
      <label style="display:flex;align-items:center;gap:8px">Distance
        <input type="range" id="sl-dist" min="30" max="300" value="100" style="width:100px;accent-color:var(--gold)">
        <span id="v-dist" style="min-width:28px">100</span>
      </label>
    </div>
  </div>
  <div id="net-wrap">
    <svg id="net" height="520"></svg>
    <div class="legend">
      <span><i class="dot" style="background:#C9A442"></i>Company</span>
      <span><i class="dot" style="background:#6b6b6b"></i>Investor</span>
      <span><i class="dot" style="background:#f43f5e"></i>Shared investor (2+)</span>
      <span><i class="dot" style="background:#C9A442;opacity:.6"></i>Lead / strategic link</span>
    </div>
  </div>

  <div class="analysis">
    <div class="card">
      <h2>Funding Stage &mdash; Core Companies</h2>
      __STAGES__
    </div>
    <div class="card">
      <h2>Shared Backers &mdash; Vet Before Contact</h2>
      <ul class="shared">__SHARED__</ul>
    </div>
  </div>

  <div class="detail-section">
    <h2>All tracked companies</h2>
    <input class="dt-filter" id="dt-q" type="search" placeholder="Filter table…" oninput="dtFilt()">
    <div class="dt-scroll">
      <table id="dt">
        <thead><tr>__DT_HEAD__</tr></thead>
        <tbody>__DT_ROWS__</tbody>
      </table>
    </div>
  </div>
</main>

<script>
// ── filter ────────────────────────────────────────────────────────────────
function filter(s) {
  document.querySelectorAll('.pill').forEach(p =>
    p.classList.toggle('active', p.dataset.f === s));
  document.querySelectorAll('#tbl tbody tr').forEach(tr =>
    tr.style.display = (s === 'all' || tr.dataset.status === s) ? '' : 'none');
}

// ── D3 force graph ────────────────────────────────────────────────────────
const G = __GRAPH__;
const svg = d3.select('#net');
const W = document.getElementById('net-wrap').clientWidth || 960, H = 520;
svg.attr('width', W).attr('viewBox', `0 0 ${W} ${H}`);

const r = d => d.type === 'company' ? 9 : 4 + Math.min(d.deg || 1, 5) * 1.8;
const col = d => d.type === 'company' ? '#C9A442' : d.deg >= 2 ? '#f43f5e' : '#555';

// Adaptive link distance: high-degree nodes get more room to breathe
const linkDist = d => {
  const maxDeg = Math.max(d.source.deg || 0, d.target.deg || 0);
  return maxDeg > 8 ? 160 : maxDeg > 3 ? 110 : 70;
};

const sim = d3.forceSimulation(G.nodes)
  .force('link',   d3.forceLink(G.links).id(d => d.id).distance(linkDist))
  .force('charge', d3.forceManyBody().strength(-500))
  .force('center', d3.forceCenter(W / 2, H / 2))
  .force('x',      d3.forceX(W / 2).strength(0.04))
  .force('y',      d3.forceY(H / 2).strength(0.04))
  .force('collide',d3.forceCollide(d => r(d) + 6));

const linkSel = svg.append('g').selectAll('line').data(G.links).join('line')
  .attr('class', d => 'n-link' + (d.lead ? ' lead' : ''));

const nodeSel = svg.append('g').selectAll('circle').data(G.nodes).join('circle')
  .attr('r', r).attr('fill', col).attr('stroke', '#0f0f0f').attr('stroke-width', 1.5)
  .call(d3.drag()
    .on('start', (e,d) => { if(!e.active) sim.alphaTarget(.3).restart(); d.fx=d.x; d.fy=d.y; })
    .on('drag',  (e,d) => { d.fx=e.x; d.fy=e.y; })
    .on('end',   (e,d) => { if(!e.active) sim.alphaTarget(0); d.fx=null; d.fy=null; }))
  .on('mouseenter', (_,d) => hi(d.id))
  .on('mouseleave', () => clearHi());

const lblSel = svg.append('g').selectAll('text').data(G.nodes).join('text')
  .attr('class', d => 'n-lbl' + (d.type==='company' ? ' company' : d.deg>=2 ? ' shared' : ''))
  .text(d => d.label)
  .style('display', d => d.type==='investor' && d.deg<2 ? 'none' : null);

sim.on('tick', () => {
  G.nodes.forEach(d => {
    d.x = Math.max(20, Math.min(W - 20, d.x));
    d.y = Math.max(16, Math.min(H - 16, d.y));
  });
  linkSel.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
         .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
  nodeSel.attr('cx',d=>d.x).attr('cy',d=>d.y);
  lblSel.attr('x',d=>d.x+r(d)+3).attr('y',d=>d.y+4);
});

// adjacency for hover
const adj = new Map(G.nodes.map(n=>[n.id,new Set([n.id])]));
G.links.forEach(l=>{adj.get(l.source.id)?.add(l.target.id);adj.get(l.target.id)?.add(l.source.id);});

function hi(id) {
  const keep = adj.get(id)||new Set([id]);
  nodeSel.classed('dimmed', d=>!keep.has(d.id));
  lblSel.classed('dimmed', d=>!keep.has(d.id))
        .style('display', d=>d.type==='investor'&&d.deg<2 ? (keep.has(d.id)?null:'none') : null);
  linkSel.classed('dimmed', d=>d.source.id!==id&&d.target.id!==id);
}
function clearHi() {
  nodeSel.classed('dimmed',false);
  lblSel.classed('dimmed',false).style('display',d=>d.type==='investor'&&d.deg<2?'none':null);
  linkSel.classed('dimmed',false);
}

// sliders
const slC=document.getElementById('sl-charge'), vC=document.getElementById('v-charge');
const slD=document.getElementById('sl-dist'),   vD=document.getElementById('v-dist');
slC.oninput=()=>{vC.textContent=slC.value;sim.force('charge').strength(+slC.value);sim.alpha(.3).restart();};
slD.oninput=()=>{vD.textContent=slD.value;sim.force('link').distance(+slD.value);sim.alpha(.3).restart();};

// detail table filter
function dtFilt() {
  const q = document.getElementById('dt-q').value.toLowerCase();
  document.querySelectorAll('#dt tbody tr').forEach(tr =>
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none');
}
</script>
</body>
</html>
"""


# ── I/O ───────────────────────────────────────────────────────────────────────

def eastern_ts():
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("America/New_York"))
    except Exception:
        from datetime import timedelta, timezone
        now = datetime.now(timezone(timedelta(hours=-5), "EST"))
    return now.strftime("%Y-%m-%d_%H%M_%Z")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--overrides", default=None,
                        help="Path to investor_overrides.json produced by the agent")
    args = parser.parse_args()

    overrides = {}
    if args.overrides:
        p = Path(args.overrides)
        if p.exists():
            with open(p, encoding="utf-8") as f:
                overrides = json.load(f)
            print(f"Loaded investor overrides for {len(overrides)} companies")
        else:
            print(f"Warning: --overrides file not found: {args.overrides}")

    rows = sheet_api.read_rows()
    if not rows:
        print("Sheet empty or unreachable.")
        return 1

    header    = [str(c).strip() for c in rows[0]]
    data_rows = [r for r in rows[1:] if any(str(c).strip() for c in r)]

    data_dir = ROOT / "data"
    dash_dir = ROOT / "dashboard-simple"
    for p in (data_dir / "archive", dash_dir / "archive"):
        p.mkdir(parents=True, exist_ok=True)

    ts = eastern_ts()

    # CSV
    csv_rows = [header] + [[cell(r, i) for i in range(len(header))] for r in data_rows]
    for path in (data_dir / "competitors.csv", data_dir / "archive" / f"competitors_{ts}.csv"):
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(csv_rows)

    # HTML — index uses ./d3.min.js, archive uses ../d3.min.js
    d = build_data(header, data_rows, overrides)
    index_path   = dash_dir / "index.html"
    archive_path = dash_dir / "archive" / f"dashboard_{ts}.html"
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(render_html(d, header, data_rows, d3_src="./d3.min.js"))
    with open(archive_path, "w", encoding="utf-8") as f:
        f.write(render_html(d, header, data_rows, d3_src="../d3.min.js"))

    sc = d["status_counts"]
    print(f"Rendered {len(data_rows)} companies "
          f"({len(d['core'])} core / {len(d['adj'])} adjacent) | "
          f"active {sc.get('active',0)}, stealth {sc.get('stealth',0)}, acquired {sc.get('acquired',0)}")
    print(f"  -> {index_path.relative_to(ROOT)}")
    print(f"  -> {archive_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
