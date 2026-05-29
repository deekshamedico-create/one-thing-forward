"""
calendar_api.py — Google Calendar via Service Account from Streamlit Secrets.
"""

from datetime import datetime, timezone


def get_today_events():
    """
    Fetch today's events. Returns list of dicts or [] on failure.
    Stores any error in st.session_state["cal_error"] for debugging.
    """
    try:
        import streamlit as st
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        # Read from secrets
        if "gcp_service_account" not in st.secrets:
            st.session_state["cal_error"] = "gcp_service_account not found in secrets"
            return []

        creds_info = dict(st.secrets["gcp_service_account"])

        creds = Credentials.from_service_account_info(
            creds_info,
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )

        service = build("calendar", "v3", credentials=creds, cache_discovery=False)

        # IST is UTC+5:30 — get today's range in UTC
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
            end   = e["end"].get("dateTime",   e["end"].get("date", ""))
            try:
                # Convert to IST
                from datetime import timedelta
                IST_OFFSET = timedelta(hours=5, minutes=30)
                start_dt  = datetime.fromisoformat(start.replace("Z", "+00:00"))
                end_dt    = datetime.fromisoformat(end.replace("Z", "+00:00"))
                start_fmt = (start_dt + IST_OFFSET).strftime("%I:%M %p")
                end_fmt   = (end_dt   + IST_OFFSET).strftime("%I:%M %p")
            except Exception:
                start_fmt = start[:10]
                end_fmt   = end[:10]

            events.append({
                "title":      e.get("summary", "Untitled"),
                "start_time": start_fmt,
                "end_time":   end_fmt,
                "location":   e.get("location", ""),
            })

        st.session_state["cal_error"] = f"OK — {len(events)} events fetched"
        return events

    except Exception as ex:
        try:
            import streamlit as st
            st.session_state["cal_error"] = str(ex)
        except Exception:
            pass
        return []
