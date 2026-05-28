#!/usr/bin/env python3
"""
Skill 3: Competitor Dashboard
Reads from Google Sheets and generates HTML dashboard + CSV exports
Output: Creates dashboard/index.html and data/*.csv files
"""

import sys
import yaml
import csv
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build

# Get config
config_file = Path(__file__).parent.parent.parent / "config.yaml"
with open(config_file) as f:
    config = yaml.safe_load(f)

SHEET_ID = config['google_sheets']['sheet_id']

def get_sheets_service():
    """Get authenticated Sheets service"""
    try:
        from google.auth import default
        credentials, _ = default(scopes=['https://www.googleapis.com/auth/spreadsheets'])
        return build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        print(f"⚠️  ADC not available: {e}")
        return None

def read_companies(sheets_service):
    """Read companies from Google Sheets"""
    if not sheets_service:
        return []
    
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range='companies!A:O'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            print("❌ No company data found in Google Sheet")
            return []
        
        headers = values[0]
        companies = []
        
        for row in values[1:]:
            if not row or len(row) < 2:
                continue
            
            # Map to actual headers
            company = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    company[header] = row[i]
            
            companies.append(company)
        
        print(f"✅ Read {len(companies)} companies from Google Sheets")
        return companies
        
    except Exception as e:
        print(f"❌ Failed to read companies: {e}")
        return []

def read_events(sheets_service):
    """Read events from Google Sheets"""
    if not sheets_service:
        return []
    
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range='events!A:H'
        ).execute()
        
        values = result.get('values', [])
        if not values or len(values) < 2:
            return []
        
        headers = values[0]
        events = []
        
        for row in values[1:]:
            if not row or len(row) < 2:
                continue
            
            event = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    event[header] = row[i]
            
            events.append(event)
        
        print(f"✅ Read {len(events)} events from Google Sheets")
        return events
        
    except Exception as e:
        print(f"⚠️  Could not read events: {e}")
        return []

def export_csv(companies, events):
    """Export data to CSV files"""
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Export companies CSV
    if companies:
        try:
            csv_file = data_dir / "companies.csv"
            
            # Get all possible headers
            all_headers = set()
            for company in companies:
                all_headers.update(company.keys())
            headers = sorted(list(all_headers))
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(companies)
            
            print(f"✅ Exported {len(companies)} companies to {csv_file.name}")
        except Exception as e:
            print(f"❌ Failed to export companies CSV: {e}")
    
    # Export events CSV
    if events:
        try:
            csv_file = data_dir / "events.csv"
            
            all_headers = set()
            for event in events:
                all_headers.update(event.keys())
            headers = sorted(list(all_headers))
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(events)
            
            print(f"✅ Exported {len(events)} events to {csv_file.name}")
        except Exception as e:
            print(f"❌ Failed to export events CSV: {e}")

def generate_html(companies, events):
    """Generate HTML dashboard from actual data"""
    dashboard_dir = Path(__file__).parent.parent.parent / "dashboard"
    dashboard_dir.mkdir(exist_ok=True)
    
    # Build company table rows
    company_rows = ""
    for company in companies:
        name = company.get('Company Name', 'Unknown')
        website = company.get('Website', '#')
        status = company.get('Business Status', 'N/A')
        funding = company.get('Latest Round Amount USD', 'N/A')
        team_size = company.get('Team Size', 'N/A')
        product = company.get('Core Product', 'N/A')
        
        status_class = "status-active" if status == "active" else ""
        company_rows += f"""                <tr>
                    <td><strong><a href="{website}" target="_blank">{name}</a></strong></td>
                    <td><span class="{status_class}">{status}</span></td>
                    <td>${funding if funding != 'N/A' else 'TBD'}</td>
                    <td>{team_size}</td>
                    <td>{product}</td>
                </tr>
"""
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mohan Competitive Intelligence Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; border-radius: 12px; padding: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        h1 {{ color: #333; margin-top: 0; }}
        .timestamp {{ color: #999; font-size: 0.9em; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #667eea; color: white; padding: 12px; text-align: left; font-weight: 600; }}
        td {{ padding: 12px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f9f9f9; }}
        a {{ color: #667eea; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .status-active {{ color: #10b981; font-weight: bold; }}
        .status-stealth {{ color: #f59e0b; font-weight: bold; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-box {{ background: #f3f4f6; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 Mohan Competitive Intelligence Dashboard</h1>
        <p class="timestamp">📊 Data as of: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{len(companies)}</div>
                <div class="stat-label">Companies Tracked</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{len(events)}</div>
                <div class="stat-label">Events Logged</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{sum(1 for c in companies if c.get('Business Status') == 'active')}</div>
                <div class="stat-label">Active Companies</div>
            </div>
        </div>
        
        <h2>Tracked Companies</h2>
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
{company_rows}            </tbody>
        </table>
        
        <h2>Recent Events ({len(events)})</h2>
        <table>
            <thead>
                <tr>
                    <th>Company</th>
                    <th>Event Type</th>
                    <th>Date</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add event rows
    for event in events[:10]:  # Show last 10 events
        company = event.get('Company Name', 'Unknown')
        event_type = event.get('Event Type', 'N/A')
        date = event.get('Event Date', 'N/A')
        description = event.get('Description', '')
        
        html_content += f"""                <tr>
                    <td><strong>{company}</strong></td>
                    <td>{event_type}</td>
                    <td>{date}</td>
                    <td>{description[:60]}</td>
                </tr>
"""
    
    html_content += """            </tbody>
        </table>
        
        <p style="color: #999; font-size: 0.85em; margin-top: 40px; text-align: center;">
            Updated daily at 18:00 EST | 
            <a href="https://github.com/jajamoa/competitor-intel">GitHub</a> | 
            <a href="https://docs.google.com/spreadsheets/d/1TXnbzCrwkJCTLaNZZKFcKC9x23wqsqXTKU8Sv5sqHMU">Google Sheet</a>
        </p>
    </div>
</body>
</html>
"""
    
    # Write HTML
    try:
        html_file = dashboard_dir / "index.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
        print(f"✅ Generated HTML dashboard: {html_file}")
    except Exception as e:
        print(f"❌ Failed to generate HTML: {e}")

def main():
    print("📊 Skill 3: Competitor Dashboard")
    print(f"   Time: {datetime.now().isoformat()}")
    print(f"   Sheet ID: {SHEET_ID}")
    
    # Get sheets service
    sheets_service = get_sheets_service()
    
    # Read data from Google Sheets
    companies = read_companies(sheets_service)
    events = read_events(sheets_service)
    
    if not companies and not events:
        print("⚠️  No data to process")
        return 0
    
    # Export to CSV
    print("\n📥 Exporting to CSV...")
    export_csv(companies, events)
    
    # Generate HTML dashboard
    print("\n📄 Generating HTML dashboard...")
    generate_html(companies, events)
    
    print(f"\n✅ Skill 3 completed")
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"❌ Skill 3 failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
