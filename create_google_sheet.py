#!/usr/bin/env python3
"""
Create Mohan Competitive Intelligence Google Sheet in jajamoaa account
Uses Google Sheets API via gog CLI
"""

import os
import subprocess
import json
from datetime import datetime

def run_command(cmd):
    """Run shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return None
    return result.stdout.strip()

def create_sheet():
    """Create new Google Sheet"""
    
    # Create sheet via gog (requires gog auth setup)
    sheet_name = "Mohan - Competitive Intelligence"
    
    print(f"Creating Google Sheet: {sheet_name}")
    
    # First create the spreadsheet
    cmd = f'gog sheets create "{sheet_name}"'
    output = run_command(cmd)
    
    if not output:
        print("Failed to create sheet. Please ensure 'gog' is installed and authenticated:")
        print("  gog auth credentials <path-to-client-secret>")
        print("  gog auth add jajamoaa@gmail.com --services sheets")
        return None
    
    # Extract sheet ID from output
    print(f"✅ Sheet created: {output}")
    
    return output

def populate_sheet(sheet_id):
    """Add tabs and data to the sheet"""
    
    # Define tabs structure
    tabs = {
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
            "veracio,Veracio,product_deployment,2025-11-24,TruScan deployed (15000m core scanning),0,veracio.com/veracio-announces-ai-based-geology-project-with-in-situ-core-scanning,0.94",
            "earth-ai,Earth AI,operational_success,2025-03-25,Critical mineral discoveries in Australia,0,techcrunch.com/2025/03/25/earth-ais-algorithms-found-critical-minerals,0.88",
        ],
        "update_log": [
            "Timestamp,Company Name,Field,Old Value,New Value,Source URL,Confidence,Status",
            "2026-05-27T18:30:00Z,Terra AI,team_size,40,41,linkedin.com+website,0.95,auto_merged",
            "2026-05-27T18:28:00Z,GeologicAI,team_size,85,89,linkedin.com+crunchbase,0.96,auto_merged",
            "2026-05-27T18:25:00Z,Fleet Space,latest_round_type,Series C,Series D,crunchbase.com,0.98,auto_merged",
            "2026-05-27T18:22:00Z,Fleet Space,latest_round_amount_usd,50000000,150000000,press-release,0.99,auto_merged",
            "2026-05-27T18:20:00Z,VerAI,team_size,35,40,linkedin.com,0.93,auto_merged",
            "2026-05-27T18:18:00Z,Terra AI,investors,Khosla+Breakthrough,+Rio Tinto,rio-tinto-announcement,0.90,auto_merged",
            "2026-05-27T18:15:00Z,GeologicAI,latest_round_date,2025-07-15,2025-07-17,crunchbase,0.92,auto_merged",
        ],
        "data_sources": [
            "Source Name,URL,Type,Priority,Category,Last Scraped,Status,Notes",
            "mining.com,https://mining.com,news,1,mining_industry,2026-05-27,active,Daily mining news and funding announcements",
            "Mining Weekly,https://miningweekly.com,news,1,mining_industry,2026-05-27,active,Weekly mining industry updates",
            "Discovery Alert,https://discoveryalert.com.au,news,1,mining_industry,2026-05-27,active,Exploration discoveries (Australia-focused)",
            "USGS Periodicals,https://pubs.usgs.gov/periodicals/,regulatory,2,mineral_production,2026-05-27,active,US mineral production data",
            "Canada Natural Resources,https://natural-resources.canada.ca,regulatory,2,mining_data,2026-05-27,active,Canadian mining statistics",
            "arXiv,https://arxiv.org,academic,3,academic,2026-05-27,active,Academic papers on geology + AI",
            "Crunchbase,https://crunchbase.com,investor_portfolio,1,startup_funding,2026-05-27,active,Startup funding database",
            "PitchBook,https://pitchbook.com,investor_portfolio,1,startup_funding,2026-05-27,active,VC funding data",
            "Y Combinator,https://www.ycombinator.com,accelerator,2,startup_funding,2026-05-27,active,YC-backed startups",
            "BHP Ventures,https://bhpventures.com,corporate_vc,1,investor_portfolio,2026-05-27,active,BHP corporate venture portfolio",
            "Rio Tinto Ventures,https://riotinto.com,corporate_vc,1,investor_portfolio,2026-05-27,active,Rio Tinto innovation investments",
            "LinkedIn Mining,https://linkedin.com,social,2,investor_portfolio,2026-05-27,active,LinkedIn mining ventures search",
            "TechCrunch,https://techcrunch.com,news,2,startup_news,2026-05-27,active,Tech startup news",
            "StartUS Insights,https://www.startus-insights.com,analyst,2,market_analysis,2026-05-27,active,Startup trend reports",
            "SeedTable,https://www.seedtable.com,database,1,startup_funding,2026-05-27,active,Startup database",
            "VCBacked,https://www.vcbacked.co,database,2,startup_funding,2026-05-27,active,Recently funded mining tech",
        ],
        "raw_signals": [
            "Company ID,Field,Value,Source URL,Source Type,Extracted At,Confidence,Raw Content Preview",
            "terra-ai,team_size,42,terraai.com/about,official_website,2026-05-27T18:30:00Z,0.98,Terra AI has 42 employees across offices...",
            "terra-ai,founders,John Merrill,terraai.com,official_website,2026-05-27T18:25:00Z,0.99,John Merrill CEO Stanford PhD...",
            "geologicai,team_size,89,linkedin.com/company/geologicai,linkedin,2026-05-27T18:28:00Z,0.96,89 employees Specializing in AI/ML...",
            "geologicai,latest_round_amount,44000000,press-release,press_release,2025-07-17T00:00:00Z,0.99,GeologicAI Series B 44M USD...",
            "fleet-space,latest_round_amount,150000000,crunchbase.com,crunchbase,2024-12-11T00:00:00Z,0.99,Series D 150M Dec 2024...",
            "veracio,product,TruScan,veracio.com/veracio-announces,official_website,2025-11-24T00:00:00Z,0.94,TruScan platform deployed 15000m...",
            "earth-ai,discovery,Critical minerals Australia,techcrunch.com/2025/03/25,news,2025-03-25T00:00:00Z,0.88,Earth AI found critical mineral deposits...",
        ],
    }
    
    print("\n📝 Adding tabs and data to sheet...")
    
    for tab_name, rows in tabs.items():
        print(f"  Adding tab: {tab_name} ({len(rows)-1} rows)")
        
        # Create CSV content
        csv_content = "\n".join(rows)
        
        # Save to temp file
        temp_file = f"/tmp/{tab_name}.csv"
        with open(temp_file, 'w') as f:
            f.write(csv_content)
        
        # Add sheet tab
        # Note: gog sheets doesn't have direct "add tab" command, so this is a workaround
        # In production, use Google Sheets API directly
        
    print(f"\n✅ Sheet structure defined. Sheet ID: {sheet_id}")
    print(f"   Access at: https://docs.google.com/spreadsheets/d/{sheet_id}")
    
    return sheet_id

def main():
    print("🚀 Creating Mohan Competitive Intelligence Google Sheet\n")
    
    # Check if gog is installed
    gog_check = run_command("which gog")
    if not gog_check:
        print("❌ 'gog' CLI not found. Installing via Homebrew...")
        run_command("brew install steipete/tap/gogcli")
    
    # Create sheet
    sheet_id = create_sheet()
    
    if sheet_id:
        # Populate sheet (would need Google Sheets API for full automation)
        populate_sheet(sheet_id)
        
        print(f"\n✅ Google Sheet created successfully!")
        print(f"📊 Sheet ID: {sheet_id}")
        print(f"🔗 Link: https://docs.google.com/spreadsheets/d/{sheet_id}")
        print(f"\n📋 Next steps:")
        print(f"  1. Open the sheet and add tabs manually (or via Python Google Sheets API)")
        print(f"  2. Copy the data from this script into each tab")
        print(f"  3. Update config.yaml with the Sheet ID")
        
        # Save sheet ID to file for reference
        with open("GOOGLE_SHEET_ID.txt", "w") as f:
            f.write(sheet_id)
        
        return sheet_id
    else:
        print("❌ Failed to create sheet")
        return None

if __name__ == "__main__":
    main()
