#!/usr/bin/env python3
"""
Render the competitor tracker into a CSV snapshot + a CEO-facing HTML dashboard.

Reads the live Google Sheet (header + rows) and writes, at the project root:
  data/competitors.csv                          latest CSV snapshot of the sheet
  data/archive/competitors_<EST-ts>.csv         timestamped CSV snapshot (kept)
  dashboard/index.html                          latest self-contained dashboard
  dashboard/archive/dashboard_<EST-ts>.html     timestamped dashboard (kept)

Each run overwrites the two "latest" files and additionally drops an
Eastern-time-stamped copy into the archive/ folders. Old archives are never
deleted, giving a local version history without touching .gitignore.

The dashboard shows: KPI summary, funding-stage distribution, a core AI+mining
vs adjacent split, an investor <-> company relationship network (the key view:
who shares backers with whom), and a searchable / sortable full table.

Columns are taken from the sheet header at runtime — nothing about the schema is
hardcoded. A company is treated as "adjacent" (not core AI+mining) when its
Business Model / Technical / stage cells carry a warning marker.

Usage:
    python scripts/render_dashboard.py
"""

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

# scripts -> competitor-dashboard -> skills -> .claude -> project root
ROOT = Path(__file__).resolve().parents[4]

WARN = "\u26a0"  # adjacency marker placed in cells during research
SKIP_INVESTOR = (
    "undisclosed", "sole owner", "无外部", "per tracxn", "cbinsights",
    "列共", "existing investor", "returning investor", "other ", "n/a",
    "不适用", "无外部 vc",
)


def col(header, name):
    low = [h.strip().lower() for h in header]
    return low.index(name.lower()) if name.lower() in low else -1


def cell(row, i):
    return str(row[i]).strip() if 0 <= i < len(row) else ""


def is_core(row, idx):
    """Adjacent (non-core) if a warning marker sits in business/technical/stage."""
    for key in ("Business Model", "Technical", "stage"):
        if WARN in cell(row, idx.get(key, -1)):
            return False
    return True


def split_top_level(s, seps=","):
    """Split on separator chars that are not inside () or （）."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "(（[":
            depth += 1
            cur += ch
        elif ch in ")）]":
            depth = max(0, depth - 1)
            cur += ch
        elif ch in seps and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


def parse_investors(raw):
    """Turn a free-text Investors cell into a clean list of (name, is_lead)."""
    if not raw:
        return []
    s = raw
    # normalise round labels + exotic separators into commas before splitting
    s = re.sub(r"[.,;。]?\s*(series\s+[a-e][^:]*:|returning\s*:|earlier\s*:|"
               r"seed\s*:|pre-?seed\s*:)", ",", s, flags=re.I)
    s = s.replace("。", ",").replace("；", ",").replace(";", ",")

    out, seen = [], set()
    for tok in split_top_level(s, ","):
        lead = "lead" in tok.lower()
        name = re.sub(r"[(（].*?[)）]", "", tok)        # drop parenthetical notes
        for piece in re.split(r"\s\+\s|\s&\s", name):    # "A + B" -> two investors
            n = piece.split("—")[0].split("–")[0].split(" - ")[0]  # drop "— note"
            n = re.sub(r"^\s*(funds advised by)\s+", "", n, flags=re.I)
            n = n.strip().strip("⚠️✅·.,;")
            n = re.sub(r"\s+", " ", n).strip()
            if not n or not re.search(r"[A-Za-z]", n):
                continue
            low = n.lower()
            if any(k in low for k in SKIP_INVESTOR) or low.startswith("+"):
                continue
            key = low
            if key in seen:
                continue
            seen.add(key)
            out.append((n, lead))
    return out


def funding_stage(latest):
    m = re.search(r"(pre-?seed|seed|series\s+[a-e])", latest, re.I)
    if m:
        return m.group(1).title().replace("Pre-Seed", "Pre-Seed")
    if "不适用" in latest or "acquired" in latest.lower() or "收购" in latest:
        return "Acquired"
    return "Other / Grant"


def has_valuation(v):
    if not v:
        return False
    low = v.lower()
    if low.startswith("undisclosed") or v.startswith("未公开") or v.startswith(WARN):
        return False
    return bool(re.search(r"\$|usd|a\$|cad|€|\d", low)) and "未公开" not in v


def build_dashboard(header, rows):
    idx = {h.strip(): i for i, h in enumerate(header)}
    name_i = col(header, "Company Name")
    web_i = col(header, "Website")
    inv_i = col(header, "Investors")
    lr_i = col(header, "Latest Round")
    val_i = col(header, "Valuation")
    src_i = col(header, "source：")
    if src_i < 0:
        src_i = col(header, "source")

    companies = []
    for r in rows:
        nm = cell(r, name_i)
        if not nm:
            continue
        companies.append({
            "name": nm,
            "core": is_core(r, idx),
            "row": r,
            "investors": parse_investors(cell(r, inv_i)) if inv_i >= 0 else [],
            "stage": funding_stage(cell(r, lr_i)) if lr_i >= 0 else "Other / Grant",
            "valuation": has_valuation(cell(r, val_i)) if val_i >= 0 else False,
        })

    core = [c for c in companies if c["core"]]
    adjacent = [c for c in companies if not c["core"]]

    # ---- relationship graph (core companies <-> investors) ----
    inv_to_cos = {}      # canonical-lower -> {"label":..., "cos":set()}
    nodes, links = [], []
    for c in core:
        nodes.append({"id": "C::" + c["name"], "label": c["name"], "type": "company"})
        for inv, lead in c["investors"]:
            k = inv.lower()
            inv_to_cos.setdefault(k, {"label": inv, "cos": set()})["cos"].add(c["name"])
            links.append({"s": "C::" + c["name"], "t": "I::" + k, "lead": lead})
    for k, v in inv_to_cos.items():
        nodes.append({"id": "I::" + k, "label": v["label"], "type": "investor",
                      "deg": len(v["cos"])})

    shared = sorted(
        ({"investor": v["label"], "cos": sorted(v["cos"])}
         for v in inv_to_cos.values() if len(v["cos"]) >= 2),
        key=lambda x: (-len(x["cos"]), x["investor"].lower()),
    )

    # ---- KPIs ----
    kpis = [
        ("Companies tracked", len(companies)),
        ("Core AI + mining", len(core)),
        ("Adjacent (geothermal / drilling / processing)", len(adjacent)),
        ("Distinct investors (core)", len(inv_to_cos)),
        ("Shared investors (back 2+ competitors)", len(shared)),
        ("Core with disclosed valuation", sum(1 for c in core if c["valuation"])),
    ]

    # ---- funding-stage distribution (core only) ----
    order = ["Pre-Seed", "Seed", "Series A", "Series B", "Series C",
             "Series D", "Acquired", "Other / Grant"]
    counts = {k: 0 for k in order}
    for c in core:
        counts[c["stage"]] = counts.get(c["stage"], 0) + 1
    stages = [(k, counts[k]) for k in order if counts.get(k)]

    return {
        "idx": idx, "name_i": name_i, "web_i": web_i, "src_i": src_i,
        "companies": companies, "core": core, "adjacent": adjacent,
        "graph": {"nodes": nodes, "links": links},
        "shared": shared, "kpis": kpis, "stages": stages,
    }


def esc(x):
    return html.escape(str(x))


def render_html(header, rows, d):
    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    name_i, web_i, src_i = d["name_i"], d["web_i"], d["src_i"]

    kpi_html = "".join(
        f'<div class="kpi"><div class="kpi-n">{esc(v)}</div>'
        f'<div class="kpi-l">{esc(k)}</div></div>' for k, v in d["kpis"]
    )

    maxc = max((n for _, n in d["stages"]), default=1)
    stage_html = "".join(
        f'<div class="bar-row"><span class="bar-lab">{esc(k)}</span>'
        f'<span class="bar"><span class="bar-fill" style="width:{int(n / maxc * 100)}%"></span></span>'
        f'<span class="bar-n">{n}</span></div>' for k, n in d["stages"]
    )

    if d["shared"]:
        shared_html = "".join(
            f'<li><b>{esc(s["investor"])}</b> <span class="cnt">×{len(s["cos"])}</span>'
            f'<br><span class="cos">{esc(" · ".join(s["cos"]))}</span></li>'
            for s in d["shared"]
        )
    else:
        shared_html = "<li>No investor backs two or more core competitors yet.</li>"

    # full table
    thead = "".join(f"<th onclick=\"sortBy({i})\">{esc(h)}</th>"
                    for i, h in enumerate(header))
    body = []
    for c in d["companies"]:
        r = c["row"]
        tds = []
        for i, h in enumerate(header):
            val = cell(r, i)
            if i == name_i:
                badge = "" if c["core"] else f' <span class="tag">{WARN} adjacent</span>'
                tds.append(f"<td class='nm'>{esc(val)}{badge}</td>")
            elif i == web_i and val:
                tds.append(f"<td><a href='{esc(val)}' target='_blank'>site</a></td>")
            elif i == src_i and val:
                links = "".join(
                    f"<a href='{esc(u.strip())}' target='_blank'>[{j+1}]</a> "
                    for j, u in enumerate(val.split("\n")) if u.strip()
                )
                tds.append(f"<td class='src'>{links}</td>")
            else:
                tds.append(f"<td>{esc(val)}</td>")
        cls = "" if c["core"] else "adj"
        body.append(f"<tr class='{cls}'>{''.join(tds)}</tr>")
    rows_html = "\n".join(body)

    graph_json = json.dumps(d["graph"])

    return (TEMPLATE
            .replace("__UPDATED__", updated)
            .replace("__NCO__", str(len(d["core"])))
            .replace("__KPIS__", kpi_html)
            .replace("__STAGES__", stage_html)
            .replace("__SHARED__", shared_html)
            .replace("__THEAD__", thead)
            .replace("__ROWS__", rows_html)
            .replace("__GRAPH__", graph_json))


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Competitive Landscape — AI + Mining</title>
<style>
  :root{ --bg:#0b1220; --card:#121b2e; --line:#22304b; --ink:#e8eef9; --mut:#93a3bf;
         --co:#38bdf8; --inv:#f59e0b; --invs:#f43f5e; --acc:#34d399; }
  *{box-sizing:border-box}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
       margin:0;background:var(--bg);color:var(--ink);padding:28px;}
  h1{margin:0 0 2px;font-size:22px;letter-spacing:.2px}
  .sub{color:var(--mut);font-size:13px;margin-bottom:22px}
  h2{font-size:15px;margin:0 0 12px;color:var(--ink)}
  .grid{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:24px}
  .kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
  .kpi-n{font-size:26px;font-weight:700}
  .kpi-l{color:var(--mut);font-size:11.5px;margin-top:4px;line-height:1.3}
  .cards{display:grid;grid-template-columns:2fr 1fr;gap:16px;margin-bottom:24px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}
  .net{height:560px;position:relative;overflow:hidden}
  svg{width:100%;height:100%;display:block;cursor:grab}
  .legend{position:absolute;right:14px;top:14px;font-size:11.5px;color:var(--mut);
          background:rgba(10,16,28,.7);border:1px solid var(--line);border-radius:8px;padding:8px 10px}
  .legend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:middle}
  .node-label{font-size:10px;fill:var(--mut);pointer-events:none}
  .node-label.co{fill:var(--ink);font-size:11px;font-weight:600}
  .node-label.shared{fill:#fecaca;font-weight:600}
  .link{stroke:#33425f;stroke-opacity:.55}
  .link.lead{stroke:var(--acc);stroke-opacity:.9}
  .dim{opacity:.08}
  ul.shared{list-style:none;margin:0;padding:0;max-height:500px;overflow:auto}
  ul.shared li{padding:9px 0;border-bottom:1px solid var(--line);font-size:13px}
  .cnt{color:var(--invs);font-weight:700;font-size:12px}
  .cos{color:var(--mut);font-size:11.5px}
  .bar-row{display:flex;align-items:center;gap:10px;margin:7px 0;font-size:12.5px}
  .bar-lab{width:92px;color:var(--mut);text-align:right}
  .bar{flex:1;background:#1c2740;border-radius:6px;height:14px;overflow:hidden}
  .bar-fill{display:block;height:100%;background:linear-gradient(90deg,var(--co),#6366f1)}
  .bar-n{width:22px;color:var(--ink);font-weight:600}
  .full{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px}
  input{width:320px;max-width:100%;padding:9px 12px;border-radius:8px;border:1px solid var(--line);
        background:#0e1830;color:var(--ink);margin-bottom:14px}
  table{width:100%;border-collapse:collapse;font-size:12px}
  th{position:sticky;top:0;background:#1a2540;text-align:left;padding:9px;cursor:pointer;white-space:nowrap}
  th:hover{background:#22304f}
  td{padding:9px;border-top:1px solid var(--line);vertical-align:top;max-width:340px}
  td.nm{font-weight:600;white-space:nowrap}
  tr.adj{opacity:.78}
  .tag{font-size:10px;color:#fca5a5;border:1px solid #7f1d1d;border-radius:5px;padding:1px 5px;font-weight:500}
  a{color:var(--co);text-decoration:none}
  a:hover{text-decoration:underline}
  .src a{color:var(--mut);margin-right:2px}
  .two{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px}
  @media(max-width:1100px){.grid{grid-template-columns:repeat(3,1fr)}.cards,.two{grid-template-columns:1fr}}
</style>
</head>
<body>
  <h1>Competitive Landscape — AI + Mining</h1>
  <div class="sub">Updated __UPDATED__ · live from the tracker · relationship view covers the __NCO__ core AI+mining companies</div>

  <div class="grid">__KPIS__</div>

  <div class="cards">
    <div class="card net">
      <h2>Investor ↔ Company network — who shares backers</h2>
      <div class="legend">
        <div><i style="background:#38bdf8"></i>Company</div>
        <div><i style="background:#f43f5e"></i>Shared investor (2+)</div>
        <div><i style="background:#f59e0b"></i>Investor</div>
        <div><i style="background:#34d399"></i>lead / strategic</div>
      </div>
      <svg id="net" viewBox="0 0 900 560" preserveAspectRatio="xMidYMid meet"></svg>
    </div>
    <div class="card">
      <h2>⚠ Shared backers — vet before contact</h2>
      <ul class="shared">__SHARED__</ul>
    </div>
  </div>

  <div class="two">
    <div class="card">
      <h2>Funding stage (core companies)</h2>
      __STAGES__
    </div>
    <div class="card">
      <h2>How to read the network</h2>
      <p style="color:var(--mut);font-size:13px;line-height:1.6">
      Blue nodes are competitors; orange nodes are their investors/partners. A
      <b style="color:#f43f5e">red</b> investor backs <b>two or more</b> competitors — these are
      the relationships to vet carefully before you approach an investor or partner,
      since they are already entangled with companies in this space. Hover any node to
      isolate its connections; drag to rearrange.</p>
    </div>
  </div>

  <div class="full">
    <h2>All tracked companies</h2>
    <input id="q" type="search" placeholder="Filter table…" oninput="filt()">
    <div style="overflow:auto;max-height:640px">
      <table id="tbl"><thead><tr>__THEAD__</tr></thead><tbody>__ROWS__</tbody></table>
    </div>
  </div>

<script>
const G = __GRAPH__;
const W=900,H=560,cx=W/2,cy=H/2;
const svg=document.getElementById('net');
const NS='http://www.w3.org/2000/svg';
const id2n={}; G.nodes.forEach(n=>{id2n[n.id]=n; n.x=cx+(Math.random()-.5)*W*.7; n.y=cy+(Math.random()-.5)*H*.7;});
// adjacency for hover
const adj={}; G.nodes.forEach(n=>adj[n.id]=new Set([n.id]));
G.links.forEach(l=>{adj[l.s].add(l.t); adj[l.t].add(l.s);});
// force layout
const REP=2600,LEN=84,SPRING=.045,GRAV=.022,STEP=34;
let alpha=1;
for(let it=0;it<600;it++){
  alpha*=.992;
  const dx={},dy={}; G.nodes.forEach(n=>{dx[n.id]=0;dy[n.id]=0;});
  for(let i=0;i<G.nodes.length;i++)for(let j=i+1;j<G.nodes.length;j++){
    const a=G.nodes[i],b=G.nodes[j]; let ax=a.x-b.x,ay=a.y-b.y; let d2=ax*ax+ay*ay||.01;
    const f=REP/d2,d=Math.sqrt(d2); ax=ax/d*f; ay=ay/d*f;
    dx[a.id]+=ax;dy[a.id]+=ay;dx[b.id]-=ax;dy[b.id]-=ay;
  }
  G.links.forEach(l=>{const a=id2n[l.s],b=id2n[l.t];let ax=b.x-a.x,ay=b.y-a.y;
    const d=Math.sqrt(ax*ax+ay*ay)||.01,f=(d-LEN)*SPRING; ax=ax/d*f;ay=ay/d*f;
    dx[a.id]+=ax;dy[a.id]+=ay;dx[b.id]-=ax;dy[b.id]-=ay;});
  G.nodes.forEach(n=>{dx[n.id]+=(cx-n.x)*GRAV;dy[n.id]+=(cy-n.y)*GRAV;});
  G.nodes.forEach(n=>{const len=Math.sqrt(dx[n.id]**2+dy[n.id]**2)||.01;
    const s=Math.min(len,STEP)*alpha; n.x+=dx[n.id]/len*s; n.y+=dy[n.id]/len*s;
    n.x=Math.max(30,Math.min(W-30,n.x)); n.y=Math.max(24,Math.min(H-24,n.y));});
}
// draw
const lel={};
G.links.forEach(l=>{const e=document.createElementNS(NS,'line');
  e.setAttribute('class','link'+(l.lead?' lead':'')); e._s=l.s; e._t=l.t; svg.appendChild(e); });
const cir={},lab={};
function nodeColor(n){return n.type==='company'?'#38bdf8':(n.deg>=2?'#f43f5e':'#f59e0b');}
function nodeR(n){return n.type==='company'?9:(4+Math.min(n.deg,5)*2.2);}
G.nodes.forEach(n=>{
  const c=document.createElementNS(NS,'circle'); c.setAttribute('r',nodeR(n));
  c.setAttribute('fill',nodeColor(n)); c.setAttribute('stroke','#0b1220'); c.setAttribute('stroke-width','1.5');
  c.style.cursor='pointer'; svg.appendChild(c); cir[n.id]=c;
  const t=document.createElementNS(NS,'text');
  t.setAttribute('class','node-label '+(n.type==='company'?'co':(n.deg>=2?'shared':'')));
  t.textContent=n.label;
  // hide singleton-investor labels until hover to reduce clutter
  if(n.type==='investor'&&n.deg<2) t.style.display='none';
  svg.appendChild(t); lab[n.id]=t;
  c.addEventListener('mouseenter',()=>focus(n.id));
  c.addEventListener('mouseleave',clearFocus);
  c.addEventListener('mousedown',e=>startDrag(e,n));
});
function place(){
  Object.values(lel).forEach(()=>{});
  svg.querySelectorAll('line').forEach(e=>{const a=id2n[e._s],b=id2n[e._t];
    e.setAttribute('x1',a.x);e.setAttribute('y1',a.y);e.setAttribute('x2',b.x);e.setAttribute('y2',b.y);});
  G.nodes.forEach(n=>{cir[n.id].setAttribute('cx',n.x);cir[n.id].setAttribute('cy',n.y);
    lab[n.id].setAttribute('x',n.x+nodeR(n)+3);lab[n.id].setAttribute('y',n.y+3);});
}
place();
function focus(id){const keep=adj[id];
  G.nodes.forEach(n=>{const on=keep.has(n.id);cir[n.id].classList.toggle('dim',!on);
    lab[n.id].classList.toggle('dim',!on);
    if(n.type==='investor'&&n.deg<2)lab[n.id].style.display=on?'block':'none';});
  svg.querySelectorAll('line').forEach(e=>{const on=e._s===id||e._t===id;
    e.classList.toggle('dim',!on);});}
function clearFocus(){G.nodes.forEach(n=>{cir[n.id].classList.remove('dim');lab[n.id].classList.remove('dim');
    if(n.type==='investor'&&n.deg<2)lab[n.id].style.display='none';});
  svg.querySelectorAll('line').forEach(e=>e.classList.remove('dim'));}
// drag
let drag=null;
function pt(e){const r=svg.getBoundingClientRect();return{x:(e.clientX-r.left)/r.width*W,y:(e.clientY-r.top)/r.height*H};}
function startDrag(e,n){drag=n;svg.style.cursor='grabbing';e.preventDefault();}
window.addEventListener('mousemove',e=>{if(!drag)return;const p=pt(e);drag.x=p.x;drag.y=p.y;place();});
window.addEventListener('mouseup',()=>{drag=null;svg.style.cursor='grab';});

// table search + sort
function filt(){const q=document.getElementById('q').value.toLowerCase();
  document.querySelectorAll('#tbl tbody tr').forEach(tr=>{
    tr.style.display=tr.textContent.toLowerCase().includes(q)?'':'none';});}
let sortAsc={};
function sortBy(i){const tb=document.querySelector('#tbl tbody');
  const rows=[...tb.rows];const asc=sortAsc[i]=!sortAsc[i];
  rows.sort((a,b)=>{const x=a.cells[i].innerText.trim(),y=b.cells[i].innerText.trim();
    const nx=parseFloat(x.replace(/[^0-9.]/g,'')),ny=parseFloat(y.replace(/[^0-9.]/g,''));
    const both=!isNaN(nx)&&!isNaN(ny)&&x.match(/\d/)&&y.match(/\d/);
    const r=both?nx-ny:x.localeCompare(y);return asc?r:-r;});
  rows.forEach(r=>tb.appendChild(r));}
</script>
</body>
</html>
"""


def eastern_timestamp() -> str:
    """Return an Eastern-time stamp like 2026-05-30_1313_EDT for archive filenames.

    Uses the America/New_York zone so the wall-clock time is correct year-round
    (the %Z suffix is EST in winter, EDT during daylight saving). Falls back to a
    fixed UTC-5 'EST' offset if the tz database is unavailable.
    """
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("America/New_York"))
    except Exception:
        from datetime import timedelta, timezone
        now = datetime.now(timezone(timedelta(hours=-5), "EST"))
    return now.strftime("%Y-%m-%d_%H%M_%Z")


def main() -> int:
    rows = sheet_api.read_rows()
    if not rows:
        print("Sheet is empty or unreachable.")
        return 1

    header = [str(c).strip() for c in rows[0]]
    data_rows = [r for r in rows[1:] if any(str(c).strip() for c in r)]

    data_dir = ROOT / "data"
    dash_dir = ROOT / "dashboard"
    data_archive = data_dir / "archive"
    dash_archive = dash_dir / "archive"
    for p in (data_dir, dash_dir, data_archive, dash_archive):
        p.mkdir(exist_ok=True)

    ts = eastern_timestamp()

    csv_text_rows = [header] + [[cell(r, i) for i in range(len(header))] for r in data_rows]
    csv_path = data_dir / "competitors.csv"
    csv_archive_path = data_archive / f"competitors_{ts}.csv"
    for path in (csv_path, csv_archive_path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            for row in csv_text_rows:
                w.writerow(row)

    d = build_dashboard(header, data_rows)
    html_text = render_html(header, data_rows, d)
    html_path = dash_dir / "index.html"
    html_archive_path = dash_archive / f"dashboard_{ts}.html"
    for path in (html_path, html_archive_path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_text)

    print(f"Rendered {len(data_rows)} companies "
          f"({len(d['core'])} core / {len(d['adjacent'])} adjacent), "
          f"{len(d['graph']['nodes'])} graph nodes, {len(d['shared'])} shared investors")
    print(f"  -> {csv_path.relative_to(ROOT)}")
    print(f"  -> {csv_archive_path.relative_to(ROOT)}")
    print(f"  -> {html_path.relative_to(ROOT)}")
    print(f"  -> {html_archive_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
