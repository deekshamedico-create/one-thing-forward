"""
calendar_api.py — Google Calendar via Service Account from Streamlit Secrets.
Uses the account owner's calendar email directly instead of "primary".
"""

from datetime import datetime, timezone, timedelta

# Your Google account email — this is the calendar to fetch from
CALENDAR_ID = "deekshamedico@gmail.com"  # ← your Gmail


def get_today_events():
    try:
        import streamlit as st
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        if "gcp_service_account" not in st.secrets:
            st.session_state["cal_error"] = "secrets not found"
            return []

        creds = Credentials.from_service_account_info(
            dict(st.secrets["gcp_service_account"]),
            scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )

        service = build("calendar", "v3", credentials=creds, cache_discovery=False)

        # Today in IST converted to UTC range
        IST = timezone(timedelta(hours=5, minutes=30))
        now_ist      = datetime.now(IST)
        start_of_day = now_ist.replace(hour=0,  minute=0,  second=0,  microsecond=0).astimezone(timezone.utc).isoformat()
        end_of_day   = now_ist.replace(hour=23, minute=59, second=59, microsecond=0).astimezone(timezone.utc).isoformat()

        result = service.events().list(
            calendarId=CALENDAR_ID,
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
                start_fmt = datetime.fromisoformat(start.replace("Z", "+00:00")).astimezone(IST).strftime("%I:%M %p")
                end_fmt   = datetime.fromisoformat(end.replace("Z",   "+00:00")).astimezone(IST).strftime("%I:%M %p")
            except Exception:
                start_fmt = start[:10]
                end_fmt   = end[:10]

            events.append({
                "title":      e.get("summary", "Untitled"),
                "start_time": start_fmt,
                "end_time":   end_fmt,
                "location":   e.get("location", ""),
            })

        st.session_state["cal_error"] = f"OK — {len(events)} events"
        return events

    except Exception as ex:
        try:
            import streamlit as st
            st.session_state["cal_error"] = str(ex)
        except Exception:
            pass
        return []
