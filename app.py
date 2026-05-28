import streamlit as st
import json
import os
from datetime import date

# ── Config ────────────────────────────────────────────────────────────────────
TASKS_FILE = "tasks.json"

DAY_CONFIG = {
    0: {"name": "Monday",    "category": "Academics",                "emoji": "📚", "color": "#2D6A4F"},
    1: {"name": "Tuesday",   "category": "Content Engine",           "emoji": "🎬", "color": "#1D4E89"},
    2: {"name": "Wednesday", "category": "Self Help & Growth",       "emoji": "🌱", "color": "#6B4226"},
    3: {"name": "Thursday",  "category": "Video Editing",            "emoji": "✂️",  "color": "#7B2D8B"},
    4: {"name": "Friday",    "category": "Finance & Stock Analysis", "emoji": "📈", "color": "#B5451B"},
    5: {"name": "Saturday",  "category": "Pending / Catch-up",       "emoji": "🔁", "color": "#5C5C5C"},
    6: {"name": "Sunday",    "category": "Rest & Review",            "emoji": "☀️", "color": "#8B6914"},
}

TASKS_PER_DAY = 3

# ── Data ──────────────────────────────────────────────────────────────────────
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return default_tasks()
    with open(TASKS_FILE, "r") as f:
        return json.load(f)

def save_tasks(data):
    with open(TASKS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def default_tasks():
    return {
        "0": [
            {"id": 1,  "text": "Review lecture notes / textbook chapter", "done_count": 0, "retire": False},
            {"id": 2,  "text": "Solve practice problems (30 min)",         "done_count": 0, "retire": False},
            {"id": 3,  "text": "Watch one educational video / lecture",    "done_count": 0, "retire": False},
            {"id": 4,  "text": "Update study schedule & goals",            "done_count": 0, "retire": False},
        ],
        "1": [
            {"id": 10, "text": "Plan next 3 content ideas",                "done_count": 0, "retire": False},
            {"id": 11, "text": "Write / draft one script or outline",      "done_count": 0, "retire": False},
            {"id": 12, "text": "Schedule / batch social posts",            "done_count": 0, "retire": False},
            {"id": 13, "text": "Review analytics & engagement",            "done_count": 0, "retire": False},
        ],
        "2": [
            {"id": 20, "text": "Read 20 pages of a self-help book",        "done_count": 0, "retire": False},
            {"id": 21, "text": "Journaling: weekly reflection (15 min)",   "done_count": 0, "retire": False},
            {"id": 22, "text": "Physical activity / workout",              "done_count": 0, "retire": False},
            {"id": 23, "text": "Meditation or breathwork (10 min)",        "done_count": 0, "retire": False},
        ],
        "3": [
            {"id": 30, "text": "Cut & edit raw footage",                   "done_count": 0, "retire": False},
            {"id": 31, "text": "Add transitions, text overlays, music",    "done_count": 0, "retire": False},
            {"id": 32, "text": "Export & review final cut",                "done_count": 0, "retire": False},
            {"id": 33, "text": "Organise project files & backups",         "done_count": 0, "retire": False},
        ],
        "4": [
            {"id": 40, "text": "Review portfolio performance",             "done_count": 0, "retire": False},
            {"id": 41, "text": "Read 2 financial news articles",           "done_count": 0, "retire": False},
            {"id": 42, "text": "Log weekly expenses & budget check",       "done_count": 0, "retire": False},
            {"id": 43, "text": "Research one stock / sector deep-dive",    "done_count": 0, "retire": False},
        ],
        "5": [
            {"id": 50, "text": "Clear anything left from the week",        "done_count": 0, "retire": False},
            {"id": 51, "text": "Reply to pending messages / emails",       "done_count": 0, "retire": False},
            {"id": 52, "text": "Plan next week's priorities",              "done_count": 0, "retire": False},
        ],
        "6": [
            {"id": 60, "text": "Weekly review: what went well?",           "done_count": 0, "retire": False},
            {"id": 61, "text": "Recharge: walk, movie, family time",       "done_count": 0, "retire": False},
            {"id": 62, "text": "Prep workspace for Monday",                "done_count": 0, "retire": False},
        ],
        "_next_id": 100,
    }

def get_today_key():
    return str(date.today().weekday())

def get_next_id(data):
    nid = data.get("_next_id", 100)
    data["_next_id"] = nid + 1
    return nid

# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500&display=swap');

    /* ── Reset & base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background-color: #FAFAF8 !important;
        color: #1A1A1A !important;
    }

    /* Remove Streamlit default top padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
        max-width: 680px !important;
    }

    /* ── Header ── */
    .otf-header {
        padding: 3rem 0 2rem 0;
        text-align: left;
    }
    .otf-eyebrow {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #999;
        margin-bottom: 0.5rem;
    }
    .otf-title {
        font-family: 'Lora', serif;
        font-size: 2.4rem;
        font-weight: 600;
        color: #1A1A1A;
        line-height: 1.15;
        margin: 0 0 0.3rem 0;
    }
    .otf-date {
        font-size: 0.8rem;
        color: #AAA;
        font-weight: 300;
    }
    .otf-accent {
        height: 2px;
        width: 40px;
        border-radius: 2px;
        margin: 1.5rem 0 0 0;
    }

    /* ── Week strip ── */
    .week-strip {
        display: flex;
        gap: 6px;
        margin: 2rem 0 2.5rem 0;
    }
    .day-chip {
        flex: 1;
        text-align: center;
        padding: 0.55rem 0.2rem;
        border-radius: 10px;
        background: #F0EFEC;
        border: 1.5px solid transparent;
    }
    .day-chip.today {
        background: #1A1A1A;
        border-color: #1A1A1A;
    }
    .day-chip-emoji {
        font-size: 1.05rem;
        display: block;
        margin-bottom: 3px;
    }
    .day-chip-label {
        font-size: 0.55rem;
        font-weight: 500;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #999;
        display: block;
    }
    .day-chip.today .day-chip-label {
        color: #FFF;
    }

    /* ── Section label ── */
    .section-label {
        font-size: 0.65rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #BBB;
        margin: 2rem 0 1rem 0;
    }

    /* ── Task row ── */
    .task-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.1rem 0;
        border-bottom: 1px solid #EBEBEB;
    }
    .task-row:first-of-type {
        border-top: 1px solid #EBEBEB;
    }
    .task-index {
        font-family: 'Lora', serif;
        font-size: 1.1rem;
        color: #DDD;
        min-width: 1.5rem;
        font-style: italic;
    }
    .task-body {
        flex: 1;
    }
    .task-text {
        font-size: 1rem;
        font-weight: 400;
        color: #1A1A1A;
        line-height: 1.45;
    }
    .task-meta {
        font-size: 0.7rem;
        color: #BBB;
        margin-top: 2px;
    }
    .once-badge {
        display: inline-block;
        font-size: 0.6rem;
        font-weight: 500;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #C0392B;
        background: #FDF0EF;
        border-radius: 4px;
        padding: 1px 6px;
    }

    /* ── Queue preview ── */
    .queue-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.7rem 0;
        border-bottom: 1px solid #F5F5F3;
        opacity: 0.45;
    }

    /* ── Buttons ── */
    div[data-testid="stButton"] > button {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 400 !important;
        color: #555 !important;
        background: #FFF !important;
        border: 1px solid #E5E5E5 !important;
        border-radius: 8px !important;
        padding: 0.4rem 0.9rem !important;
        transition: all 0.15s ease !important;
        width: 100% !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: #F5F5F3 !important;
        border-color: #CCC !important;
        color: #1A1A1A !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid #E8E8E6 !important;
        gap: 0 !important;
        margin-bottom: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        color: #AAA !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
        padding: 0.6rem 1.2rem !important;
        margin-right: 0.5rem !important;
    }
    .stTabs [aria-selected="true"] {
        color: #1A1A1A !important;
        border-bottom: 2px solid #1A1A1A !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 0 !important;
    }

    /* ── Inputs ── */
    .stTextInput > label, .stSelectbox > label, .stCheckbox > label span {
        font-size: 0.8rem !important;
        font-weight: 400 !important;
        color: #666 !important;
        letter-spacing: 0.03em !important;
    }
    .stTextInput input {
        background: #FFF !important;
        border: 1px solid #E0E0DC !important;
        border-radius: 8px !important;
        color: #1A1A1A !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.6rem 0.9rem !important;
    }
    .stTextInput input:focus {
        border-color: #999 !important;
        box-shadow: none !important;
    }
    div[data-baseweb="select"] > div {
        background: #FFF !important;
        border: 1px solid #E0E0DC !important;
        border-radius: 8px !important;
        color: #1A1A1A !important;
        font-size: 0.9rem !important;
    }
    .stCheckbox label span {
        color: #444 !important;
        font-size: 0.88rem !important;
    }

    /* ── Expander (week view) ── */
    details {
        border: 1px solid #EBEBEB !important;
        border-radius: 10px !important;
        background: #FFF !important;
        margin-bottom: 0.5rem !important;
    }
    summary {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #1A1A1A !important;
        padding: 0.85rem 1rem !important;
    }
    .stExpander > details > div {
        padding: 0 1rem 1rem 1rem !important;
    }

    /* ── Misc ── */
    .stAlert {
        border-radius: 8px !important;
        font-size: 0.88rem !important;
    }
    p, .stMarkdown p {
        color: #1A1A1A !important;
    }
    .stCaption, .stMarkdown small {
        color: #999 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ── Views ─────────────────────────────────────────────────────────────────────
def view_today(data):
    today_key = get_today_key()
    day_info  = DAY_CONFIG[int(today_key)]
    all_tasks = data.get(today_key, [])
    active    = all_tasks[:TASKS_PER_DAY]
    queued    = all_tasks[TASKS_PER_DAY:]

    # Header
    st.markdown(f"""
    <div class="otf-header">
        <div class="otf-eyebrow">{day_info['name']}</div>
        <div class="otf-title">{day_info['emoji']}&nbsp;{day_info['category']}</div>
        <div class="otf-date">{date.today().strftime('%A, %d %B %Y')}</div>
        <div class="otf-accent" style="background:{day_info['color']}"></div>
    </div>
    """, unsafe_allow_html=True)

    # Week strip
    strip = '<div class="week-strip">'
    for i, cfg in DAY_CONFIG.items():
        cls = "day-chip today" if i == int(today_key) else "day-chip"
        strip += (f'<div class="{cls}">'
                  f'<span class="day-chip-emoji">{cfg["emoji"]}</span>'
                  f'<span class="day-chip-label">{cfg["name"][:3]}</span>'
                  f'</div>')
    strip += '</div>'
    st.markdown(strip, unsafe_allow_html=True)

    # Active tasks
    st.markdown('<div class="section-label">Focus — up to 3 tasks</div>', unsafe_allow_html=True)

    if not active:
        st.info("No tasks yet for today. Add some in the **Add Task** tab.")
    else:
        rows_html = ""
        for i, task in enumerate(active):
            badge = '<span class="once-badge">once</span>&nbsp;' if task.get("retire") else ""
            done_note = f'Done {task["done_count"]}×' if task["done_count"] > 0 else "Recurring"
            rows_html += f"""
            <div class="task-row">
                <span class="task-index">{i+1}</span>
                <div class="task-body">
                    <div class="task-text">{badge}{task['text']}</div>
                    <div class="task-meta">{done_note}</div>
                </div>
            </div>"""
        st.markdown(rows_html, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        for task in active:
            c1, c2 = st.columns([5, 1])
            with c1:
                if st.button(f"✓  Done  ·  {task['text'][:42]}{'…' if len(task['text'])>42 else ''}", key=f"done_{task['id']}"):
                    mark_done(data, today_key, task["id"])
                    st.rerun()
            with c2:
                if st.button("✕", key=f"del_{task['id']}"):
                    delete_task(data, today_key, task["id"])
                    st.rerun()

    # Queue preview
    if queued:
        st.markdown('<div class="section-label">Coming up in queue</div>', unsafe_allow_html=True)
        rows_html = ""
        for task in queued:
            rows_html += f"""
            <div class="queue-row">
                <span class="task-index">·</span>
                <div class="task-text">{task['text']}</div>
            </div>"""
        st.markdown(rows_html, unsafe_allow_html=True)


def view_week(data):
    today_key = get_today_key()
    st.markdown('<div class="section-label">Weekly Timetable</div>', unsafe_allow_html=True)

    for day_idx, cfg in DAY_CONFIG.items():
        key      = str(day_idx)
        tasks    = data.get(key, [])
        is_today = (key == today_key)
        label    = f"{cfg['emoji']}  {cfg['name']}  —  {cfg['category']}" + ("  ◀ today" if is_today else "")

        with st.expander(label, expanded=is_today):
            if not tasks:
                st.caption("No tasks yet.")
            else:
                for i, task in enumerate(tasks):
                    c1, c2 = st.columns([10, 1])
                    with c1:
                        weight = "**" if i < TASKS_PER_DAY else ""
                        flags  = []
                        if task.get("retire"):   flags.append("once")
                        if task["done_count"]>0: flags.append(f"done {task['done_count']}×")
                        suffix = f" *({', '.join(flags)})*" if flags else ""
                        prefix = f"{i+1}. " if i < TASKS_PER_DAY else f"— "
                        st.markdown(f"{prefix}{weight}{task['text']}{weight}{suffix}")
                    with c2:
                        if st.button("✕", key=f"wdel_{task['id']}"):
                            delete_task(data, key, task["id"])
                            st.rerun()


def view_add(data):
    st.markdown('<div class="section-label" style="margin-top:2rem">New task</div>', unsafe_allow_html=True)

    day_options = {
        f"{cfg['emoji']}  {cfg['name']}  —  {cfg['category']}": str(i)
        for i, cfg in DAY_CONFIG.items()
    }

    selected_label = st.selectbox("Which day?", list(day_options.keys()))
    selected_key   = day_options[selected_label]

    st.markdown("<br>", unsafe_allow_html=True)
    task_text = st.text_input("Task", placeholder="e.g. Read 2 chapters of textbook", label_visibility="collapsed")
    retire    = st.checkbox("One-time task — remove after done (default: rotates back to queue)")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Add task →", use_container_width=True):
        if task_text.strip():
            nid = get_next_id(data)
            data.setdefault(selected_key, []).append(
                {"id": nid, "text": task_text.strip(), "done_count": 0, "retire": retire}
            )
            save_tasks(data)
            st.success(f"Added to {DAY_CONFIG[int(selected_key)]['name']}.")
            st.rerun()
        else:
            st.warning("Please type a task first.")


# ── Actions ───────────────────────────────────────────────────────────────────
def mark_done(data, day_key, task_id):
    tasks = data.get(day_key, [])
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            t["done_count"] += 1
            if t.get("retire"):
                tasks.pop(i)
            else:
                tasks.append(tasks.pop(i))
            break
    save_tasks(data)

def delete_task(data, day_key, task_id):
    data[day_key] = [t for t in data.get(day_key, []) if t["id"] != task_id]
    save_tasks(data)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="One Thing Forward",
        page_icon="🎯",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    inject_css()
    data = load_tasks()

    t1, t2, t3 = st.tabs(["Today", "This Week", "Add Task"])
    with t1: view_today(data)
    with t2: view_week(data)
    with t3: view_add(data)

if __name__ == "__main__":
    main()
