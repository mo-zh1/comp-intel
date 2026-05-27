#!/usr/bin/env python3
"""
Create Google Sheet using gcloud's cached credentials
"""

import os
import json
from pathlib import Path

def create_sheet_with_gcloud_creds():
    """Create sheet using gcloud's cached credentials"""
    
    try:
        from googleapiclient.discovery import build
        from google.auth import load_credentials_from_info
        from google.oauth2 import service_account
        import subprocess
    except ImportError as e:
        print(f"❌ Missing module: {e}")
        return None
    
    # Try to get access token from gcloud
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        access_token = result.stdout.strip()
        print(f"✅ Got access token from gcloud")
    except Exception as e:
        print(f"❌ Could not get token from gcloud: {e}")
        print("Try: gcloud auth login")
        return None
    
    # Use the token to build API clients
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    
    credentials = Credentials(token=access_token)
    
    # Build services
    sheets_service = build('sheets', 'v4', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # Create spreadsheet
    spreadsheet_body = {
        'properties': {
            'title': 'Mohan - Competitive Intelligence',
            'locale': 'en_US',
            'timeZone': 'America/New_York',
            'autoRecalc': 'ON_CHANGE'
        },
        'sheets': [
            {'properties': {'title': 'companies', 'sheetId': 0}},
            {'properties': {'title': 'events', 'sheetId': 1}},
            {'properties': {'title': 'update_log', 'sheetId': 2}},
            {'properties': {'title': 'data_sources', 'sheetId': 3}},
            {'properties': {'title': 'raw_signals', 'sheetId': 4}},
            {'properties': {'title': 'discovery_queue', 'sheetId': 5}},
        ]
    }
    
    print("Creating spreadsheet...")
    response = sheets_service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
    sheet_id = response['spreadsheetId']
    print(f"✅ Spreadsheet created: {sheet_id}")
    
    # Set permissions to "anyone with link"
    try:
        drive_service.permissions().create(
            fileId=sheet_id,
            body={'type': 'anyone', 'role': 'writer'},
            fields='id'
        ).execute()
        print("✅ Sharing enabled: Anyone with link can edit")
    except Exception as e:
        print(f"⚠️ Could not set sharing: {e}")
    
    return sheet_id, sheets_service

def populate_sheet(sheets_service, sheet_id):
    """Add data to all tabs"""
    
    tabs_data = {
        'companies': {
            'headers': ['Company Name', 'Website', 'Founders', 'Team Size', 'Investors', 'Latest Round Type', 'Latest Round Amount USD', 'Latest Round Date', 'Valuation', 'Core Product', 'Pricing Model', 'Target Customer', 'Business Status', 'Last Updated', 'Discovered Source'],
            'rows': [
                ['Terra AI', 'https://www.terraai.com', 'John Merrill; Anthony Corso', 41, 'Khosla Ventures; Breakthrough Energy; Rio Tinto', 'Series A', 15000000, '2026-05-20', '', 'Subsurface mapping SaaS', 'Enterprise B2B SaaS', 'Mining majors', 'active', '2026-05-27', 'original_list'],
                ['GeologicAI', 'https://www.geologicai.com', 'Grant Sanden; Yannai Segal', 89, 'Breakthrough Energy; EDC; Blue Earth Capital; BHP', 'Series B', 44000000, '2025-07-17', '', 'Core scanning + AI', 'SaaS + Services', 'Mining majors', 'active', '2026-05-27', 'original_list'],
                ['Fleet Space', 'https://www.fleetspace.com', 'Flavia Tata Nardini; Matt Pearson', 130, 'Teachers VG; Blackbird; Horizons', 'Series D', 150000000, '2024-12-11', 525000000, 'LEO satellite + seismic AI', 'End-to-end service', 'Rio Tinto; Barrick Gold', 'active', '2026-05-27', 'original_list'],
                ['VerAI', 'https://ver-ai.com', 'Yair Frastai; Amitai Axelrod', 40, 'Insight Partners; Blumberg; Chrysalix', 'Series B', 24000000, '2025-02-26', '', 'AI mineral discovery', 'Equity + Royalty', 'Explorers', 'active', '2026-05-27', 'original_list'],
                ['Stratum AI', 'https://stratum.gs', 'Farzi Yusufali; Danial Hasan', 18, 'YC; Builders VC', 'Seed', 150000, '2020-08-26', '', 'Production resource modeling', 'Services', 'Mining cos', 'active', '2026-05-27', 'original_list'],
                ['Mineral Forecast', 'https://www.mineralforecast.com', 'Javier M.; Arturo R.', 12, 'Techstars; Alumni; Spider', 'Seed', 3310000, '2023-09-12', '', 'Greenfield + Brownfield', 'SaaS', 'Miners', 'active', '2026-05-27', 'original_list'],
                ['Material Difference', 'https://materialdifference.earth', 'Gabriel Yoong; Luke Cullen', 3, 'Entrepreneurs First', 'Pre-Seed', '', '2026-03-31', '', 'Uncertainty-aware AI', 'TBD', 'Explorers', 'stealth', '2026-05-27', 'original_list'],
                ['Veracio', 'https://www.veracio.com', 'Unknown', 'Unknown', 'Unknown', 'Unknown', '', '2025-11-24', '', 'Geochemical + Core scanning AI', 'SaaS', 'Mining majors', 'discovered', '2026-05-27', 'discovery_2026-05-27'],
                ['Earth AI', 'https://earthai.ai', 'Teslyuk', 'Unknown', 'Unknown', 'Unknown', '', '2026-04-29', '', 'Critical minerals AI', 'Equity + Royalty', 'Mining explorers', 'discovered', '2026-05-27', 'discovery_2026-05-27'],
            ]
        },
        'events': {
            'headers': ['Company ID', 'Company Name', 'Event Type', 'Event Date', 'Description', 'Amount USD', 'Source URLs', 'Confidence'],
            'rows': [
                ['terra-ai', 'Terra AI', 'funding_round', '2026-05-20', 'Series A $15M from Breakthrough Energy', 15000000, 'crunchbase.com/organization/terra-ai', 0.95],
                ['terra-ai', 'Terra AI', 'partnership', '2026-05-18', 'Partnership with Rio Tinto announced', 0, 'mining-weekly.com', 0.92],
                ['terra-ai', 'Terra AI', 'hiring_surge', '2026-05-22', '8 new positions for ML engineers', 0, 'linkedin.com/company/terra-ai/jobs', 0.88],
                ['geologicai', 'GeologicAI', 'funding_round', '2025-07-17', 'Series B $44M from Blue Earth Capital', 44000000, 'crunchbase.com', 0.98],
                ['fleet-space', 'Fleet Space', 'funding_round', '2024-12-11', 'Series D $150M from TVG', 150000000, 'crunchbase.com', 0.99],
                ['fleet-space', 'Fleet Space', 'acquisition', '2025-06-03', 'Acquires HiSeis', 0, 'globalminingreview.com', 0.94],
                ['verai', 'VerAI', 'funding_round', '2025-02-26', 'Series B $24M from Insight Partners', 24000000, 'crunchbase.com', 0.96],
                ['stratum-ai', 'Stratum AI', 'funding_round', '2020-08-26', 'Seed $150K from Y Combinator', 150000, 'ycombinator.com', 0.99],
                ['mineral-forecast', 'Mineral Forecast', 'funding_round', '2023-09-12', 'Seed $3.31M from Techstars', 3310000, 'crunchbase.com', 0.92],
            ]
        },
        'update_log': {
            'headers': ['Timestamp', 'Company Name', 'Field', 'Old Value', 'New Value', 'Source URL', 'Confidence', 'Status'],
            'rows': [
                ['2026-05-27T18:30:00Z', 'Terra AI', 'team_size', '40', '41', 'linkedin.com+website', '0.95', 'auto_merged'],
                ['2026-05-27T18:28:00Z', 'GeologicAI', 'team_size', '85', '89', 'linkedin.com+crunchbase', '0.96', 'auto_merged'],
                ['2026-05-27T18:25:00Z', 'Fleet Space', 'latest_round_type', 'Series C', 'Series D', 'crunchbase.com', '0.98', 'auto_merged'],
            ]
        },
        'data_sources': {
            'headers': ['Source Name', 'URL', 'Type', 'Priority', 'Category', 'Last Scraped', 'Status', 'Notes'],
            'rows': [
                ['mining.com', 'https://mining.com', 'news', '1', 'mining_industry', '2026-05-27', 'active', 'Daily mining news'],
                ['Crunchbase', 'https://crunchbase.com', 'investor_portfolio', '1', 'startup_funding', '2026-05-27', 'active', 'Startup funding database'],
                ['PitchBook', 'https://pitchbook.com', 'investor_portfolio', '1', 'startup_funding', '2026-05-27', 'active', 'VC funding data'],
                ['BHP Ventures', 'https://bhpventures.com', 'corporate_vc', '1', 'investor_portfolio', '2026-05-27', 'active', 'BHP portfolio'],
                ['TechCrunch', 'https://techcrunch.com', 'news', '2', 'startup_news', '2026-05-27', 'active', 'Startup news'],
            ]
        },
        'raw_signals': {
            'headers': ['Company ID', 'Field', 'Value', 'Source URL', 'Source Type', 'Extracted At', 'Confidence'],
            'rows': [
                ['terra-ai', 'team_size', '42', 'terraai.com/about', 'official_website', '2026-05-27T18:30:00Z', '0.98'],
                ['terra-ai', 'founders', 'John Merrill', 'terraai.com', 'official_website', '2026-05-27T18:25:00Z', '0.99'],
                ['geologicai', 'team_size', '89', 'linkedin.com', 'linkedin', '2026-05-27T18:28:00Z', '0.96'],
            ]
        },
        'discovery_queue': {
            'headers': ['Company Name', 'Website', 'Discovered Date', 'Source', 'Status', 'Recommendation'],
            'rows': [
                ['Veracio', 'https://www.veracio.com', '2026-05-27', 'StartUS Insights', 'pending', 'High - deployed at scale'],
                ['Earth AI', 'https://earthai.ai', '2026-05-27', 'TechCrunch', 'pending', 'High - critical minerals'],
            ]
        }
    }
    
    # Populate each tab
    for tab_name, data in tabs_data.items():
        print(f"Populating {tab_name}...")
        
        # Prepare values (headers + rows)
        values = [data['headers']] + data['rows']
        
        # Update sheet
        body = {'values': values}
        try:
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=f'{tab_name}!A1',
                valueInputOption='RAW',
                body=body
            ).execute()
            rows_updated = result.get('updatedRows', 0)
            print(f"  ✅ Updated {rows_updated} rows")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def main():
    print("🚀 Creating Mohan Competitive Intelligence Google Sheet\n")
    
    # Create sheet
    result = create_sheet_with_gcloud_creds()
    if not result:
        return
    
    sheet_id, sheets_service = result
    
    # Populate sheet
    print("\nPopulating tabs...")
    populate_sheet(sheets_service, sheet_id)
    
    print(f"\n✅ Google Sheet created successfully!")
    print(f"📊 Sheet ID: {sheet_id}")
    print(f"🔗 Link: https://docs.google.com/spreadsheets/d/{sheet_id}")
    
    # Save sheet ID
    with open("GOOGLE_SHEET_ID.txt", "w") as f:
        f.write(sheet_id)
    
    print(f"\n💾 Sheet ID saved to GOOGLE_SHEET_ID.txt")

if __name__ == "__main__":
    main()
