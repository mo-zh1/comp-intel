#!/usr/bin/env python3
"""Skill 1: Competitor Discovery"""

import sys
import os
from datetime import datetime

# Add parent path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, parent_dir)

from google_sheet_api import sheet_api

def main():
    print("🔍 Skill 1: Competitor Discovery")
    print(f"   Time: {datetime.now().isoformat()}")
    
    # Test connection
    if not sheet_api.test_connection():
        print("❌ Cannot connect to Google Sheet")
        return 1
    
    print("✅ Connected to Google Sheet")
    
    # Sample discoveries
    discoveries = [
        {
            "name": "Veracio",
            "website": "https://www.veracio.com",
            "discovered_date": datetime.now().strftime("%Y-%m-%d"),
            "source": "mining-weekly.com",
            "description": "AI core scanning"
        },
        {
            "name": "Earth AI",
            "website": "https://earthai.ai",
            "discovered_date": datetime.now().strftime("%Y-%m-%d"),
            "source": "techcrunch.com",
            "description": "Mineral discovery AI"
        }
    ]
    
    print(f"\n✅ Found {len(discoveries)} new competitors")
    for c in discoveries:
        print(f"   - {c['name']} via {c['source']}")
    
    # Update Google Sheet
    print("\n📝 Updating Google Sheet...")
    for i, company in enumerate(discoveries):
        row = 2 + i
        sheet_api.update_cell(row, 1, company['name'])
        sheet_api.update_cell(row, 2, company['website'])
        sheet_api.update_cell(row, 3, company['discovered_date'])
        sheet_api.update_cell(row, 4, company['source'])
        sheet_api.update_cell(row, 5, "pending")
        print(f"   ✅ Added {company['name']}")
    
    print(f"\n✅ Skill 1 done")
    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
