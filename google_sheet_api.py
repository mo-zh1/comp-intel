"""
Google Sheet HTTP API wrapper
Uses Apps Script to read/write without SDK
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime

class GoogleSheetAPI:
    """
    Simple HTTP API wrapper for Google Sheets
    No SDK required, just standard HTTP requests
    """
    
    # Sheet ID from mo.zh's setup
    SHEET_ID = "1e9gbtCVgzp2RdWyThrdl_eEs62n63Nto3aSQtH5FXHM"
    
    # Web App URL (Apps Script endpoint)
    WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyZNpmB-tuj30_M1uABI9wygCgWgfeDLURtUc_-ITZwHowB0PmZob7ykJQe5QyAMyDleQ/exec"
    
    def __init__(self):
        self.timeout = 30
    
    def read_all_data(self) -> List[List]:
        """Read entire sheet"""
        try:
            response = requests.get(self.WEB_APP_URL, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to read sheet: {e}")
            return []
    
    def read_range(self, sheet_name: str, range_spec: str) -> List[List]:
        """Read specific range (if supported by Apps Script)"""
        # Apps Script may not support range queries
        # Return all data and filter client-side
        return self.read_all_data()
    
    def update_cell(self, row: int, col: int, value: str) -> bool:
        """
        Update a single cell
        row: 1-indexed row number
        col: 1-indexed column number
        """
        try:
            payload = {
                "action": "update_cell",
                "row": row,
                "col": col,
                "value": value
            }
            response = requests.post(self.WEB_APP_URL, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get("status") == "success"
        except Exception as e:
            print(f"❌ Failed to update cell: {e}")
            return False
    
    def update_row_by_key(self, key_col: int, key_value: str, target_col: int, new_value: str) -> bool:
        """
        Update a row by matching a key value
        """
        try:
            payload = {
                "action": "update_row_by_key",
                "keyCol": key_col,
                "keyValue": key_value,
                "targetCol": target_col,
                "newValue": new_value
            }
            response = requests.post(self.WEB_APP_URL, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get("status") == "success"
        except Exception as e:
            print(f"❌ Failed to update row: {e}")
            return False
    
    def append_row(self, values: List[str]) -> bool:
        """Append a new row (if supported)"""
        try:
            payload = {
                "action": "append_row",
                "values": values
            }
            response = requests.post(self.WEB_APP_URL, json=payload, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            return result.get("status") == "success"
        except Exception as e:
            print(f"❌ Failed to append row: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test if API is working"""
        try:
            response = requests.get(self.WEB_APP_URL, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

# Create global instance
sheet_api = GoogleSheetAPI()

if __name__ == "__main__":
    print("Testing Google Sheet API...")
    
    # Test connection
    if sheet_api.test_connection():
        print("✅ Connected to Google Sheet")
    else:
        print("❌ Cannot connect")
        exit(1)
    
    # Read data
    data = sheet_api.read_all_data()
    print(f"✅ Read {len(data)} rows")
    
    # Test update
    if sheet_api.update_cell(2, 14, f"Test {datetime.now().strftime('%Y-%m-%d %H:%M')}"):
        print("✅ Cell update successful")
    else:
        print("❌ Cell update failed")
