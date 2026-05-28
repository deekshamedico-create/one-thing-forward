"""
day_views.py — Renders the unique dashboard for each weekday.
Each function receives (data_module, calendar_events).
"""

import streamlit as st
from datetime import date
from modules import database as db
from modules.styles import DAY_CONFIG, DAY_COLORS, CONTENT_STATUSES

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
    if not events:
        st.caption("No Google Calendar events today — or calendar not connected.")
        return
    html = ""
    for e in events:
        loc = f'<div class="cal-location">📍 {e["location"]}</div>' if e.get("location") else ""
        html += f"""
        <div class="cal-event">
            <div class="cal-time">{e['start_time']}</div>
            <div>
                <div class="cal-title">{e['title']}</div>
                {loc}
            </div>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)


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

def render_monday(events):
    _page_header(0, "Academic & Research Day")
    _week_strip(0)
    _calendar_section(events)
    _task_section(0, "Academic focus")
    _add_task_form(0)


# ── Tuesday — Content ─────────────────────────────────────────────────────────

def render_tuesday(events):
    _page_header(1, "Content Engine Day")
    _week_strip(1)
    _calendar_section(events)

    # Quick capture banner
    st.markdown("""
    <div class="capture-banner">
        <h4>⚡ Quick Capture</h4>
        <p>Got an idea? Drop it here. Organise later.</p>
    </div>
    """, unsafe_allow_html=True)

    cap_col1, cap_col2 = st.columns([5, 1])
    with cap_col1:
        idea = st.text_input("Capture an idea", key="quick_cap", label_visibility="collapsed",
                             placeholder="New content idea, script angle, thumbnail concept…")
    with cap_col2:
        ctype = st.selectbox("Type", ["idea", "script", "note", "content"], key="quick_cap_type",
                             label_visibility="collapsed")
    if st.button("Save →", key="quick_cap_btn"):
        if idea.strip():
            db.add_capture(idea.strip(), ctype)
            st.success("Captured!")
            st.rerun()

    _task_section(1, "Content tasks")

    # Content pipeline summary
    st.markdown('<div class="section-label">Content Pipeline</div>', unsafe_allow_html=True)
    tab_r, tab_y, tab_l = st.tabs(["Reels", "YouTube", "LinkedIn"])
    for tab, ctype in zip([tab_r, tab_y, tab_l], ["reel", "youtube", "linkedin"]):
        with tab:
            items = db.get_content(ctype=ctype)
            if not items:
                st.caption("Nothing here yet.")
            for item in items:
                status_cls = f"status-{item['status']}"
                c1, c2, c3 = st.columns([6, 2, 1])
                with c1:
                    st.markdown(item["title"])
                with c2:
                    new_status = st.selectbox(
                        "", CONTENT_STATUSES,
                        index=CONTENT_STATUSES.index(item["status"]),
                        key=f"cs_{item['id']}",
                        label_visibility="collapsed"
                    )
                    if new_status != item["status"]:
                        db.update_content_status(item["id"], new_status)
                        st.rerun()
                with c3:
                    if st.button("✕", key=f"cd_{item['id']}"):
                        db.delete_content(item["id"])
                        st.rerun()

            with st.expander(f"＋ Add {ctype} idea"):
                t = st.text_input("Title / concept", key=f"ci_{ctype}", label_visibility="collapsed",
                                  placeholder="Content title…")
                n = st.text_input("Notes (optional)", key=f"cn_{ctype}", label_visibility="collapsed",
                                  placeholder="Notes…")
                if st.button(f"Add", key=f"cadd_{ctype}"):
                    if t.strip():
                        db.add_content(t.strip(), ctype=ctype, notes=n.strip())
                        st.rerun()

    _add_task_form(1)


# ── Wednesday — Self Help ─────────────────────────────────────────────────────

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

def render_friday(events):
    _page_header(4, "Finance & Markets Day")
    _week_strip(4)
    _calendar_section(events)
    _task_section(4, "Finance checklist")

    st.markdown('<div class="section-label">Portfolio & Watchlist</div>', unsafe_allow_html=True)
    tab_w, tab_h, tab_r = st.tabs(["Watchlist", "Holdings", "Research"])

    for tab, ftype in zip([tab_w, tab_h, tab_r], ["watchlist", "holding", "research"]):
        with tab:
            items = db.get_finance(ftype=ftype)
            if not items:
                st.caption("Nothing here yet.")
            for item in items:
                c1, c2, c3 = st.columns([2, 5, 1])
                with c1:
                    st.markdown(f'<div class="ticker">{item["ticker"]}</div>', unsafe_allow_html=True)
                with c2:
                    st.caption(item["notes"] if item["notes"] else "—")
                with c3:
                    if st.button("✕", key=f"fd_{item['id']}"):
                        db.delete_finance(item["id"])
                        st.rerun()

            with st.expander(f"＋ Add to {ftype}"):
                ft = st.text_input("Ticker / name", key=f"fi_{ftype}", label_visibility="collapsed",
                                   placeholder="e.g. INFY, HDFC, Gold…")
                fn = st.text_input("Notes", key=f"fn_{ftype}", label_visibility="collapsed",
                                   placeholder="Why watching? Thesis?")
                if st.button("Add", key=f"fadd_{ftype}"):
                    if ft.strip():
                        db.add_finance(ft.strip(), ftype=ftype, notes=fn.strip())
                        st.rerun()

    _add_task_form(4)


# ── Saturday — Flex / Catch-up ────────────────────────────────────────────────

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
