"""
app.py — One Thing Forward: Personal Life OS
Run with: streamlit run app.py
"""

import streamlit as st
from datetime import date, datetime

from modules.database import init_db, get_conn
from modules.styles import get_css, DAY_CONFIG
from modules.calendar_api import get_today_events
from modules import day_views as dv

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="One Thing Forward",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Auto-refresh every 60s to keep clock live ─────────────────────────────────
st.markdown("""
<script>
setTimeout(function(){ window.location.reload(); }, 60000);
</script>
""", unsafe_allow_html=True)

# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()

# ── Today ─────────────────────────────────────────────────────────────────────
today_key = date.today().weekday()
day_info  = DAY_CONFIG[today_key]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(get_css(today_key), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem 0;'>
        <div style='font-family: Lora, serif; font-size: 1.3rem; font-weight: 600; color: #1A1A1A;'>
            One Thing Forward
        </div>
        <div style='font-size: 0.72rem; color: #AAA; margin-top: 4px;'>
            Your personal life OS
        </div>
    </div>
    <hr style='margin: 0.8rem 0;'>
    """, unsafe_allow_html=True)

    # Fresh time on every rerun
    now = datetime.now()
    st.markdown(f"""
    <div style='font-size: 0.78rem; color: #888; margin-bottom: 1rem; line-height: 1.7;'>
        <div>{now.strftime('%A, %d %B %Y')}</div>
        <div style='font-size: 1rem; font-weight: 500; color: #1A1A1A;'>{now.strftime('%I:%M %p')}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Navigate**")
    page = st.radio(
        "",
        options=[
            "📅  Today",
            "📋  All Tasks",
            "💡  Captures",
            "🎬  Content Pipeline",
            "📈  Finance",
            "📺  Watch Queue",
            "⚙️  Settings",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)

    st.markdown("**Preview another day**")
    override_day = st.selectbox(
        "",
        options=[f"{DAY_CONFIG[i]['emoji']} {DAY_CONFIG[i]['name']}" for i in range(7)],
        index=today_key,
        label_visibility="collapsed",
        key="day_override",
    )
    view_day = [DAY_CONFIG[i]["name"] for i in range(7)].index(override_day.split(" ", 1)[1])

    # ── Reset DB tasks (clears seeded tasks so new defaults load) ─────────────
    st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
    with st.expander("⚙️ Database"):
        st.caption("Reset tasks if you see old default tasks.")
        if st.button("🔄 Reset default tasks", key="reset_tasks"):
            conn = get_conn()
            conn.execute("DELETE FROM tasks")
            conn.commit()
            conn.close()
            from modules.database import _seed_default_tasks
            _seed_default_tasks()
            st.success("Tasks reset! Reload the page.")
            st.rerun()

# ── Calendar (cached 5 min) ───────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_calendar():
    return get_today_events()

events = load_calendar()

# ── Route pages ───────────────────────────────────────────────────────────────
if "Today" in page:
    renderers = {
        0: dv.render_monday,
        1: dv.render_tuesday,
        2: dv.render_wednesday,
        3: dv.render_thursday,
        4: dv.render_friday,
        5: dv.render_saturday,
        6: dv.render_sunday,
    }
    renderers[view_day](events)

elif "All Tasks" in page:
    st.markdown('<div class="page-header"><div class="page-title">All Tasks</div><div class="accent-rule"></div></div>', unsafe_allow_html=True)
    from modules.database import get_tasks, delete_task
    for day_idx, cfg in DAY_CONFIG.items():
        tasks = get_tasks(day_key=day_idx, status="pending")
        label = f"{cfg['emoji']}  {cfg['name']}  —  {cfg['category']}"
        if day_idx == today_key:
            label += "  ◀ today"
        with st.expander(label, expanded=(day_idx == today_key)):
            if not tasks:
                st.caption("No tasks.")
            for i, t in enumerate(tasks):
                c1, c2 = st.columns([10, 1])
                with c1:
                    w = "**" if i < 3 else ""
                    flag = " *(once)*" if not t["recurring"] else ""
                    done = f" *(done {t['done_count']}×)*" if t["done_count"] > 0 else ""
                    st.markdown(f"{i+1}. {w}{t['text']}{w}{flag}{done}")
                with c2:
                    if st.button("✕", key=f"at_del_{t['id']}"):
                        delete_task(t["id"])
                        st.rerun()

elif "Captures" in page:
    st.markdown('<div class="page-header"><div class="page-title">💡 Quick Captures</div><div class="accent-rule"></div></div>', unsafe_allow_html=True)
    from modules.database import get_captures, process_capture, delete_capture, add_capture
    with st.expander("＋ New capture", expanded=True):
        ct = st.text_area("What's on your mind?", key="new_cap_text", label_visibility="collapsed",
                          placeholder="Idea, thought, task, content concept…", height=80)
        ctype = st.selectbox("Type", ["idea", "note", "task", "content"], key="new_cap_type")
        if st.button("Save capture →", key="save_cap"):
            if ct.strip():
                add_capture(ct.strip(), ctype)
                st.success("Saved!")
                st.rerun()
    captures = get_captures(processed=False)
    st.markdown(f'<div class="section-label">Inbox — {len(captures)} item(s)</div>', unsafe_allow_html=True)
    if not captures:
        st.caption("Inbox is clear.")
    for c in captures:
        with st.expander(f"{c['text'][:60]}…" if len(c['text']) > 60 else c['text']):
            st.markdown(c["text"])
            st.caption(f"Type: {c['type']}  ·  {c['created_at']}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Mark processed", key=f"cp_{c['id']}"):
                    process_capture(c["id"])
                    st.rerun()
            with col2:
                if st.button("Delete", key=f"cdel_{c['id']}"):
                    delete_capture(c["id"])
                    st.rerun()

elif "Content Pipeline" in page:
    st.markdown('<div class="page-header"><div class="page-title">🎬 Content Pipeline</div><div class="accent-rule"></div></div>', unsafe_allow_html=True)
    from modules.database import get_content, add_content, update_content_status, delete_content
    from modules.styles import CONTENT_STATUSES, CONTENT_TYPES
    with st.expander("＋ Add content item"):
        ct_title = st.text_input("Title", key="cp_title", label_visibility="collapsed",
                                 placeholder="Video / reel / post title…")
        ct_col1, ct_col2 = st.columns(2)
        with ct_col1:
            ct_type = st.selectbox("Type", CONTENT_TYPES, key="cp_type")
        with ct_col2:
            ct_status = st.selectbox("Status", CONTENT_STATUSES, key="cp_status")
        ct_notes = st.text_input("Notes", key="cp_notes", label_visibility="collapsed", placeholder="Notes…")
        if st.button("Add", key="cp_add"):
            if ct_title.strip():
                add_content(ct_title.strip(), ct_type, ct_notes.strip())
                st.rerun()
    for status in CONTENT_STATUSES:
        items = get_content(status=status)
        if not items:
            continue
        st.markdown(f'<div class="section-label">{status.upper()} — {len(items)}</div>', unsafe_allow_html=True)
        for item in items:
            c1, c2, c3 = st.columns([6, 2, 1])
            with c1:
                st.markdown(f"**{item['title']}** &nbsp; `{item['type']}`", unsafe_allow_html=True)
                if item["notes"]:
                    st.caption(item["notes"])
            with c2:
                new_s = st.selectbox("", CONTENT_STATUSES,
                                     index=CONTENT_STATUSES.index(item["status"]),
                                     key=f"pipe_{item['id']}", label_visibility="collapsed")
                if new_s != item["status"]:
                    update_content_status(item["id"], new_s)
                    st.rerun()
            with c3:
                if st.button("✕", key=f"pipe_del_{item['id']}"):
                    delete_content(item["id"])
                    st.rerun()

elif "Finance" in page:
    st.markdown('<div class="page-header"><div class="page-title">📈 Finance & Markets</div><div class="accent-rule"></div></div>', unsafe_allow_html=True)
    from modules.database import get_finance, add_finance, delete_finance
    from modules.styles import FINANCE_TYPES
    tab_w, tab_h, tab_r = st.tabs(["Watchlist", "Holdings", "Research"])
    for tab, ftype in zip([tab_w, tab_h, tab_r], FINANCE_TYPES):
        with tab:
            items = get_finance(ftype=ftype)
            if not items:
                st.caption("Nothing here yet.")
            for item in items:
                c1, c2, c3 = st.columns([2, 6, 1])
                with c1:
                    st.markdown(f"**{item['ticker']}**")
                with c2:
                    st.caption(item["notes"] if item["notes"] else "—")
                with c3:
                    if st.button("✕", key=f"fin_{item['id']}"):
                        delete_finance(item["id"])
                        st.rerun()
            with st.expander(f"＋ Add to {ftype}"):
                ft = st.text_input("Ticker", key=f"fadd_t_{ftype}", label_visibility="collapsed",
                                   placeholder="e.g. INFY, HDFC, Gold")
                fn = st.text_input("Notes / thesis", key=f"fadd_n_{ftype}", label_visibility="collapsed",
                                   placeholder="Why watching?")
                if st.button("Add", key=f"fadd_btn_{ftype}"):
                    if ft.strip():
                        add_finance(ft.strip(), ftype=ftype, notes=fn.strip())
                        st.rerun()

elif "Watch Queue" in page:
    st.markdown('<div class="page-header"><div class="page-title">📺 Watch Queue</div><div class="accent-rule"></div></div>', unsafe_allow_html=True)
    from modules.database import get_watch_queue, add_watch_item, mark_watched, delete_watch_item
    from modules.styles import WATCH_CATEGORIES
    with st.expander("＋ Add video"):
        wt = st.text_input("Title", key="wq_add_t", label_visibility="collapsed", placeholder="Video title…")
        wu = st.text_input("URL", key="wq_add_u", label_visibility="collapsed", placeholder="https://…")
        wc = st.selectbox("Category", [c for c in WATCH_CATEGORIES if c != "all"], key="wq_add_c")
        if st.button("Add to queue", key="wq_main_add"):
            if wt.strip():
                add_watch_item(wt.strip(), wu.strip(), wc)
                st.rerun()
    cat_f = st.selectbox("Filter by category", WATCH_CATEGORIES, key="wq_main_filter")
    items = get_watch_queue(category=cat_f if cat_f != "all" else None)
    st.markdown(f'<div class="section-label">To watch — {len(items)}</div>', unsafe_allow_html=True)
    if not items:
        st.caption("Queue is empty.")
    for item in items:
        c1, c2, c3 = st.columns([7, 1, 1])
        with c1:
            if item["url"]:
                st.markdown(f'<a href="{item["url"]}" target="_blank">{item["title"]}</a>', unsafe_allow_html=True)
            else:
                st.markdown(item["title"])
            st.caption(item["category"])
        with c2:
            if st.button("✓", key=f"wmain_{item['id']}"):
                mark_watched(item["id"])
                st.rerun()
        with c3:
            if st.button("✕", key=f"wdmain_{item['id']}"):
                delete_watch_item(item["id"])
                st.rerun()

elif "Settings" in page:
    st.markdown('<div class="page-header"><div class="page-title">⚙️ Settings</div><div class="accent-rule"></div></div>', unsafe_allow_html=True)
    st.markdown("#### Google Calendar")
    st.info("""
**Setup steps:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project → enable **Google Calendar API**
3. Create **OAuth 2.0 credentials** (Desktop app) → download as `credentials.json`
4. Place `credentials.json` in the project root folder
5. Restart the app — a browser window will open for sign-in
6. After signing in, `token.json` is created automatically
    """)
    st.markdown("#### Shoot Day")
    from modules.database import get_shoot_day, set_shoot_day
    shoot = get_shoot_day()
    st.caption(f"This month's shoot day: **{shoot}**" if shoot else "Not set for this month.")
    new_shoot = st.date_input("Set shoot day", key="settings_shoot")
    if st.button("Save shoot day"):
        set_shoot_day(str(new_shoot))
        st.success(f"Shoot day set: {new_shoot}")
