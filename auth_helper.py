"""
Helper module for getting Google Sheets API credentials
Tries multiple authentication methods
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Optional

def get_credentials():
    """
    Get Google Sheets API credentials using multiple fallback methods
    Returns: credentials object suitable for google-api-python-client
    """
    
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    
    # Method 1: Try Application Default Credentials
    try:
        from google.auth import default
        credentials, _ = default(scopes=['https://www.googleapis.com/auth/spreadsheets'])
        print("✅ Using Application Default Credentials")
        return credentials
    except Exception as e:
        print(f"⚠️  ADC not available: {type(e).__name__}")
    
    # Method 2: Try to get token from gcloud
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout.strip():
            token = result.stdout.strip()
            credentials = Credentials(token=token)
            print("✅ Using gcloud cached token")
            return credentials
    except Exception as e:
        print(f"⚠️  gcloud token fetch failed: {type(e).__name__}")
    
    # Method 3: Try to use wrapper if available
    try:
        wrapper_path = Path.home() / ".config" / "gcloud" / "gcloud_creds_wrapper.py"
        if wrapper_path.exists():
            import sys
            sys.path.insert(0, str(wrapper_path.parent))
            from gcloud_creds_wrapper import credentials as wrapper_creds
            print("✅ Using gcloud credentials wrapper")
            return wrapper_creds
    except Exception as e:
        print(f"⚠️  Wrapper method failed: {type(e).__name__}")
    
    # Method 4: Try service account key if provided
    try:
        sa_key_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if sa_key_path and Path(sa_key_path).exists():
            from google.oauth2 import service_account
            credentials = service_account.Credentials.from_service_account_file(
                sa_key_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            print(f"✅ Using service account from {sa_key_path}")
            return credentials
    except Exception as e:
        print(f"⚠️  Service account method failed: {type(e).__name__}")
    
    # No credentials available
    print("❌ Could not obtain credentials via any method")
    return None

def build_sheets_service():
    """Build authenticated Sheets service"""
    from googleapiclient.discovery import build
    
    credentials = get_credentials()
    
    if not credentials:
        return None
    
    try:
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"❌ Failed to build Sheets service: {e}")
        return None

def test_credentials():
    """Test if credentials are working"""
    service = build_sheets_service()
    
    if not service:
        return False
    
    try:
        # Try to access a test spreadsheet
        result = service.spreadsheets().get(
            spreadsheetId='1TXnbzCrwkJCTLaNZZKFcKC9x23wqsqXTKU8Sv5sqHMU',
            fields='properties.title'
        ).execute()
        
        print(f"✅ Credentials working! Sheet: {result['properties']['title']}")
        return True
    except Exception as e:
        print(f"❌ Credentials test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Google Sheets credentials...")
    test_credentials()
