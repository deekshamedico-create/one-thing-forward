import streamlit as st
import json
import os
from datetime import datetime, date

# ── Config ────────────────────────────────────────────────────────────────────
TASKS_FILE = "tasks.json"

DAY_CONFIG = {
    0: {"name": "Monday",    "category": "Academics",                "emoji": "📚", "color": "#4F46E5"},
    1: {"name": "Tuesday",   "category": "Content Engine",           "emoji": "🎬", "color": "#0891B2"},
    2: {"name": "Wednesday", "category": "Self Help & Growth",       "emoji": "🌱", "color": "#059669"},
    3: {"name": "Thursday",  "category": "Video Editing",            "emoji": "✂️", "color": "#D97706"},
    4: {"name": "Friday",    "category": "Finance & Stock Analysis", "emoji": "📈", "color": "#DC2626"},
    5: {"name": "Saturday",  "category": "Pending / Catch-up",       "emoji": "🔁", "color": "#7C3AED"},
    6: {"name": "Sunday",    "category": "Rest & Review",            "emoji": "☀️", "color": "#B45309"},
}

TASKS_PER_DAY = 3  # max shown at once

# ── Data Layer ────────────────────────────────────────────────────────────────
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
        "0": [  # Monday - Academics
            {"id": 1, "text": "Review lecture notes / textbook chapter", "done_count": 0, "retire": False},
            {"id": 2, "text": "Solve practice problems (30 min)", "done_count": 0, "retire": False},
            {"id": 3, "text": "Watch one educational video / lecture", "done_count": 0, "retire": False},
            {"id": 4, "text": "Update study schedule & goals", "done_count": 0, "retire": False},
        ],
        "1": [  # Tuesday - Content Engine
            {"id": 10, "text": "Plan next 3 content ideas", "done_count": 0, "retire": False},
            {"id": 11, "text": "Write / draft one script or outline", "done_count": 0, "retire": False},
            {"id": 12, "text": "Schedule / batch social posts", "done_count": 0, "retire": False},
            {"id": 13, "text": "Review analytics & engagement", "done_count": 0, "retire": False},
        ],
        "2": [  # Wednesday - Self Help
            {"id": 20, "text": "Read 20 pages of a self-help book", "done_count": 0, "retire": False},
            {"id": 21, "text": "Journaling: weekly reflection (15 min)", "done_count": 0, "retire": False},
            {"id": 22, "text": "Physical activity / workout", "done_count": 0, "retire": False},
            {"id": 23, "text": "Meditation or breathwork (10 min)", "done_count": 0, "retire": False},
        ],
        "3": [  # Thursday - Video Editing
            {"id": 30, "text": "Cut & edit raw footage", "done_count": 0, "retire": False},
            {"id": 31, "text": "Add transitions, text overlays, music", "done_count": 0, "retire": False},
            {"id": 32, "text": "Export & review final cut", "done_count": 0, "retire": False},
            {"id": 33, "text": "Organise project files & backups", "done_count": 0, "retire": False},
        ],
        "4": [  # Friday - Finance
            {"id": 40, "text": "Review portfolio performance", "done_count": 0, "retire": False},
            {"id": 41, "text": "Read 2 financial news articles", "done_count": 0, "retire": False},
            {"id": 42, "text": "Log weekly expenses & budget check", "done_count": 0, "retire": False},
            {"id": 43, "text": "Research one stock / sector deep-dive", "done_count": 0, "retire": False},
        ],
        "5": [  # Saturday - Pending
            {"id": 50, "text": "Clear anything left from the week", "done_count": 0, "retire": False},
            {"id": 51, "text": "Reply to pending messages / emails", "done_count": 0, "retire": False},
            {"id": 52, "text": "Plan next week's priorities", "done_count": 0, "retire": False},
        ],
        "6": [  # Sunday - Rest
            {"id": 60, "text": "Weekly review: what went well?", "done_count": 0, "retire": False},
            {"id": 61, "text": "Recharge: walk, movie, family time", "done_count": 0, "retire": False},
            {"id": 62, "text": "Prep workspace for Monday", "done_count": 0, "retire": False},
        ],
        "_next_id": 100,
    }

def get_today_key():
    return str(date.today().weekday())

def get_next_id(data):
    nid = data.get("_next_id", 100)
    data["_next_id"] = nid + 1
    return nid

# ── Styles ────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: #0F0F0F;
        color: #F0EDE8;
    }

    .hero-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .hero-day {
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: #666;
        margin-bottom: 0.3rem;
    }

    .hero-category {
        font-size: 2.2rem;
        font-weight: 600;
        color: #F0EDE8;
        margin: 0;
        line-height: 1.1;
    }

    .hero-date {
        font-family: 'Space Mono', monospace;
        font-size: 0.7rem;
        color: #444;
        margin-top: 0.4rem;
        letter-spacing: 0.15em;
    }

    .accent-bar {
        height: 3px;
        border-radius: 2px;
        margin: 1.2rem auto;
        width: 60px;
    }

    .task-card {
        background: #1A1A1A;
        border: 1px solid #2A2A2A;
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.7rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: border-color 0.2s;
    }

    .task-card:hover {
        border-color: #3A3A3A;
    }

    .task-number {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        color: #444;
        min-width: 20px;
    }

    .task-text {
        font-size: 1rem;
        font-weight: 400;
        color: #D0CCC6;
        flex: 1;
        line-height: 1.4;
    }

    .done-count {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        color: #555;
        white-space: nowrap;
    }

    .section-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #555;
        margin: 1.8rem 0 0.8rem 0;
    }

    .week-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 6px;
        margin: 1rem 0;
    }

    .week-pill {
        text-align: center;
        padding: 0.5rem 0.2rem;
        border-radius: 8px;
        font-family: 'Space Mono', monospace;
        font-size: 0.6rem;
        letter-spacing: 0.05em;
        color: #555;
        background: #1A1A1A;
        border: 1px solid #222;
    }

    .week-pill.today {
        color: #F0EDE8;
        border-color: #444;
    }

    .week-pill-emoji {
        font-size: 1rem;
        display: block;
        margin-bottom: 2px;
    }

    div[data-testid="stButton"] button {
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        border: 1px solid #2A2A2A !important;
        background: #1A1A1A !important;
        color: #D0CCC6 !important;
        transition: all 0.15s !important;
        width: 100% !important;
    }

    div[data-testid="stButton"] button:hover {
        background: #252525 !important;
        border-color: #3A3A3A !important;
        color: #F0EDE8 !important;
    }

    .stTextInput input, .stSelectbox select, div[data-baseweb="select"] {
        background: #1A1A1A !important;
        border: 1px solid #2A2A2A !important;
        border-radius: 8px !important;
        color: #D0CCC6 !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    .stTextInput input:focus {
        border-color: #444 !important;
        box-shadow: none !important;
    }

    .stCheckbox label {
        color: #D0CCC6 !important;
        font-size: 0.9rem !important;
    }

    .stExpander {
        background: #1A1A1A !important;
        border: 1px solid #2A2A2A !important;
        border-radius: 12px !important;
    }

    hr {
        border-color: #1E1E1E !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        background: #0F0F0F !important;
        gap: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        background: #1A1A1A !important;
        border-radius: 8px !important;
        color: #666 !important;
        font-family: 'Space Mono', monospace !important;
        font-size: 0.65rem !important;
        letter-spacing: 0.1em !important;
        padding: 0.4rem 0.8rem !important;
    }

    .stTabs [aria-selected="true"] {
        color: #F0EDE8 !important;
        background: #252525 !important;
    }

    .stSuccess {
        background: #0D1F13 !important;
        border: 1px solid #1A4A28 !important;
        border-radius: 8px !important;
    }

    .retire-tag {
        font-family: 'Space Mono', monospace;
        font-size: 0.55rem;
        color: #DC2626;
        letter-spacing: 0.1em;
        border: 1px solid #3A1515;
        padding: 1px 6px;
        border-radius: 4px;
    }

    .queue-tag {
        font-family: 'Space Mono', monospace;
        font-size: 0.55rem;
        color: #555;
        letter-spacing: 0.1em;
        border: 1px solid #222;
        padding: 1px 6px;
        border-radius: 4px;
    }

    </style>
    """, unsafe_allow_html=True)

# ── Views ─────────────────────────────────────────────────────────────────────
def view_today(data):
    today_key = get_today_key()
    day_info = DAY_CONFIG[int(today_key)]
    today_tasks = data.get(today_key, [])
    active_tasks = today_tasks[:TASKS_PER_DAY]

    # Hero header
    st.markdown(f"""
    <div class="hero-header">
        <div class="hero-day">{day_info['name']}</div>
        <div class="hero-category">{day_info['emoji']} {day_info['category']}</div>
        <div class="hero-date">{date.today().strftime('%d %B %Y').upper()}</div>
        <div class="accent-bar" style="background:{day_info['color']}"></div>
    </div>
    """, unsafe_allow_html=True)

    # Week strip
    week_html = '<div class="week-grid">'
    for i, cfg in DAY_CONFIG.items():
        cls = "week-pill today" if i == int(today_key) else "week-pill"
        week_html += f'<div class="{cls}"><span class="week-pill-emoji">{cfg["emoji"]}</span>{cfg["name"][:3].upper()}</div>'
    week_html += '</div>'
    st.markdown(week_html, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Your focus today</div>', unsafe_allow_html=True)

    if not active_tasks:
        st.info("No tasks for today. Add some below! 👇")
    else:
        for i, task in enumerate(active_tasks):
            retire_tag = '<span class="retire-tag">ONCE</span>' if task.get("retire") else '<span class="queue-tag">QUEUE</span>'
            done_label = f"×{task['done_count']}" if task['done_count'] > 0 else ""
            st.markdown(f"""
            <div class="task-card">
                <span class="task-number">0{i+1}</span>
                <span class="task-text">{task['text']}</span>
                {retire_tag}
                <span class="done-count">{done_label}</span>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"✓ Done — rotate to back", key=f"done_{task['id']}"):
                    mark_done(data, today_key, task['id'])
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{task['id']}"):
                    delete_task(data, today_key, task['id'])
                    st.rerun()

    # Queue preview
    if len(today_tasks) > TASKS_PER_DAY:
        st.markdown('<div class="section-label">Up next in queue</div>', unsafe_allow_html=True)
        for task in today_tasks[TASKS_PER_DAY:]:
            st.markdown(f"""
            <div class="task-card" style="opacity:0.4">
                <span class="task-number">—</span>
                <span class="task-text">{task['text']}</span>
            </div>
            """, unsafe_allow_html=True)


def view_week(data):
    st.markdown('<div class="section-label">Full Weekly Timetable</div>', unsafe_allow_html=True)
    today_key = get_today_key()

    for day_idx, cfg in DAY_CONFIG.items():
        key = str(day_idx)
        tasks = data.get(key, [])
        is_today = (key == today_key)
        label = f"{cfg['emoji']} {cfg['name']} — {cfg['category']}" + (" ◀ TODAY" if is_today else "")

        with st.expander(label, expanded=is_today):
            if not tasks:
                st.caption("No tasks yet.")
            for i, task in enumerate(tasks):
                col1, col2, col3 = st.columns([0.5, 6, 1])
                with col1:
                    st.caption(f"{i+1}.")
                with col2:
                    active = "**" if i < TASKS_PER_DAY else ""
                    retire_note = " *(once)*" if task.get("retire") else ""
                    done_note = f" *(done {task['done_count']}×)*" if task['done_count'] > 0 else ""
                    st.markdown(f"{active}{task['text']}{active}{retire_note}{done_note}")
                with col3:
                    if st.button("🗑", key=f"wdel_{task['id']}"):
                        delete_task(data, key, task['id'])
                        st.rerun()


def view_add(data):
    st.markdown('<div class="section-label">Add a new task</div>', unsafe_allow_html=True)

    day_options = {f"{cfg['emoji']} {cfg['name']} — {cfg['category']}": str(i)
                   for i, cfg in DAY_CONFIG.items()}

    selected_label = st.selectbox("Which day / category?", list(day_options.keys()))
    selected_key = day_options[selected_label]

    task_text = st.text_input("What's the task?", placeholder="e.g. Read 2 chapters of textbook")
    retire = st.checkbox("One-time task (retire after done)", value=False,
                         help="If checked, task disappears after you mark it done. Otherwise it rotates.")

    if st.button("＋ Add Task", use_container_width=True):
        if task_text.strip():
            nid = get_next_id(data)
            new_task = {"id": nid, "text": task_text.strip(), "done_count": 0, "retire": retire}
            data.setdefault(selected_key, []).append(new_task)
            save_tasks(data)
            st.success(f"Added to {DAY_CONFIG[int(selected_key)]['name']}!")
            st.rerun()
        else:
            st.warning("Please enter a task first.")


# ── Actions ───────────────────────────────────────────────────────────────────
def mark_done(data, day_key, task_id):
    tasks = data.get(day_key, [])
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            t["done_count"] += 1
            if t.get("retire"):
                tasks.pop(i)  # remove one-time tasks
            else:
                tasks.append(tasks.pop(i))  # rotate to back
            break
    save_tasks(data)

def delete_task(data, day_key, task_id):
    tasks = data.get(day_key, [])
    data[day_key] = [t for t in tasks if t["id"] != task_id]
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

    tab1, tab2, tab3 = st.tabs(["TODAY", "THIS WEEK", "ADD TASK"])

    with tab1:
        view_today(data)

    with tab2:
        view_week(data)

    with tab3:
        view_add(data)


if __name__ == "__main__":
    main()
