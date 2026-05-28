#!/usr/bin/env python3
"""
Bridge to use gog's OAuth tokens for Google Sheets API
gog already has jajamoaa@gmail.com authenticated
"""

import subprocess
import json
import sys
from pathlib import Path

def call_gog_sheets(command, sheet_id, range_spec, values=None):
    """
    Call gog sheets command and return parsed result
    """
    
    cmd = [
        "gog",
        "sheets",
        command,
        sheet_id,
        range_spec,
        "--account=jajamoaa@gmail.com",
        "--json"
    ]
    
    if values:
        cmd.extend(values)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"gog error: {result.stderr}")
            return None
        
        # Parse JSON output
        try:
            return json.loads(result.stdout)
        except:
            return result.stdout
            
    except Exception as e:
        print(f"Error calling gog: {e}")
        return None

def test_gog():
    """Test if gog can access the Google Sheet"""
    print("Testing gog access to Google Sheets...")
    
    sheet_id = "1TXnbzCrwkJCTLaNZZKFcKC9x23wqsqXTKU8Sv5sqHMU"
    
    # Try to read
    result = call_gog_sheets("get", sheet_id, "companies!A1:E3")
    
    if result:
        print("✅ gog can access Google Sheets!")
        print(f"Result: {result}")
        return True
    else:
        print("❌ gog cannot access Google Sheets")
        return False

if __name__ == "__main__":
    test_gog()
