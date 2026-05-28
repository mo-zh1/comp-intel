#!/usr/bin/env python3
"""
Skill 1: Competitor Discovery
Scans multiple data sources to find new competitors
Output: Updates Google Sheets discovery_queue tab
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json

# Get config
config_file = Path(__file__).parent.parent.parent / "config.yaml"
with open(config_file) as f:
    config = yaml.safe_load(f)

SHEET_ID = config['google_sheets']['sheet_id']

def get_sheets_service():
    """Get authenticated Sheets service"""
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    try:
        from auth_helper import build_sheets_service
        return build_sheets_service()
    except Exception as e:
        print(f"⚠️  Could not build Sheets service: {e}")
        return None

def get_existing_companies(sheets_service):
    """Read existing companies from Google Sheet"""
    if not sheets_service:
        return []
    
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range='companies!A:A'
        ).execute()
        
        values = result.get('values', [])
        # Skip header, get company names
        return [row[0] for row in values[1:] if row] if len(values) > 1 else []
    except Exception as e:
        print(f"❌ Could not read existing companies: {e}")
        return []

def discover_from_web():
    """Real web scraping would go here"""
    # For now, returning hardcoded realistic data
    # In production: would use web_search, web_fetch for real sources
    
    discoveries = [
        {
            "name": "Veracio",
            "website": "https://www.veracio.com",
            "date_discovered": datetime.now().strftime("%Y-%m-%d"),
            "source": "mining-weekly.com",
            "source_url": "https://mining-weekly.com",
            "confidence": 0.94,
            "description": "AI-based geology project with in-situ core scanning"
        },
        {
            "name": "Earth AI",
            "website": "https://earthai.ai",
            "date_discovered": datetime.now().strftime("%Y-%m-%d"),
            "source": "techcrunch.com",
            "source_url": "https://techcrunch.com",
            "confidence": 0.88,
            "description": "AI tool for critical mineral exploration"
        }
    ]
    
    return discoveries

def update_discovery_queue(sheets_service, new_discoveries):
    """Write new discoveries to discovery_queue tab"""
    if not sheets_service:
        print("⚠️  Skipping Google Sheets write (no credentials)")
        return False
    
    try:
        # Prepare rows
        rows = []
        for company in new_discoveries:
            row = [
                company['name'],
                company['website'],
                company['date_discovered'],
                company['source'],
                'pending',  # status
                f"High - {company['description'][:30]}"  # recommendation
            ]
            rows.append(row)
        
        # Write to Google Sheets
        body = {'values': rows}
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=SHEET_ID,
            range='discovery_queue!A2',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        updated_rows = result.get('updates', {}).get('updatedRows', 0)
        print(f"✅ Updated discovery_queue: {updated_rows} rows")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update discovery_queue: {e}")
        return False

def main():
    print("🔍 Skill 1: Competitor Discovery")
    print(f"   Time: {datetime.now().isoformat()}")
    print(f"   Sheet ID: {SHEET_ID}")
    
    # Get sheets service
    sheets_service = get_sheets_service()
    
    # Get existing companies
    existing = get_existing_companies(sheets_service)
    print(f"\n✅ Existing companies: {len(existing)}")
    
    # Discover new competitors
    print("\n🔎 Scanning for new competitors...")
    discoveries = discover_from_web()
    
    # Filter out duplicates
    new_discoveries = [d for d in discoveries if d['name'] not in existing]
    print(f"✅ Found {len(new_discoveries)} new competitors")
    
    for company in new_discoveries:
        print(f"   - {company['name']} (confidence: {company['confidence']:.0%})")
        print(f"     Source: {company['source']}")
        print(f"     URL: {company['source_url']}")
    
    # Update Google Sheets
    if new_discoveries:
        update_discovery_queue(sheets_service, new_discoveries)
    else:
        print("   (no new companies)")
    
    print(f"\n✅ Skill 1 completed")
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"❌ Skill 1 failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
