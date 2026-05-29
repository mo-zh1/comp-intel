"""
Shared Google Sheet client for the competitor-intel skills.

Backed by a deployed Apps Script Web App (rows/cols are 1-indexed):
  GET                                                   -> all rows as a 2D list
  POST {action:"update_cell", row, col, value}          -> set one cell
  POST {action:"update_row_by_key", keyCol, keyValue,   -> set one cell in the
        targetCol, newValue}                               row whose keyCol == keyValue
  POST {action:"append", rowData:[...]}                 -> append a row

Pure stdlib (urllib) so the skills run with no third-party dependencies.
All three skills import `sheet_api` from this module.
"""

import json
import urllib.request
from typing import List, Optional

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyZNpmB-tuj30_M1uABI9wygCgWgfeDLURtUc_-ITZwHowB0PmZob7ykJQe5QyAMyDleQ/exec"
SHEET_ID = "1e9gbtCVgzp2RdWyThrdl_eEs62n63Nto3aSQtH5FXHM"


class GoogleSheetAPI:
    def __init__(self, timeout: int = 60):
        self.timeout = timeout

    def _get(self):
        with urllib.request.urlopen(WEB_APP_URL, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode())

    def _post(self, payload: dict) -> dict:
        req = urllib.request.Request(
            WEB_APP_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            text = resp.read().decode()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"status": "error", "message": text[:200]}

    def read_rows(self) -> List[list]:
        """Return the whole sheet as a list of rows (each a list of cell values)."""
        try:
            data = self._get()
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"read_rows failed: {e}")
            return []

    def header(self) -> List[str]:
        """First row, trimmed to strings."""
        rows = self.read_rows()
        return [str(c).strip() for c in rows[0]] if rows else []

    def column_index(self, name: str) -> Optional[int]:
        """1-indexed column for a header name (case-insensitive), or None."""
        target = name.strip().lower()
        for i, h in enumerate(self.header()):
            if h.strip().lower() == target:
                return i + 1
        return None

    def update_cell(self, row: int, col: int, value) -> bool:
        res = self._post({"action": "update_cell", "row": row, "col": col, "value": value})
        return res.get("status") == "success"

    def update_row_by_key(self, key_col: int, key_value: str, target_col: int, new_value) -> bool:
        res = self._post({
            "action": "update_row_by_key",
            "keyCol": key_col,
            "keyValue": key_value,
            "targetCol": target_col,
            "newValue": new_value,
        })
        return res.get("status") == "success"

    def append(self, row_values: list) -> bool:
        res = self._post({"action": "append", "rowData": row_values})
        return res.get("status") == "success"

    def test_connection(self) -> bool:
        try:
            self._get()
            return True
        except Exception as e:
            print(f"connection failed: {e}")
            return False


sheet_api = GoogleSheetAPI()


if __name__ == "__main__":
    if not sheet_api.test_connection():
        raise SystemExit("Cannot reach the sheet web app")
    rows = sheet_api.read_rows()
    print(f"Connected. {len(rows)} rows. Header: {sheet_api.header()}")
