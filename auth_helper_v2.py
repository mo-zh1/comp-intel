"""
Google Sheets API authentication helper - Version 2
Uses direct gog CLI calling without keyring
"""

import subprocess
import json
import sys
from pathlib import Path

def call_gog(args, json_output=True):
    """Call gog with given arguments"""
    cmd = ["gog"] + args
    
    if json_output:
        cmd.append("--json")
    
    try:
        # Try with different keyring password settings
        env = None
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        if result.returncode == 0:
            if json_output and result.stdout.strip():
                try:
                    return json.loads(result.stdout)
                except:
                    return result.stdout
            return result.stdout
        else:
            # Check error message
            if "keyring" in result.stderr.lower() or "password" in result.stderr.lower():
                # Try to work around keyring issue
                return None
            print(f"gog error: {result.stderr}", file=sys.stderr)
            return None
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def build_sheets_service():
    """
    Build Google Sheets service using gog
    Returns a wrapper object that can read/write sheets
    """
    
    # Check if gog can access sheets
    print("Checking gog access to Google Sheets...")
    
    result = call_gog(
        ["sheets", "get", "1TXnbzCrwkJCTLaNZZKFcKC9x23wqsqXTKU8Sv5sqHMU", 
         "companies!A1:A1", 
         "--account=jajamoaa@gmail.com"],
        json_output=True
    )
    
    if result is None:
        print("❌ Cannot access gog sheets (keyring issue)")
        print("   Falling back to standard Google API...")
        
        # Fall back to standard Google API
        try:
            from google.auth import default
            credentials, _ = default(scopes=['https://www.googleapis.com/auth/spreadsheets'])
            from googleapiclient.discovery import build
            return build('sheets', 'v4', credentials=credentials)
        except Exception as e:
            print(f"❌ Standard API also failed: {e}")
            return None
    
    print("✅ gog can access Google Sheets")
    
    # Return a wrapper that uses gog CLI
    return GogSheetsWrapper()

class GogSheetsWrapper:
    """Wrapper around gog CLI for Sheets API operations"""
    
    def __init__(self):
        self.sheet_id = "1TXnbzCrwkJCTLaNZZKFcKC9x23wqsqXTKU8Sv5sqHMU"
        self.account = "jajamoaa@gmail.com"
    
    def get_values(self, range_spec):
        """Read values from sheet"""
        result = subprocess.run([
            "gog", "sheets", "get", self.sheet_id, range_spec,
            f"--account={self.account}",
            "--plain"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse TSV output
            lines = result.stdout.strip().split('\n')
            return [line.split('\t') for line in lines]
        return []
    
    def append_values(self, range_spec, values):
        """Append values to sheet"""
        flat_values = []
        for row in values:
            flat_values.extend(row)
        
        result = subprocess.run([
            "gog", "sheets", "append", self.sheet_id, range_spec,
            f"--account={self.account}",
            "--plain"
        ] + flat_values, capture_output=True, text=True)
        
        return result.returncode == 0

def get_credentials():
    """Get credentials (for compatibility)"""
    service = build_sheets_service()
    return service

if __name__ == "__main__":
    print("Testing gog-based authentication...")
    service = build_sheets_service()
    if service:
        print("✅ Service created")
    else:
        print("❌ Failed to create service")
