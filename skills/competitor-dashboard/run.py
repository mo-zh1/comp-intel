#!/usr/bin/env python3
"""Skill 3: Competitor Dashboard"""

import sys
import os
import csv
from pathlib import Path
from datetime import datetime

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

from google_sheet_api import sheet_api

def main():
    print("📊 Skill 3: Competitor Dashboard")
    print(f"   Time: {datetime.now().isoformat()}")
    
    if not sheet_api.test_connection():
        print("❌ Cannot connect")
        return 1
    
    print("✅ Connected to Google Sheet")
    
    # Sample company data
    companies = [
        ["Terra AI", "https://www.terraai.com", "John Merrill", "42", "active"],
        ["GeologicAI", "https://www.geologicai.com", "Grant Sanden", "89", "active"],
        ["Fleet Space", "https://www.fleetspace.com", "Flavia Tata", "135", "active"],
        ["VerAI", "https://ver-ai.com", "Yair Frastai", "40", "active"],
        ["Stratum AI", "https://stratum.gs", "Farzi Yusufali", "18", "active"],
    ]
    
    # Export CSV
    print("\n📤 Exporting to CSV...")
    data_dir = Path(parent_dir) / "data"
    data_dir.mkdir(exist_ok=True)
    
    csv_file = data_dir / "companies.csv"
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Company Name", "Website", "Founders", "Team Size", "Status"])
        writer.writerows(companies)
    
    print(f"✅ Exported {len(companies)} to {csv_file.name}")
    
    # Generate HTML
    print("\n📄 Generating HTML...")
    dashboard_dir = Path(parent_dir) / "dashboard"
    dashboard_dir.mkdir(exist_ok=True)
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Mohan Competitive Intelligence</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; }}
        h1 {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f9f9f9; }}
        a {{ color: #667eea; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 Mohan Competitive Intelligence</h1>
        <p>Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <table>
            <tr>
                <th>Company</th>
                <th>Website</th>
                <th>Founders</th>
                <th>Team</th>
                <th>Status</th>
            </tr>
"""
    
    for company in companies:
        html_content += f"""            <tr>
                <td><b><a href="{company[1]}" target="_blank">{company[0]}</a></b></td>
                <td><a href="{company[1]}" target="_blank">Link</a></td>
                <td>{company[2]}</td>
                <td>{company[3]}</td>
                <td><span style="color: green; font-weight: bold;">{company[4]}</span></td>
            </tr>
"""
    
    html_content += """        </table>
    </div>
</body>
</html>
"""
    
    html_file = dashboard_dir / "index.html"
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Generated {html_file}")
    
    print(f"\n✅ Skill 3 done")
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
