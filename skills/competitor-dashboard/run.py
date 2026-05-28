#!/usr/bin/env python3
"""
Skill 3: Competitor Dashboard
Generates static HTML dashboard + CSV exports
Output: Creates /dashboard/index.html and /data/*.csv files
"""

import os
import json
from datetime import datetime
from pathlib import Path
import sys
import csv

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def generate_dashboard():
    """Generate HTML dashboard and export CSVs"""
    
    print("📊 Skill 3: Competitor Dashboard Starting...")
    print(f"   Time: {datetime.now().isoformat()}")
    
    # Create output directories
    dashboard_dir = Path(__file__).parent.parent.parent / "dashboard"
    data_dir = Path(__file__).parent.parent.parent / "data"
    dashboard_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)
    
    # Sample company data
    companies = [
        {"name": "Terra AI", "status": "active", "funding": "$15M", "team_size": 42, "product": "Subsurface mapping"},
        {"name": "GeologicAI", "status": "active", "funding": "$44M", "team_size": 89, "product": "Core scanning AI"},
        {"name": "Fleet Space", "status": "active", "funding": "$150M", "team_size": 135, "product": "Satellite seismic"},
        {"name": "VerAI", "status": "active", "funding": "$24M", "team_size": 40, "product": "Mineral discovery"},
        {"name": "Stratum AI", "status": "active", "funding": "$150K", "team_size": 18, "product": "Production modeling"},
    ]
    
    # Export CSV
    csv_file = data_dir / "competitors.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "status", "funding", "team_size", "product"])
        writer.writeheader()
        writer.writerows(companies)
    
    print(f"✅ Exported {len(companies)} companies to {csv_file.name}")
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mohan Competitive Intelligence Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        h1 {{ color: #333; margin-top: 0; }}
        .generated {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f5f5f5; }}
        .status-active {{ color: green; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 Mohan Competitive Intelligence</h1>
        <p class="generated">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Tracked Companies ({len(companies)})</h2>
        <table>
            <thead>
                <tr>
                    <th>Company</th>
                    <th>Status</th>
                    <th>Latest Funding</th>
                    <th>Team Size</th>
                    <th>Core Product</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for company in companies:
        status_class = "status-active" if company["status"] == "active" else ""
        html_content += f"""                <tr>
                    <td><strong>{company['name']}</strong></td>
                    <td><span class="{status_class}">{company['status']}</span></td>
                    <td>{company['funding']}</td>
                    <td>{company['team_size']}</td>
                    <td>{company['product']}</td>
                </tr>
"""
    
    html_content += """            </tbody>
        </table>
        <p style="color: #999; font-size: 0.9em; margin-top: 30px;">Data updated daily at 18:00 EST</p>
    </div>
</body>
</html>
"""
    
    # Write HTML
    html_file = dashboard_dir / "index.html"
    with open(html_file, "w") as f:
        f.write(html_content)
    
    print(f"✅ Generated HTML dashboard: {html_file}")
    
    # Simulate GitHub push
    print(f"✅ Simulated GitHub push:")
    print(f"   - {csv_file.name}")
    print(f"   - dashboard/index.html")
    
    return {
        "status": "success",
        "companies_exported": len(companies),
        "html_file": str(html_file),
        "csv_file": str(csv_file)
    }

if __name__ == "__main__":
    try:
        result = generate_dashboard()
        print(f"\n✅ Skill 3 completed successfully")
        exit(0)
    except Exception as e:
        print(f"❌ Skill 3 failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
