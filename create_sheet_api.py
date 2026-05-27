#!/usr/bin/env python3
"""
Create Google Sheet using Google Sheets API directly
Works without TTY requirement
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.discovery import build

# Scopes required
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def get_credentials():
    """Get Google API credentials"""
    try:
        # Try to use default credentials first (service account or Application Default)
        from google.auth import default
        credentials, project = default(scopes=SCOPES)
        return credentials
    except DefaultCredentialsError:
        print("Default credentials not found. Using OAuth flow...")
        # Fall back to OAuth2 flow
        # This requires client_secrets.json in the home directory
        secrets_path = os.path.expanduser("~/.config/gcloud/client_secrets.json")
        
        if not os.path.exists(secrets_path):
            print(f"❌ Missing credentials file at {secrets_path}")
            print("Please set up Google API credentials first:")
            print("  1. Go to https://console.cloud.google.com/apis/credentials")
            print("  2. Create OAuth2 credentials (type: Desktop application)")
            print("  3. Download and save to ~/.config/gcloud/client_secrets.json")
            return None
        
        flow = InstalledAppFlow.from_client_secrets_file(secrets_path, SCOPES)
        credentials = flow.run_local_server(port=8080)
        return credentials

def create_sheet(credentials, title, tabs=None):
    """Create a new Google Sheet with specified tabs"""
    
    service = build('sheets', 'v4', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)
    
    # Create spreadsheet
    spreadsheet = {
        'properties': {
            'title': title,
            'locale': 'en_US',
            'autoRecalc': 'ON_CHANGE',
            'timeZone': 'America/New_York'
        },
        'sheets': []
    }
    
    # Add default sheet if no tabs specified
    if tabs:
        for i, tab_name in enumerate(tabs.keys()):
            spreadsheet['sheets'].append({
                'properties': {
                    'sheetId': i,
                    'title': tab_name,
                    'index': i,
                    'sheetType': 'GRID',
                    'gridProperties': {
                        'rowCount': 1000,
                        'columnCount': 20
                    }
                }
            })
    
    print(f"Creating spreadsheet: {title}")
    result = service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
    spreadsheet_id = result.get('spreadsheetId')
    
    print(f"✅ Spreadsheet created: {spreadsheet_id}")
    
    # Share with "anyone with link can edit"
    try:
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body={'type': 'anyone', 'role': 'writer'},
            fields='id'
        ).execute()
        print("✅ Sharing enabled: Anyone with link can edit")
    except Exception as e:
        print(f"⚠️ Could not set sharing: {e}")
    
    return spreadsheet_id

def populate_tabs(credentials, spreadsheet_id, tabs_data):
    """Populate tabs with data"""
    
    service = build('sheets', 'v4', credentials=credentials)
    
    for tab_name, rows in tabs_data.items():
        if not rows:
            continue
        
        print(f"Populating tab: {tab_name}")
        
        # Prepare data
        values = [
            [cell if isinstance(cell, str) else str(cell) for cell in row.split(',')]
            for row in rows
        ]
        
        # Update sheet
        body = {
            'values': values
        }
        
        try:
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f'{tab_name}!A1',
                valueInputOption='RAW',
                body=body
            ).execute()
            print(f"  ✅ Updated {result.get('updatedRows')} rows")
        except Exception as e:
            print(f"  ❌ Error: {e}")

def main():
    print("🚀 Creating Mohan Competitive Intelligence Google Sheet\n")
    
    # Get credentials
    credentials = get_credentials()
    if not credentials:
        print("❌ Failed to authenticate. Please set up credentials.")
        return None
    
    # Define tabs
    tabs = {
        "companies": None,
        "events": None,
        "update_log": None,
        "data_sources": None,
        "raw_signals": None,
        "discovery_queue": None
    }
    
    # Tab data
    tabs_data = {
        "companies": [
            "Company Name,Website,Founders,Team Size,Investors,Latest Round Type,Latest Round Amount USD,Latest Round Date,Valuation,Core Product,Pricing Model,Target Customer,Business Status,Last Updated,Discovered Source",
            "Terra AI,https://www.terraai.com,John Merrill; Anthony Corso,41,Khosla Ventures; Breakthrough Energy; Rio Tinto,Series A,15000000,2026-05-20,,Subsurface mapping SaaS,Enterprise B2B SaaS,Mining majors,active,2026-05-27,original_list",
            "GeologicAI,https://www.geologicai.com,Grant Sanden; Yannai Segal,89,Breakthrough Energy; EDC; Blue Earth Capital; BHP,Series B,44000000,2025-07-17,,Core scanning + AI,SaaS + Services,Mining majors,active,2026-05-27,original_list",
            "Fleet Space,https://www.fleetspace.com,Flavia Tata Nardini; Matt Pearson,130,Teachers VG; Blackbird; Horizons,Series D,150000000,2024-12-11,525000000,LEO satellite + seismic AI,End-to-end service,Rio Tinto; Barrick Gold,active,2026-05-27,original_list",
            "VerAI,https://ver-ai.com,Yair Frastai; Amitai Axelrod,40,Insight Partners; Blumberg; Chrysalix,Series B,24000000,2025-02-26,,AI mineral discovery,Equity + Royalty,Explorers,active,2026-05-27,original_list",
            "Stratum AI,https://stratum.gs,Farzi Yusufali; Danial Hasan,18,YC; Builders VC,Seed,150000,2020-08-26,,Production resource modeling,Services,Mining cos,active,2026-05-27,original_list",
            "Mineral Forecast,https://www.mineralforecast.com,Javier M.; Arturo R.,12,Techstars; Alumni; Spider,Seed,3310000,2023-09-12,,Greenfield + Brownfield,SaaS,Miners,active,2026-05-27,original_list",
            "Material Difference,https://materialdifference.earth,Gabriel Yoong; Luke Cullen,3,Entrepreneurs First,Pre-Seed,0,2026-03-31,,Uncertainty-aware AI,TBD,Explorers,stealth,2026-05-27,original_list",
            "Veracio,https://www.veracio.com,Unknown,Unknown,Unknown,Unknown,Unknown,2025-11-24,,Geochemical + Core scanning AI,SaaS,Mining majors,discovered,2026-05-27,discovery_2026-05-27",
            "Earth AI,https://earthai.ai,Teslyuk,Unknown,Unknown,Unknown,Unknown,2026-04-29,,Critical minerals AI + Resource,Equity + Royalty,Mining explorers,discovered,2026-05-27,discovery_2026-05-27",
        ],
        "events": [
            "Company ID,Company Name,Event Type,Event Date,Description,Amount USD,Source URLs,Confidence",
            "terra-ai,Terra AI,funding_round,2026-05-20,Series A $15M from Breakthrough Energy,15000000,crunchbase.com/organization/terra-ai,0.95",
            "terra-ai,Terra AI,partnership,2026-05-18,Partnership with Rio Tinto announced,0,mining-weekly.com/terra-ai-rio-tinto,0.92",
            "terra-ai,Terra AI,hiring_surge,2026-05-22,8 new positions for ML/geology engineers,0,linkedin.com/company/terra-ai/jobs,0.88",
            "geologicai,GeologicAI,funding_round,2025-07-17,Series B $44M from Blue Earth Capital,44000000,crunchbase.com/organization/geologicai,0.98",
            "fleet-space,Fleet Space,funding_round,2024-12-11,Series D $150M from Teachers Venture Growth,150000000,crunchbase.com/organization/fleet-space-technologies,0.99",
            "fleet-space,Fleet Space,acquisition,2025-06-03,Acquires HiSeis seismic sensors,0,globalminingreview.com/fleet-space-acquires-hiseis,0.94",
            "verai,VerAI,funding_round,2025-02-26,Series B $24M from Insight Partners,24000000,crunchbase.com/organization/verai,0.96",
            "stratum-ai,Stratum AI,funding_round,2020-08-26,Seed $150K from Y Combinator,150000,ycombinator.com,0.99",
            "mineral-forecast,Mineral Forecast,funding_round,2023-09-12,Seed $3.31M from Techstars,3310000,crunchbase.com/organization/mineral-forecast,0.92",
        ],
        "update_log": [
            "Timestamp,Company Name,Field,Old Value,New Value,Source URL,Confidence,Status",
            "2026-05-27T18:30:00Z,Terra AI,team_size,40,41,linkedin.com+website,0.95,auto_merged",
            "2026-05-27T18:28:00Z,GeologicAI,team_size,85,89,linkedin.com+crunchbase,0.96,auto_merged",
        ],
        "data_sources": [
            "Source Name,URL,Type,Priority,Category,Last Scraped,Status,Notes",
            "mining.com,https://mining.com,news,1,mining_industry,2026-05-27,active,Daily mining news",
            "Crunchbase,https://crunchbase.com,investor_portfolio,1,startup_funding,2026-05-27,active,Startup funding database",
        ],
        "raw_signals": [
            "Company ID,Field,Value,Source URL,Source Type,Extracted At,Confidence",
            "terra-ai,team_size,42,terraai.com/about,official_website,2026-05-27T18:30:00Z,0.98",
        ],
        "discovery_queue": [
            "Company Name,Website,Discovered Date,Source,Status,Recommendation",
            "Veracio,https://www.veracio.com,2026-05-27,StartUS Insights,pending,High - deployed at scale",
            "Earth AI,https://earthai.ai,2026-05-27,TechCrunch,pending,High - critical minerals focus",
        ]
    }
    
    # Create sheet
    sheet_id = create_sheet(credentials, "Mohan - Competitive Intelligence", tabs)
    
    if sheet_id:
        # Populate tabs
        print("\nPopulating tabs...")
        populate_tabs(credentials, sheet_id, tabs_data)
        
        print(f"\n✅ Google Sheet created successfully!")
        print(f"📊 Sheet ID: {sheet_id}")
        print(f"🔗 Link: https://docs.google.com/spreadsheets/d/{sheet_id}")
        
        # Save sheet ID
        with open("GOOGLE_SHEET_ID.txt", "w") as f:
            f.write(sheet_id)
        print(f"\n💾 Sheet ID saved to GOOGLE_SHEET_ID.txt")
        
        return sheet_id
    else:
        print("❌ Failed to create sheet")
        return None

if __name__ == "__main__":
    main()
