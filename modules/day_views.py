"""
day_views.py — Renders the unique dashboard for each weekday.
Each function receives (data_module, calendar_events).
"""

import streamlit as st
from datetime import date
from modules import database as db
from modules.styles import DAY_CONFIG, DAY_COLORS, CONTENT_STATUSES
from modules import sheets as sh

TASKS_PER_DAY = 3


# ── Shared components ─────────────────────────────────────────────────────────

def _week_strip(today_key):
    chips = ""
    for i, cfg in DAY_CONFIG.items():
        cls = "day-chip active" if i == today_key else "day-chip"
        chips += (
            f'<div class="{cls}">'
            f'<span class="day-chip-emoji">{cfg["emoji"]}</span>'
            f'<span class="day-chip-label">{cfg["name"][:3]}</span>'
            f'</div>'
        )
    st.markdown(f'<div class="week-strip">{chips}</div>', unsafe_allow_html=True)


def _page_header(day_key, subtitle=""):
    cfg = DAY_CONFIG[day_key]
    accent = DAY_COLORS[day_key]
    today_str = date.today().strftime("%A, %d %B %Y")
    st.markdown(f"""
    <div class="page-header">
        <div class="page-eyebrow">{cfg['name']}</div>
        <div class="page-title">{cfg['emoji']}&nbsp;{cfg['category']}</div>
        <div class="page-subtitle">{today_str}{' · ' + subtitle if subtitle else ''}</div>
        <div class="accent-rule"></div>
    </div>
    """, unsafe_allow_html=True)


def _calendar_section(events):
    st.markdown('<div class="section-label">Today\'s Schedule</div>', unsafe_allow_html=True)
    if events:
        html = ""
        for e in events:
            loc = '<div class="cal-location">\U0001f4cd ' + e["location"] + '</div>' if e.get("location") else ""
            t   = e["start_time"]
            ti  = e["title"]
            html += '<div class="cal-event"><div class="cal-time">' + t + '</div><div><div class="cal-title">' + ti + '</div>' + loc + '</div></div>'
        st.markdown(html, unsafe_allow_html=True)
        return
    today_str    = str(date.today())
    sched_key    = "sched_" + today_str
    saved        = st.session_state.get(sched_key, "")
    with st.expander("+ Add schedule for today", expanded=False):
        new_val = st.text_area(
            "sched", value=saved,
            key="sched_ta_" + today_str,
            label_visibility="collapsed",
            placeholder="9:00 AM - OPD\n11:30 AM - Surgery\n2:00 PM - Meeting",
            height=120,
        )
        if st.button("Save", key="sched_btn_" + today_str):
            st.session_state[sched_key] = new_val
            st.rerun()
    if saved:
        html = ""
        for line in [l.strip() for l in saved.split("\n") if l.strip()]:
            parts = line.replace(" - ", " — ").split(" — ", 1)
            if len(parts) == 2:
                html += '<div class="cal-event"><div class="cal-time">' + parts[0] + '</div><div class="cal-title">' + parts[1] + '</div></div>'
            else:
                html += '<div class="cal-event"><div class="cal-time">·</div><div class="cal-title">' + line + '</div></div>'
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.caption("No schedule added. Tap above to add.")

def _task_section(day_key, label="Focus tasks"):
    tasks = db.get_tasks(day_key=day_key, status="pending")
    active = tasks[:TASKS_PER_DAY]
    queued = tasks[TASKS_PER_DAY:]

    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)

    if not active:
        st.caption("No tasks yet. Add some below.")
        return

    # Task rows (HTML display)
    rows = ""
    for i, t in enumerate(active):
        pri = '<span class="priority-high">● HIGH</span>&nbsp;' if t["priority"] == 1 else ""
        done_note = f"Done {t['done_count']}×" if t["done_count"] > 0 else "Recurring"
        rows += f"""
        <div class="task-row">
            <span class="task-idx">{i+1}</span>
            <div style="flex:1">
                <div class="task-text">{pri}{t['text']}</div>
                <div class="task-meta">{done_note}</div>
            </div>
        </div>"""
    st.markdown(rows, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)

    # Action buttons
    for t in active:
        c1, c2 = st.columns([6, 1])
        label_text = t['text'][:50] + ("…" if len(t['text']) > 50 else "")
        with c1:
            if st.button(f"✓  {label_text}", key=f"done_{t['id']}"):
                db.mark_task_done(t["id"], t["recurring"])
                st.rerun()
        with c2:
            if st.button("✕", key=f"del_{t['id']}"):
                db.delete_task(t["id"])
                st.rerun()

    # Queue preview
    if queued:
        st.markdown('<div class="section-label">Coming up</div>', unsafe_allow_html=True)
        html = ""
        for t in queued:
            html += f"""
            <div class="queue-row">
                <span class="task-idx">·</span>
                <span class="task-text">{t['text']}</span>
            </div>"""
        st.markdown(html, unsafe_allow_html=True)


def _add_task_form(day_key):
    with st.expander("＋  Add task for today"):
        text = st.text_input("Task description", key=f"add_task_text_{day_key}", label_visibility="collapsed",
                             placeholder="What needs to get done?")
        c1, c2 = st.columns(2)
        with c1:
            priority = st.selectbox("Priority", [("High", 1), ("Medium", 2), ("Low", 3)],
                                    format_func=lambda x: x[0], key=f"add_task_pri_{day_key}")
        with c2:
            recurring = st.checkbox("Recurring (rotates)", value=True, key=f"add_task_rec_{day_key}")
        if st.button("Add task", key=f"add_task_btn_{day_key}"):
            if text.strip():
                db.add_task(text.strip(), day_key, priority=priority[1], recurring=recurring)
                st.success("Added.")
                st.rerun()
            else:
                st.warning("Please enter a task.")


# ── Monday — Academics ────────────────────────────────────────────────────────

# ── Monday config ─────────────────────────────────────────────────────────────

PATIENT_SHEET_ID  = "1Dx9yCdRlHAXDV0HqdhMLgQNlVKLSGBVURm6R-KufV6A"
PATIENT_SHEET_URL = "https://docs.google.com/spreadsheets/d/" + PATIENT_SHEET_ID + "/edit"

# All Monday tasks — rotate 3 per week
MONDAY_TASKS = [
    {"id": "m1",  "text": "Read IJO article",                          "tag": "read"},
    {"id": "m2",  "text": "Read JCRS abstract",                        "tag": "read"},
    {"id": "m3",  "text": "Read JRS abstract",                         "tag": "read"},
    {"id": "m4",  "text": "Read Newsletter",                           "tag": "read"},
    {"id": "m5",  "text": "Watch 1 surgical video",                    "tag": "learning"},
    {"id": "m6",  "text": "Add 1 patient to clinical case library",    "tag": "clinical"},
]

# Monthly tasks — first Monday of month
MONDAY_MONTHLY = [
    {"id": "m7",  "text": "Check BMC articles to review",              "tag": "review",  "freq": "monthly"},
    {"id": "m8",  "text": "Check IJ articles to review",               "tag": "review",  "freq": "monthly"},
    {"id": "m9",  "text": "Edit surgical video",                        "tag": "editing", "freq": "monthly"},
]

MONDAY_TAG_COLORS = {
    "read":     "#2D6A4F",
    "learning": "#1D4E89",
    "clinical": "#7B341E",
    "review":   "#4A235A",
    "editing":  "#B5451B",
}


def _is_first_monday_of_month(today):
    from datetime import timedelta
    if today.weekday() != 0:
        return False
    first_day = today.replace(day=1)
    days_until_monday = (0 - first_day.weekday()) % 7
    from datetime import timedelta
    first_monday = first_day + timedelta(days=days_until_monday)
    return today == first_monday


def _get_monday_tasks():
    from datetime import date
    today    = date.today()
    week_num = today.isocalendar()[1]

    # Pick 3 rotating tasks based on week number
    # Cycle through all 6 tasks, showing 3 at a time
    total = len(MONDAY_TASKS)
    idx   = (week_num * 3) % total
    rotating = [MONDAY_TASKS[i % total] for i in range(idx, idx + 3)]

    # Monthly tasks if first Monday
    monthly = []
    if _is_first_monday_of_month(today):
        monthly = MONDAY_MONTHLY

    return rotating + monthly


@st.cache_data(ttl=3600)
def _load_patients():
    """Fetch patient list from Google Sheet."""
    try:
        import requests, io
        import pandas as pd
        url = "https://docs.google.com/spreadsheets/d/" + PATIENT_SHEET_ID + "/export?format=csv&gid=0"
        r   = requests.get(url, timeout=10)
        r.raise_for_status()
        df  = pd.read_csv(io.StringIO(r.text))
        df.columns = [c.strip() for c in df.columns]
        return df.to_dict("records")
    except Exception:
        return []


def _get_this_week_patient():
    """
    Return the current patient. Stays until marked done.
    Uses week number as seed for consistent pick within the week.
    """
    from datetime import date
    import hashlib

    # Check if user has marked a patient done this week
    week_num  = date.today().isocalendar()[1]
    state_key = "patient_done_week_" + str(week_num)
    if st.session_state.get(state_key):
        return None, None  # Already done this week

    patients = _load_patients()
    if not patients:
        return None, None

    # Pick patient based on week number — consistent within week
    idx     = week_num % len(patients)
    patient = patients[idx]
    return patient, state_key


def render_monday(events):
    _page_header(0, "Academic & Research Day")
    _week_strip(0)
    _calendar_section(events)

    # ── Patient of the week ───────────────────────────────────────────────────
    patient, state_key = _get_this_week_patient()

    st.markdown('<div class="section-label">Patient of the Week</div>', unsafe_allow_html=True)
    if patient:
        name      = str(patient.get("Name", patient.get("Patient Name", "Unknown")))
        diagnosis = str(patient.get("Diagnosis", "")).strip()
        notes     = str(patient.get("Notes", "")).strip()

        diag_html  = '<div style="font-size:0.78rem;color:#888;margin-top:3px">' + diagnosis + '</div>' if diagnosis and diagnosis != "nan" else ""
        notes_html = '<div style="font-size:0.75rem;color:#AAA;margin-top:2px">' + notes + '</div>' if notes and notes != "nan" else ""

        col1, col2 = st.columns([12, 2])
        with col1:
            st.markdown(
                '<div style="background:#F5F0FF;border:1px solid #E0D5F5;border-radius:10px;'
                'padding:0.9rem 1.1rem;margin-bottom:1rem">'
                '<div style="font-size:0.65rem;font-weight:600;letter-spacing:0.15em;'
                'text-transform:uppercase;color:#4A235A;margin-bottom:3px">Add to case library</div>'
                '<div style="font-size:1.1rem;font-weight:600;color:#1A1A1A">' + name + '</div>'
                + diag_html + notes_html +
                '</div>',
                unsafe_allow_html=True
            )
        with col2:
            if st.button("✓ Done", key="patient_done_btn"):
                st.session_state[state_key] = True
                st.cache_data.clear()
                st.rerun()

        st.markdown(
            '<a href="' + PATIENT_SHEET_URL + '" target="_blank" '
            'style="font-size:0.78rem;color:#4A235A">Open patient sheet ↗</a>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="padding:0.6rem 0;font-size:0.88rem;color:#2D6A4F">'
            '✓ Patient added this week!</div>',
            unsafe_allow_html=True
        )

    # ── Monday Task Queue ─────────────────────────────────────────────────────
    st.markdown('<div class="section-label">This Week — Academic Tasks</div>', unsafe_allow_html=True)

    today_tasks = _get_monday_tasks()

    if "mon_done" not in st.session_state:
        st.session_state["mon_done"] = set()
    done_set = st.session_state["mon_done"]

    todo = [t for t in today_tasks if t["id"] not in done_set]
    done = [t for t in today_tasks if t["id"] in done_set]

    if todo:
        for item in todo:
            tag_color = MONDAY_TAG_COLORS.get(item["tag"], "#888")
            freq_note = " · monthly" if item.get("freq") else ""
            col1, col2 = st.columns([1, 16])
            with col1:
                if st.button("○", key="mchk_" + item["id"], help="Mark done"):
                    done_set.add(item["id"])
                    st.rerun()
            with col2:
                st.markdown(
                    '<div style="padding:0.45rem 0;border-bottom:1px solid #F0EFEC">'
                    '<div style="font-size:0.95rem;color:#1A1A1A">' + item["text"] + '</div>'
                    '<div style="font-size:0.65rem;color:' + tag_color + ';margin-top:2px">' + item["tag"] + freq_note + '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
    else:
        st.markdown(
            '<div style="padding:1rem 0;font-size:0.9rem;color:#2D6A4F">✓ All done for this Monday!</div>',
            unsafe_allow_html=True
        )

    if done:
        st.markdown('<div class="section-label" style="margin-top:1.5rem">Done</div>', unsafe_allow_html=True)
        for item in done:
            col1, col2 = st.columns([1, 16])
            with col1:
                if st.button("✓", key="mundo_" + item["id"], help="Undo"):
                    done_set.discard(item["id"])
                    st.rerun()
            with col2:
                st.markdown(
                    '<div style="padding:0.45rem 0;border-bottom:1px solid #F0EFEC;opacity:0.4">'
                    '<div style="font-size:0.95rem;color:#1A1A1A;text-decoration:line-through">' + item["text"] + '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
        if st.button("↺ Reset", key="mon_reset"):
            st.session_state["mon_done"] = set()
            st.rerun()

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    with st.expander("📋 Full Monday queue"):
        all_tasks = MONDAY_TASKS + MONDAY_MONTHLY
        for item in all_tasks:
            is_active = any(t["id"] == item["id"] for t in today_tasks)
            marker    = "▶  " if is_active else "·  "
            color     = "#1A1A1A" if is_active else "#BBB"
            freq      = " (monthly)" if item.get("freq") else ""
            st.markdown(
                '<div style="padding:0.4rem 0;border-bottom:1px solid #F5F5F3;'
                'font-size:0.88rem;color:' + color + '">'
                + marker + item["text"] + freq + '</div>',
                unsafe_allow_html=True
            )

    _add_task_form(0)



# ── Tuesday — Content ─────────────────────────────────────────────────────────

# ── Tuesday config ────────────────────────────────────────────────────────────

TUESDAY_TASKS = [
    {"id": "t1", "text": "Research content topics + update content calendar", "tag": "strategy"},
    {"id": "t2", "text": "Schedule content on YouTube",                        "tag": "publish"},
    {"id": "t3", "text": "Schedule content on Meta (Instagram/Facebook)",      "tag": "publish"},
    {"id": "t4", "text": "Script writing",                                     "tag": "create"},
    {"id": "t5", "text": "LinkedIn post",                                      "tag": "create"},
    {"id": "t6", "text": "Website blog",                                       "tag": "create"},
    {"id": "t7", "text": "Video editing (if time available)",                  "tag": "editing"},
    {"id": "t8", "text": "Thumbnails → carry to Thursday if needed",           "tag": "thursday"},
]

TUESDAY_TAG_COLORS = {
    "strategy": "#1D4E89",
    "publish":  "#2D6A4F",
    "create":   "#7B341E",
    "editing":  "#4A235A",
    "thursday": "#B5451B",
}


def _get_tuesday_tasks():
    from datetime import date
    today    = date.today()
    week_num = today.isocalendar()[1]
    total    = len(TUESDAY_TASKS)
    idx      = (week_num * 3) % total
    return [TUESDAY_TASKS[i % total] for i in range(idx, idx + 3)]


def render_tuesday(events):
    _page_header(1, "Content Engine Day")
    _week_strip(1)
    _calendar_section(events)

    # Quick capture banner
    st.markdown(
        '<div style="background:#EEF4FF;border:1px solid #C7D9F5;border-radius:10px;'
        'padding:0.9rem 1.1rem;margin-bottom:1.2rem">'
        '<div style="font-size:0.65rem;font-weight:600;letter-spacing:0.15em;'
        'text-transform:uppercase;color:#1D4E89;margin-bottom:6px">⚡ Quick Capture</div>'
        '<div style="font-size:0.8rem;color:#444">Got a content idea? Save it instantly.</div>'
        '</div>',
        unsafe_allow_html=True
    )

    cap_col1, cap_col2 = st.columns([5, 1])
    with cap_col1:
        idea = st.text_input("Capture", key="tue_cap", label_visibility="collapsed",
                             placeholder="New idea, script angle, thumbnail concept…")
    with cap_col2:
        ctype = st.selectbox("Type", ["idea", "script", "note"], key="tue_cap_type",
                             label_visibility="collapsed")
    if st.button("Save →", key="tue_cap_btn"):
        if idea.strip():
            db.add_capture(idea.strip(), ctype)
            st.success("Captured!")
            st.rerun()

    # Task queue
    st.markdown('<div class="section-label">This Week — Content Tasks</div>', unsafe_allow_html=True)

    today_tasks = _get_tuesday_tasks()

    from datetime import date as _date
    week_num = _date.today().isocalendar()[1]
    total    = len(TUESDAY_TASKS)
    next_idx = ((week_num + 1) * 3) % total
    next_tasks = [TUESDAY_TASKS[i % total]["text"][:30] for i in range(next_idx, next_idx + 3)]
    st.caption("Next week → " + " · ".join(next_tasks))

    if "tue_done" not in st.session_state:
        st.session_state["tue_done"] = set()
    done_set = st.session_state["tue_done"]

    todo = [t for t in today_tasks if t["id"] not in done_set]
    done = [t for t in today_tasks if t["id"] in done_set]

    if todo:
        for item in todo:
            tag_color = TUESDAY_TAG_COLORS.get(item["tag"], "#888")
            col1, col2 = st.columns([1, 16])
            with col1:
                if st.button("○", key="tchk_" + item["id"]):
                    done_set.add(item["id"])
                    st.rerun()
            with col2:
                st.markdown(
                    '<div style="padding:0.45rem 0;border-bottom:1px solid #F0EFEC">'
                    '<div style="font-size:0.95rem;color:#1A1A1A">' + item["text"] + '</div>'
                    '<div style="font-size:0.65rem;color:' + tag_color + ';margin-top:2px">' + item["tag"] + '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
    else:
        st.markdown(
            '<div style="padding:1rem 0;font-size:0.9rem;color:#2D6A4F">✓ All done for this Tuesday!</div>',
            unsafe_allow_html=True
        )

    if done:
        st.markdown('<div class="section-label" style="margin-top:1.5rem">Done</div>', unsafe_allow_html=True)
        for item in done:
            col1, col2 = st.columns([1, 16])
            with col1:
                if st.button("✓", key="tundo_" + item["id"]):
                    done_set.discard(item["id"])
                    st.rerun()
            with col2:
                st.markdown(
                    '<div style="padding:0.45rem 0;border-bottom:1px solid #F0EFEC;opacity:0.4">'
                    '<div style="font-size:0.95rem;color:#1A1A1A;text-decoration:line-through">' + item["text"] + '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )
        if st.button("↺ Reset", key="tue_reset"):
            st.session_state["tue_done"] = set()
            st.rerun()

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    with st.expander("📋 Full Tuesday queue"):
        for item in TUESDAY_TASKS:
            is_active = any(t["id"] == item["id"] for t in today_tasks)
            marker    = "▶  " if is_active else "·  "
            color     = "#1A1A1A" if is_active else "#BBB"
            st.markdown(
                '<div style="padding:0.4rem 0;border-bottom:1px solid #F5F5F3;'
                'font-size:0.88rem;color:' + color + '">'
                + marker + item["text"] + '</div>',
                unsafe_allow_html=True
            )

    _add_task_form(1)


def render_wednesday(events):
    _page_header(2, "Learning & Self-Help Day")
    _week_strip(2)
    _calendar_section(events)
    _task_section(2, "Today's focus")

    # Watch queue
    st.markdown('<div class="section-label">Watch Queue</div>', unsafe_allow_html=True)
    cats = ["all", "productivity", "psychology", "finance", "spirituality", "other"]
    cat_filter = st.selectbox("Category filter", cats, key="wq_cat", label_visibility="collapsed")
    items = db.get_watch_queue(category=cat_filter if cat_filter != "all" else None)

    # Show max 4 to avoid overwhelm
    shown = items[:4]
    if not shown:
        st.caption("Queue is empty — add videos below.")
    for item in shown:
        c1, c2, c3 = st.columns([7, 1, 1])
        with c1:
            url_html = f'<a href="{item["url"]}" target="_blank">{item["title"]}</a>' if item["url"] else item["title"]
            st.markdown(url_html, unsafe_allow_html=True)
            st.caption(item["category"])
        with c2:
            if st.button("✓", key=f"ww_{item['id']}"):
                db.mark_watched(item["id"])
                st.rerun()
        with c3:
            if st.button("✕", key=f"wd_{item['id']}"):
                db.delete_watch_item(item["id"])
                st.rerun()

    if len(items) > 4:
        st.caption(f"… and {len(items)-4} more in queue.")

    with st.expander("＋ Add to watch queue"):
        wt = st.text_input("Video title", key="wq_title", label_visibility="collapsed",
                           placeholder="Video title…")
        wu = st.text_input("URL (optional)", key="wq_url", label_visibility="collapsed",
                           placeholder="https://youtube.com/…")
        wc = st.selectbox("Category", ["productivity", "psychology", "finance", "spirituality", "other"],
                          key="wq_cat_add")
        if st.button("Add to queue", key="wq_add_btn"):
            if wt.strip():
                db.add_watch_item(wt.strip(), wu.strip(), wc)
                st.rerun()

    _add_task_form(2)


# ── Thursday — Video Editing ──────────────────────────────────────────────────

def render_thursday(events):
    _page_header(3, "Deep Work — Editing Only")
    _week_strip(3)

    # Thursday is distraction-free — no calendar clutter, just tasks + pipeline
    st.markdown('<div class="section-label">Editing Queue</div>', unsafe_allow_html=True)
    items = db.get_content(status=None)
    # Show only items not yet uploaded
    pipeline = [i for i in items if i["status"] != "uploaded"]

    if not pipeline:
        st.caption("No active projects in the pipeline.")
    for item in pipeline:
        status_cls = "status-" + item["status"]
        c1, c2, c3 = st.columns([6, 2, 1])
        with c1:
            st.markdown(f"**{item['title']}**")
            st.caption(item["type"])
        with c2:
            new_s = st.selectbox("", CONTENT_STATUSES,
                                 index=CONTENT_STATUSES.index(item["status"]),
                                 key=f"ep_{item['id']}", label_visibility="collapsed")
            if new_s != item["status"]:
                db.update_content_status(item["id"], new_s)
                st.rerun()
        with c3:
            if st.button("✕", key=f"ed_{item['id']}"):
                db.delete_content(item["id"])
                st.rerun()

    _task_section(3, "Editing checklist")
    _add_task_form(3)


# ── Friday — Finance ──────────────────────────────────────────────────────────

# Update these URLs to your actual links
EXCEL_SHEET_URL = sh.SHEET_URL   # pulled from sheets.py

# Friday checklist
# ── Friday task config ───────────────────────────────────────────────────────
# FIXED: shown every single Friday
FRIDAY_FIXED = [
    {"id": "f1", "text": "Check portfolio",        "tag": "portfolio"},
    {"id": "f2", "text": "Check Momentum portfolio","tag": "portfolio"},
]

# STOCK ROTATION LIST — 24 stocks, one per week
# FA + Investor Presentation both done for the same stock each Friday
FRIDAY_STOCKS = [
    # Active Holdings
    "BHEL", "NESTLEIND", "ABSLAMC", "PFC", "AARTIIND",
    "AUROPHARMA", "KIRLPNU", "BALRAMCHIN", "ADANIPORTS", "DATAPATTNS",
    "BHARATFORG",
    # Watchlist
    "HDFCBANK", "BAJAJFINSV", "BAJAJHFL", "BHARTIAIRTEL", "HCLTECH",
    "HINDALCO", "ICICIBANK", "LT", "LUPIN", "M&M",
    "NTPC", "RVNL", "SILVER",
]

# ROTATING: other non-stock tasks that still cycle
FRIDAY_ROTATING = [
    {"id": "f5", "text": "Check pledge margins — pledge more if available", "tag": "margins"},
    {"id": "f6", "text": "Check buy / sell signals",                        "tag": "signals"},
]

# PERIODIC: shown only on first Friday of the month (or quarter)
FRIDAY_PERIODIC = [
    {"id": "f7",  "text": "Pay credit card bills",       "tag": "bills", "freq": "first-friday-monthly",    "months": 1},
    {"id": "f9b", "text": "Pay Jio bill",                "tag": "bills", "freq": "first-friday-monthly",    "months": 1},
    {"id": "f9c", "text": "Pay VF bill",                 "tag": "bills", "freq": "first-friday-monthly",    "months": 1},
    {"id": "f9d", "text": "Pay GST",                     "tag": "bills", "freq": "first-friday-monthly",    "months": 1},
    {"id": "f8",  "text": "Society maintenance bill",    "tag": "bills", "freq": "first-friday-quarterly",  "months": 3},
]

FRIDAY_CHECKLIST = FRIDAY_FIXED + FRIDAY_ROTATING + FRIDAY_PERIODIC

TAG_COLORS = {
    "portfolio": "#1D4E89",
    "research":  "#7B341E",
    "margins":   "#2D6A4F",
    "signals":   "#4A235A",
    "bills":     "#5C5C5C",
}




def _get_friday_tasks():
    """
    Build today's 3-task Friday list:
    - 2 fixed (always)
    - 1 rotating (cycles through FRIDAY_ROTATING week by week)
    - Plus any periodic tasks that are due this week
    """
    from datetime import date
    import math

    today     = date.today()
    # Use ISO week number to determine which rotating task to show
    week_num  = today.isocalendar()[1]
    rot_index = week_num % len(FRIDAY_ROTATING)
    rotating  = [FRIDAY_ROTATING[rot_index]]

    # Check periodic tasks
    periodic_due = []
    for t in FRIDAY_PERIODIC:
        # Show in the first Friday of every N months
        # Simple check: show if current month % months == 0
        if today.month % t["months"] == 0:
            periodic_due.append(t)

    # Build final list: fixed + rotating + periodic (if due)
    tasks = FRIDAY_FIXED + rotating + periodic_due
    return tasks


def _is_first_friday_of_month(today):
    """Return True if today is the first Friday of the month."""
    from datetime import date, timedelta
    if today.weekday() != 4:  # 4 = Friday
        return False
    # First Friday = no Friday exists in same month before this date
    first_day = today.replace(day=1)
    # Find first Friday of month
    days_until_friday = (4 - first_day.weekday()) % 7
    first_friday = first_day + timedelta(days=days_until_friday)
    return today == first_friday


def _get_friday_tasks():
    from datetime import date
    today    = date.today()
    week_num = today.isocalendar()[1]

    # Stock of the week — cycles through 24 stocks
    stock_idx   = week_num % len(FRIDAY_STOCKS)
    this_stock  = FRIDAY_STOCKS[stock_idx]
    next_stock  = FRIDAY_STOCKS[(stock_idx + 1) % len(FRIDAY_STOCKS)]

    stock_tasks = [
        {"id": "f3", "text": "FA analysis — " + this_stock + " → save to Google Sheet", "tag": "research", "stock": this_stock},
        {"id": "f4", "text": "Investor Presentation — " + this_stock + " (latest results + concall)", "tag": "research", "stock": this_stock},
    ]

    # One other rotating task (pledge / buy-sell signals)
    rot_idx  = week_num % len(FRIDAY_ROTATING)
    rotating = [FRIDAY_ROTATING[rot_idx]]

    # Periodic bills — first Friday of month/quarter
    periodic_due = []
    is_first_fri = _is_first_friday_of_month(today)
    for t in FRIDAY_PERIODIC:
        if t["freq"] == "first-friday-monthly":
            if is_first_fri:
                periodic_due.append(t)
        elif t["freq"] == "first-friday-quarterly":
            if is_first_fri and today.month in [1, 4, 7, 10]:
                periodic_due.append(t)

    return FRIDAY_FIXED + stock_tasks + rotating + periodic_due, this_stock, next_stock


def render_friday(events):
    _page_header(4, "Finance & Markets Day")
    _week_strip(4)
    _calendar_section(events)

    if EXCEL_SHEET_URL:
        link_html = (
            '<a href="' + EXCEL_SHEET_URL + '" target="_blank" style="'
            'display:inline-block;padding:0.55rem 1rem;background:#FFF;'
            'border:1px solid #E2E0DC;border-radius:8px;text-decoration:none;'
            'color:#1A1A1A;font-size:0.85rem;margin-bottom:0.8rem">'
            '📋 Open Holdings Excel Sheet ↗</a>'
        )
        st.markdown(link_html, unsafe_allow_html=True)

    today_tasks, this_stock, next_stock = _get_friday_tasks()
    st.markdown('<div class="section-label">Friday</div>', unsafe_allow_html=True)
    stock_banner = '<div style="background:#FFF8F0;border:1px solid #F5E6D0;border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:1rem"><div style="font-size:0.65rem;font-weight:600;letter-spacing:0.15em;text-transform:uppercase;color:#B5451B;margin-bottom:3px">Stock of the week</div><div style="font-size:1.3rem;font-weight:600;color:#1A1A1A">' + this_stock + '</div><div style="font-size:0.72rem;color:#AAA;margin-top:2px">Next week: ' + next_stock + '</div></div>'
    st.markdown(stock_banner, unsafe_allow_html=True)

    if "fri_done" not in st.session_state:
        st.session_state["fri_done"] = set()
    done_set = st.session_state["fri_done"]

    todo = [t for t in today_tasks if t["id"] not in done_set]
    done = [t for t in today_tasks if t["id"] in done_set]

    if todo:
        for item in todo:
            tag_color = TAG_COLORS.get(item["tag"], "#888")
            freq_note = ""
            if item.get("freq") == "monthly":   freq_note = " · monthly"
            if item.get("freq") == "quarterly": freq_note = " · quarterly"
            col1, col2 = st.columns([1, 16])
            with col1:
                if st.button("○", key="chk_" + item["id"], help="Mark done"):
                    done_set.add(item["id"])
                    st.rerun()
            with col2:
                row = (
                    '<div style="padding:0.45rem 0;border-bottom:1px solid #F0EFEC">'
                    '<div style="font-size:0.95rem;color:#1A1A1A">' + item["text"] + '</div>'
                    '<div style="font-size:0.65rem;color:' + tag_color + ';margin-top:2px">' + item["tag"] + freq_note + '</div>'
                    '</div>'
                )
                st.markdown(row, unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:1rem 0;font-size:0.9rem;color:#2D6A4F">✓ All done for today!</div>', unsafe_allow_html=True)

    if done:
        st.markdown('<div class="section-label" style="margin-top:1.5rem">Done</div>', unsafe_allow_html=True)
        for item in done:
            col1, col2 = st.columns([1, 16])
            with col1:
                if st.button("✓", key="undo_" + item["id"], help="Undo"):
                    done_set.discard(item["id"])
                    st.rerun()
            with col2:
                row = (
                    '<div style="padding:0.45rem 0;border-bottom:1px solid #F0EFEC;opacity:0.4">'
                    '<div style="font-size:0.95rem;color:#1A1A1A;text-decoration:line-through">' + item["text"] + '</div>'
                    '</div>'
                )
                st.markdown(row, unsafe_allow_html=True)
        if st.button("↺ Reset", key="fri_reset"):
            st.session_state["fri_done"] = set()
            st.rerun()

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    with st.expander("📋 View full queue — all 9 tasks"):
        all_tasks = FRIDAY_FIXED + FRIDAY_ROTATING + FRIDAY_PERIODIC
        for item in all_tasks:
            is_active = any(t["id"] == item["id"] for t in today_tasks)
            marker    = "▶  " if is_active else "·  "
            freq      = " (" + item["freq"] + ")" if item.get("freq") else ""
            color     = "#1A1A1A" if is_active else "#BBB"
            st.markdown(
                '<div style="padding:0.4rem 0;border-bottom:1px solid #F5F5F3;'
                'font-size:0.88rem;color:' + color + '">'
                + marker + item["text"] + freq + '</div>',
                unsafe_allow_html=True
            )

    st.markdown('<div class="section-label">Portfolio & Watchlist</div>', unsafe_allow_html=True)
    tab_w, tab_h, tab_r = st.tabs(["Watchlist", "Holdings", "Research Notes"])

    for tab, ftype in zip([tab_w, tab_h, tab_r], ["watchlist", "holding", "research"]):
        with tab:
            items = db.get_finance(ftype=ftype)
            if not items:
                st.caption("Nothing here yet.")
            for item in items:
                c1, c2, c3 = st.columns([2, 6, 1])
                with c1:
                    st.markdown('<div class="ticker">' + item["ticker"] + '</div>', unsafe_allow_html=True)
                with c2:
                    st.caption(item["notes"] if item["notes"] else "—")
                with c3:
                    if st.button("✕", key="fd_" + str(item["id"])):
                        db.delete_finance(item["id"])
                        st.rerun()
            with st.expander("+ Add to " + ftype):
                ft = st.text_input("Ticker / name", key="fi_" + ftype,
                                   label_visibility="collapsed", placeholder="e.g. INFY, HDFC…")
                fn = st.text_input("Notes", key="fn_" + ftype,
                                   label_visibility="collapsed", placeholder="Investment thesis?")
                if st.button("Add", key="fadd_" + ftype):
                    if ft.strip():
                        db.add_finance(ft.strip(), ftype=ftype, notes=fn.strip())
                        st.rerun()

    _add_task_form(4)


def render_saturday(events):
    _page_header(5, "Light day — clear the backlog")
    _week_strip(5)
    _calendar_section(events)

    # Carried forward tasks from previous days
    carried = db.get_carried_tasks()
    if carried:
        st.markdown('<div class="section-label">Carried forward</div>', unsafe_allow_html=True)
        rows = ""
        for t in carried:
            rows += f"""
            <div class="task-row">
                <span class="task-idx">↩</span>
                <div class="task-text">{t['text']}</div>
            </div>"""
        st.markdown(rows, unsafe_allow_html=True)
        st.markdown("<div style='margin-top:0.5rem'></div>", unsafe_allow_html=True)
        for t in carried:
            c1, c2 = st.columns([6, 1])
            with c1:
                if st.button(f"✓  {t['text'][:50]}", key=f"car_done_{t['id']}"):
                    db.mark_task_done(t["id"], t["recurring"])
                    st.rerun()
            with c2:
                if st.button("✕", key=f"car_del_{t['id']}"):
                    db.delete_task(t["id"])
                    st.rerun()

    _task_section(5, "Saturday tasks")
    _add_task_form(5)

    # Pending captures
    caps = db.get_captures(processed=False)
    if caps:
        st.markdown('<div class="section-label">Unprocessed captures</div>', unsafe_allow_html=True)
        for c in caps:
            c1, c2, c3 = st.columns([6, 1, 1])
            with c1:
                st.markdown(f"{c['text']} &nbsp;<span style='font-size:0.65rem;color:#AAA'>{c['type']}</span>",
                            unsafe_allow_html=True)
                st.caption(c["created_at"])
            with c2:
                if st.button("✓", key=f"cap_p_{c['id']}"):
                    db.process_capture(c["id"])
                    st.rerun()
            with c3:
                if st.button("✕", key=f"cap_d_{c['id']}"):
                    db.delete_capture(c["id"])
                    st.rerun()


# ── Sunday — Personal / Shoot Day ────────────────────────────────────────────

def render_sunday(events):
    from modules.database import get_shoot_day
    today_str = date.today().isoformat()
    shoot_day = get_shoot_day()
    is_shoot_day = (shoot_day == today_str)

    if is_shoot_day:
        _page_header(6, "🎥 SHOOT DAY")
        _week_strip(6)
        st.markdown('<div class="section-label">Shoot Day Checklist</div>', unsafe_allow_html=True)
        shoot_items = [
            "Scripts printed / loaded on tablet",
            "Camera battery charged",
            "SD cards formatted and ready",
            "Lighting setup done",
            "Background / set ready",
            "Intro + outro planned",
            "Thumbnail concept ready",
            "Recording schedule set",
        ]
        for item in shoot_items:
            st.checkbox(item, key=f"shoot_{item}")

        st.markdown('<div class="section-label">Scripts to shoot today</div>', unsafe_allow_html=True)
        scripted = db.get_content(status="scripting")
        if not scripted:
            st.caption("No scripts marked 'scripting' in pipeline.")
        for s in scripted:
            st.markdown(f"— {s['title']} &nbsp; `{s['type']}`", unsafe_allow_html=True)

    else:
        _page_header(6, "Personal & Rest Day")
        _week_strip(6)
        _calendar_section(events)
        _task_section(6, "Personal time")

        # Shoot day config
        with st.expander("📅 Set this month's Shoot Day"):
            shoot = db.get_shoot_day()
            st.caption(f"Current shoot day: **{shoot}**" if shoot else "Not set yet.")
            new_shoot = st.date_input("Pick shoot day", key="shoot_date_picker")
            if st.button("Set shoot day", key="set_shoot_btn"):
                db.set_shoot_day(str(new_shoot))
                st.success(f"Shoot day set to {new_shoot}")
                st.rerun()

    _add_task_form(6)
