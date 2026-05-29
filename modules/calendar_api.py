"""
calendar_api.py — Google Calendar integration using Service Account.
Credentials are read from Streamlit Secrets (no file needed).
"""

from datetime import datetime, timezone


def get_today_events():
    """
    Fetch today's calendar events using service account from Streamlit secrets.
    Returns a list of dicts: {title, start_time, end_time, location}
    Returns [] if not configured or on any error.
    """
    try:
        import streamlit as st
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        # Load credentials from Streamlit secrets
        creds_dict = dict(st.secrets["gcp_service_account"])

        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )

        service = build("calendar", "v3", credentials=creds, cache_discovery=False)

        # Today's time range in UTC
        now          = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0,  minute=0,  second=0,  microsecond=0).isoformat()
        end_of_day   = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

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
