"""
styles.py — All CSS for the app. One place to change the look.
"""

# Day-specific accent colours (subtle, not loud)
DAY_COLORS = {
    0: "#2D6A4F",   # Monday   — deep green    (focus, academics)
    1: "#1D4E89",   # Tuesday  — deep blue     (content, creativity)
    2: "#6B4226",   # Wednesday— warm brown    (self-help, warmth)
    3: "#4A235A",   # Thursday — deep purple   (editing, deep work)
    4: "#7B341E",   # Friday   — dark terracotta(finance, analytical)
    5: "#4A4A4A",   # Saturday — neutral grey  (flex, light)
    6: "#7D6608",   # Sunday   — golden olive  (personal, spiritual)
}

DAY_CONFIG = {
    0: {"name": "Monday",    "category": "Academics",                "emoji": "📚"},
    1: {"name": "Tuesday",   "category": "Content Engine",           "emoji": "🎬"},
    2: {"name": "Wednesday", "category": "Self Help & Growth",       "emoji": "🌱"},
    3: {"name": "Thursday",  "category": "Video Editing",            "emoji": "✂️"},
    4: {"name": "Friday",    "category": "Finance & Markets",        "emoji": "📈"},
    5: {"name": "Saturday",  "category": "Flex & Recovery",          "emoji": "🔁"},
    6: {"name": "Sunday",    "category": "Personal & Rest",          "emoji": "☀️"},
}

CONTENT_STATUSES = ["idea", "scripting", "shot", "editing", "thumbnail", "uploaded"]
CONTENT_TYPES    = ["reel", "youtube", "linkedin", "blog", "script", "thumbnail"]
WATCH_CATEGORIES = ["all", "productivity", "psychology", "finance", "spirituality", "other"]
FINANCE_TYPES    = ["watchlist", "holding", "research"]
CAPTURE_TYPES    = ["note", "idea", "task", "content"]


def get_css(day_key: int) -> str:
    accent = DAY_COLORS.get(day_key, "#2D6A4F")
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif !important;
    }}

    /* ── App background ── */
    .stApp {{
        background-color: #FAFAF8 !important;
        color: #1A1A1A !important;
    }}
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 760px !important;
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background-color: #F4F3F0 !important;
        border-right: 1px solid #E8E6E1 !important;
    }}
    [data-testid="stSidebar"] .stRadio label {{
        font-size: 0.88rem !important;
        color: #444 !important;
        padding: 0.25rem 0 !important;
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        font-family: 'Lora', serif !important;
        color: #1A1A1A !important;
    }}

    /* ── Page header ── */
    .page-header {{
        padding: 2rem 0 1rem 0;
    }}
    .page-eyebrow {{
        font-size: 0.68rem;
        font-weight: 500;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #AAA;
        margin-bottom: 0.4rem;
    }}
    .page-title {{
        font-family: 'Lora', serif;
        font-size: 2.1rem;
        font-weight: 600;
        color: #1A1A1A;
        line-height: 1.15;
        margin: 0 0 0.25rem 0;
    }}
    .page-subtitle {{
        font-size: 0.82rem;
        color: #AAA;
        font-weight: 300;
    }}
    .accent-rule {{
        height: 2px;
        width: 36px;
        background: {accent};
        border-radius: 2px;
        margin: 1.2rem 0 1.8rem 0;
    }}

    /* ── Week strip ── */
    .week-strip {{
        display: flex;
        gap: 5px;
        margin-bottom: 2rem;
    }}
    .day-chip {{
        flex: 1;
        text-align: center;
        padding: 0.5rem 0.1rem;
        border-radius: 9px;
        background: #EEECEA;
        border: 1.5px solid transparent;
        cursor: default;
    }}
    .day-chip.active {{
        background: {accent};
        border-color: {accent};
    }}
    .day-chip-emoji {{ font-size: 0.95rem; display: block; margin-bottom: 2px; }}
    .day-chip-label {{
        font-size: 0.52rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #999;
        display: block;
    }}
    .day-chip.active .day-chip-label {{ color: #FFF; }}

    /* ── Section labels ── */
    .section-label {{
        font-size: 0.63rem;
        font-weight: 600;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        color: #BBB;
        margin: 2rem 0 0.9rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #EBEBEB;
    }}

    /* ── Calendar events ── */
    .cal-event {{
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        padding: 0.7rem 0;
        border-bottom: 1px solid #F0EFec;
    }}
    .cal-time {{
        font-size: 0.72rem;
        color: {accent};
        font-weight: 500;
        min-width: 80px;
        padding-top: 2px;
    }}
    .cal-title {{
        font-size: 0.9rem;
        color: #1A1A1A;
    }}
    .cal-location {{
        font-size: 0.72rem;
        color: #AAA;
        margin-top: 2px;
    }}

    /* ── Task rows ── */
    .task-row {{
        display: flex;
        align-items: center;
        gap: 0.9rem;
        padding: 0.95rem 0;
        border-bottom: 1px solid #F0EFEC;
    }}
    .task-row:first-of-type {{ border-top: 1px solid #F0EFEC; }}
    .task-idx {{
        font-family: 'Lora', serif;
        font-style: italic;
        font-size: 1rem;
        color: #CCC;
        min-width: 1.4rem;
    }}
    .task-text {{
        flex: 1;
        font-size: 0.95rem;
        color: #1A1A1A;
        line-height: 1.4;
    }}
    .task-meta {{
        font-size: 0.68rem;
        color: #CCC;
        margin-top: 2px;
    }}
    .priority-high {{ color: {accent}; font-size: 0.6rem; font-weight: 600; }}

    /* ── Queue rows (dimmed) ── */
    .queue-row {{
        display: flex; align-items: center; gap: 0.9rem;
        padding: 0.6rem 0; border-bottom: 1px solid #F5F5F3; opacity: 0.38;
    }}

    /* ── Content pipeline ── */
    .status-badge {{
        display: inline-block;
        font-size: 0.6rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 2px 8px;
        border-radius: 20px;
        background: #F0EFEC;
        color: #888;
    }}
    .status-uploaded {{ background: #EAF5EE; color: #2D6A4F; }}
    .status-editing  {{ background: #EAF0FF; color: #1D4E89; }}
    .status-idea     {{ background: #F5F5F3; color: #999; }}

    /* ── Capture box ── */
    .capture-banner {{
        background: {accent};
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 1.5rem 0;
        color: white;
    }}
    .capture-banner h4 {{
        font-family: 'Lora', serif;
        font-size: 1rem;
        margin: 0 0 0.3rem 0;
        color: white;
    }}
    .capture-banner p {{
        font-size: 0.78rem;
        margin: 0;
        opacity: 0.75;
        color: white !important;
    }}

    /* ── Finance ── */
    .ticker-row {{
        display: flex; align-items: center; gap: 1rem;
        padding: 0.8rem 0; border-bottom: 1px solid #F0EFEC;
    }}
    .ticker {{ font-weight: 600; font-size: 0.95rem; color: #1A1A1A; min-width: 80px; }}
    .ticker-type {{
        font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em;
        text-transform: uppercase; color: #AAA;
        border: 1px solid #E5E5E5; border-radius: 4px; padding: 1px 6px;
    }}
    .ticker-notes {{ font-size: 0.82rem; color: #888; flex: 1; }}

    /* ── Buttons ── */
    div[data-testid="stButton"] > button {{
        font-family: 'Inter', sans-serif !important;
        font-size: 0.8rem !important;
        font-weight: 400 !important;
        color: #555 !important;
        background: #FFF !important;
        border: 1px solid #E2E0DC !important;
        border-radius: 7px !important;
        transition: all 0.15s ease !important;
    }}
    div[data-testid="stButton"] > button:hover {{
        background: #F5F3F0 !important;
        border-color: #CCC !important;
        color: #1A1A1A !important;
    }}

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {{
        background: transparent !important;
        border-bottom: 1px solid #E8E6E1 !important;
        gap: 0 !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        color: #AAA !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
        padding: 0.55rem 1.1rem !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: #1A1A1A !important;
        border-bottom: 2px solid {accent} !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{ padding-top: 0.5rem !important; }}

    /* ── Inputs ── */
    .stTextInput > label, .stSelectbox > label,
    .stTextArea > label, .stCheckbox > label span {{
        font-size: 0.78rem !important;
        font-weight: 400 !important;
        color: #888 !important;
    }}
    .stTextInput input, .stTextArea textarea {{
        background: #FFF !important;
        border: 1px solid #E2E0DC !important;
        border-radius: 8px !important;
        color: #1A1A1A !important;
        font-size: 0.92rem !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {accent} !important;
        box-shadow: none !important;
    }}
    div[data-baseweb="select"] > div {{
        background: #FFF !important;
        border: 1px solid #E2E0DC !important;
        border-radius: 8px !important;
        color: #1A1A1A !important;
    }}

    /* ── Expanders ── */
    details {{
        border: 1px solid #EBEBEB !important;
        border-radius: 10px !important;
        background: #FFF !important;
        margin-bottom: 0.45rem !important;
    }}
    summary {{
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: #1A1A1A !important;
        padding: 0.8rem 1rem !important;
    }}

    /* ── Misc ── */
    p, .stMarkdown p {{ color: #1A1A1A !important; }}
    .stAlert {{ border-radius: 8px !important; font-size: 0.85rem !important; }}
    hr {{ border-color: #EEECEA !important; }}
    h1, h2, h3 {{ font-family: 'Lora', serif !important; color: #1A1A1A !important; }}
    </style>
    """
