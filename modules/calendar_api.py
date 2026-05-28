"""
calendar_api.py — Google Calendar integration.

SETUP (one-time):
1. Go to https://console.cloud.google.com
2. Create a project → enable Google Calendar API
3. Create OAuth credentials (Desktop app) → download as credentials.json
4. Place credentials.json in the project root folder
5. On first run, a browser window opens for sign-in → token.json is created automatically

If you skip setup, the app still works — calendar section just shows a friendly message.
"""

import os
import json
from datetime import datetime, timezone
from pathlib import Path

CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _get_service():
    """Authenticate and return a Google Calendar service object."""
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        return None

    if not Path(CREDENTIALS_FILE).exists():
        return None

    creds = None
    if Path(TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def get_today_events():
    """
    Returns a list of today's calendar events.
    Each event is a dict: {title, start_time, end_time, location}
    Returns [] if calendar is not configured.
    """
    service = _get_service()
    if not service:
        return []

    try:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_of_day   = now.replace(hour=23, minute=59, second=59).isoformat()

        result = service.events().list(
            calendarId="primary",
            timeMin=start_of_day,
            timeMax=end_of_day,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = []
        for e in result.get("items", []):
            start = e["start"].get("dateTime", e["start"].get("date", ""))
            end   = e["end"].get("dateTime",   e["end"].get("date",   ""))
            # Format time nicely
            try:
                start_fmt = datetime.fromisoformat(start).strftime("%I:%M %p")
                end_fmt   = datetime.fromisoformat(end).strftime("%I:%M %p")
            except Exception:
                start_fmt = start
                end_fmt   = end

            events.append({
                "title":      e.get("summary", "Untitled"),
                "start_time": start_fmt,
                "end_time":   end_fmt,
                "location":   e.get("location", ""),
            })
        return events

    except Exception:
        return []
