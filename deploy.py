#!/usr/bin/env python3
import subprocess
import json
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Get token from mohan account
subprocess.run(['gcloud', 'config', 'set', 'account', 'account@mohan.media'], capture_output=True, check=True)
result = subprocess.run(['gcloud', 'auth', 'print-access-token'], capture_output=True, text=True, check=True)
token = result.stdout.strip()

# Build API clients
creds = Credentials(token=token)
sheets = build('sheets', 'v4', credentials=creds)
drive = build('drive', 'v3', credentials=creds)

# Create spreadsheet
body = {
    'properties': {
        'title': 'Mohan - Competitive Intelligence',
        'locale': 'en_US',
        'timeZone': 'America/New_York'
    },
    'sheets': [
        {'properties': {'title': 'companies'}},
        {'properties': {'title': 'events'}},
        {'properties': {'title': 'update_log'}},
        {'properties': {'title': 'data_sources'}},
        {'properties': {'title': 'raw_signals'}},
        {'properties': {'title': 'discovery_queue'}},
    ]
}

resp = sheets.spreadsheets().create(body=body, fields='spreadsheetId').execute()
sheet_id = resp['spreadsheetId']
print(f"✅ Sheet created: {sheet_id}")

# Enable sharing
drive.permissions().create(
    fileId=sheet_id,
    body={'type': 'anyone', 'role': 'writer'},
    fields='id'
).execute()
print("✅ Sharing enabled")

# Save ID
with open('GOOGLE_SHEET_ID.txt', 'w') as f:
    f.write(sheet_id)

print(f"\n📊 Sheet ID: {sheet_id}")
print(f"🔗 Link: https://docs.google.com/spreadsheets/d/{sheet_id}")
