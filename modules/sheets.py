"""
sheets.py — Google Sheets integration for One Thing Forward.

READ  : Uses public CSV export — no auth needed (sheet must be shared as "Anyone with link can view")
WRITE : Uses gspread + Service Account for saving FA results

SETUP for writing (one-time):
1. Go to console.cloud.google.com
2. Enable Google Sheets API
3. Create a Service Account → download JSON key → rename to service_account.json
4. Place service_account.json in project root
5. Share your Google Sheet with the service account email (Editor access)
6. Add gspread to requirements.txt

The dashboard reads your positions without any setup — just keep the sheet shared publicly.
"""

import pandas as pd
import requests
import io
from datetime import datetime

# ── Your sheet config ──────────────────────────────────────────────────────────
SHEET_ID       = "1tT9NLUcpVqsVN7dFJ2O2v4I4lDwxZcHPAUStQff16OY"
SHEET_URL      = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"
POSITIONS_GID  = "0"       # First sheet (Positions) — gid=0 by default
CLOSED_GID     = ""        # Will auto-detect

def _csv_url(gid="0"):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"


def get_positions():
    """
    Fetch live positions from the Positions sheet.
    Returns a list of dicts or empty list on failure.
    """
    try:
        url      = _csv_url("0")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        df.columns = [c.strip() for c in df.columns]
        return df.to_dict("records")
    except Exception as e:
        return []


def get_closed_trades():
    """
    Fetch closed trades. Try to find the Closed sheet by fetching sheet metadata.
    Falls back to gid=1 if not found.
    """
    try:
        # Try gid=788593635 — will detect below
        # First attempt gid=1 (second sheet)
        for gid in ["1", "788593635", "2"]:
            try:
                url      = _csv_url(gid)
                response = requests.get(url, timeout=8)
                if response.status_code == 200:
                    df = pd.read_csv(io.StringIO(response.text))
                    df.columns = [c.strip() for c in df.columns]
                    # Check if it looks like closed trades (has Exit Price column)
                    if "Exit Price" in df.columns or "exit_price" in df.columns.str.lower().tolist():
                        return df.to_dict("records")
            except Exception:
                continue
        return []
    except Exception:
        return []


def save_fa_result_to_sheet(ticker, horizon, analysis_text):
    """
    Save FA analysis result to a 'FA Results' tab in the Google Sheet.
    Requires gspread + service_account.json in project root.
    Returns (success: bool, message: str)
    """
    import os
    from pathlib import Path

    if not Path("service_account.json").exists():
        return False, "service_account.json not found. See Settings for setup instructions."

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds  = Credentials.from_service_account_file("service_account.json", scopes=scopes)
        client = gspread.authorize(creds)
        sheet  = client.open_by_key(SHEET_ID)

        # Get or create FA Results worksheet
        try:
            ws = sheet.worksheet("FA Results")
        except gspread.WorksheetNotFound:
            ws = sheet.add_worksheet(title="FA Results", rows=1000, cols=5)
            ws.append_row(["Date", "Ticker", "Horizon", "Summary (first 500 chars)", "Full Analysis"])

        # Truncate for summary column
        summary = analysis_text[:500].replace("\n", " ")
        row     = [
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            ticker.upper(),
            horizon,
            summary,
            analysis_text[:5000],  # Google Sheets cell limit
        ]
        ws.append_row(row)
        return True, f"Saved {ticker.upper()} FA result to Google Sheet → FA Results tab."

    except ImportError:
        return False, "gspread not installed. Add 'gspread' to requirements.txt and redeploy."
    except Exception as e:
        return False, f"Sheet write error: {str(e)}"
