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

# Update these URLs to your actual links
EXCEL_SHEET_URL = ""   # ← paste your Google Sheets / OneDrive URL here

# Friday checklist
FRIDAY_CHECKLIST = [
    {"id": "f1", "text": "Check portfolio",                                             "tag": "portfolio"},
    {"id": "f2", "text": "Check Momentum portfolio",                                    "tag": "portfolio"},
    {"id": "f3", "text": "FA analysis of all holdings → add to Excel sheet",            "tag": "research"},
    {"id": "f4", "text": "Investor presentation screening — latest results + concalls", "tag": "research"},
    {"id": "f5", "text": "Check pledge margins — pledge more if available",             "tag": "margins"},
    {"id": "f6", "text": "Check buy / sell signals",                                    "tag": "signals"},
    {"id": "f7", "text": "Check credit card bills",                                     "tag": "bills"},
    {"id": "f8", "text": "Society maintenance bill (every 3 months)",                   "tag": "bills"},
    {"id": "f9", "text": "Jio / VF bill",                                               "tag": "bills"},
]

TAG_COLORS = {
    "portfolio": "#1D4E89",
    "research":  "#7B341E",
    "margins":   "#2D6A4F",
    "signals":   "#4A235A",
    "bills":     "#5C5C5C",
}

# ── FA Analyser prompt (your exact prompt) ────────────────────────────────────
FA_SYSTEM_PROMPT = """You are an Indian stock fundamental analyser for long-term investors.

CRITICAL RULES:
1. No forward-looking statements implying future performance. Analysis is based on verified historical data only.
2. Every metric MUST cite its source. If not found → write DATA UNAVAILABLE.
3. Never fabricate financial data. Attempt live web search first. If unavailable, state clearly.
4. No buy/sell/target price. Ever. You give a VIEW. The user decides.
5. Execute all steps in exact order.

RESEARCH CHECKLIST (fetch via web search):
- Live CMP, 52W high/low, market cap, face value
- P/E, P/B, EV/EBITDA — current + sector average + stock's own 5-year historical average
- Revenue CAGR: 3Y and 5Y | Net Profit CAGR: 3Y and 5Y | EPS CAGR: 3Y and 5Y
- EBITDA margin trend: 5 years | Net profit margin trend: 5 years
- EPS: last 8 quarters with YoY change | Free Cash Flow: last 3-5 years
- Debt-to-Equity: 5-year trend | Interest Coverage Ratio | Current Ratio
- ROE and ROCE: current + 3Y avg + 5Y avg | Dividend history and payout ratio
- Promoter holding: last 8-12 quarters | Promoter pledging (flag if above 10%)
- FII and DII holding trend: last 8 quarters
- Competitive moat | Sector tailwinds/headwinds | Regulatory risks
- Management track record | Latest quarterly earnings call commentary
- 3 closest peer companies | Top 5 recent news items

VALUATION: Compare P/E, P/B, EV/EBITDA vs sector average and stock's own 5Y history.
Signal: CHEAP / FAIR / EXPENSIVE. Overall: UNDERVALUED / FAIRLY VALUED / OVERVALUED / MIXED

GROWTH: Classify as ACCELERATING / STEADY / SLOWING / DECLINING

FINANCIAL HEALTH:
- D/E: below 1=SAFE, 1-2=MODERATE, above 2=LEVERAGED
- Interest Coverage: above 3x=HEALTHY, 1.5-3x=WATCH, below 1.5=RISK
- Current Ratio: above 1.5=COMFORTABLE, 1-1.5=WATCH, below 1=RISK
- FCF: positive+growing=STRONG, positive+flat=STABLE, negative=CONCERN

RETURN QUALITY: ROE/ROCE above 15%=GOOD, 10-15%=AVERAGE, below 10%=WEAK

PEER COMPARISON: 3 closest competitors on P/E, P/B, ROE, Revenue Growth, D/E
Classify: LEADING / MID-PACK / LAGGING

OWNERSHIP: Promoter trend: BUYING/STABLE/SELLING | FII: INCREASING/STABLE/DECREASING
DII: INCREASING/STABLE/DECREASING | Flag pledging above 10%

FUNDAMENTAL VIEW (for stated horizon):
- One-sentence summary of fundamentals
- 3 strengths | 2 risks/watch points | 1 thing to track
- Overall quality: STRONG / MODERATE / WEAK

DATA CONFIDENCE: Count live metrics retrieved.
9-10 live=HIGH, 6-8=MODERATE, below 6=LOW, 0=VERY LOW

OUTPUT FORMAT:
Produce a clean structured analysis with these sections clearly labeled:
SNAPSHOT | VALUATION | GROWTH | FINANCIAL HEALTH | RETURN QUALITY | PEER COMPARISON | OWNERSHIP | FUNDAMENTAL VIEW

Use Indian numbering (Cr/Lakh). Cite every source. Flag DATA UNAVAILABLE clearly.
This is a VIEW based on fundamentals only. Not a buy/sell recommendation."""

# ── Quarterly Results prompt (your exact prompt) ──────────────────────────────
RESULTS_SYSTEM_PROMPT = """You are a senior equity research analyst with 15+ years of experience covering Indian listed companies. You write for sophisticated retail investors who hold concentrated portfolios.

Your job: read the attached quarterly results PDF and produce a single-page executive summary that tells me — in under 3 minutes of reading — whether this quarter was good, bad, or mixed, and whether the long-term thesis is still intact.

You are NOT a SEBI-registered advisor. You do NOT issue buy/sell/hold calls.

OUTPUT STRUCTURE:

1. HEADLINE VERDICT
One crisp sentence. Good quarter / Bad quarter / Mixed quarter and why.

2. KEY FINANCIALS TABLE
Revenue | QoQ% | YoY%
EBITDA | QoQ% | YoY%
PAT | QoQ% | YoY%
+ Business-specific KPI based on sector

SECTOR LENS:
Banks & NBFCs → QoQ | NIM, GNPA/NNPA, credit cost, slippage, loan growth
FMCG/Consumer → YoY | Volume vs price growth, rural vs urban, gross margin
Capital Goods/Infra → YoY | Order inflows, order book, book-to-bill, execution
IT/Technology → QoQ+YoY | USD revenue, EBIT margin, deal wins TCV, attrition
Pharma → YoY | US generics, domestic formulations, R&D, ANDA pipeline
Auto → YoY+MoM | Volume by segment, ASP, EV mix, exports
Cement/Metals → QoQ | Realization/unit, volume, cost/tonne, EBITDA/tonne
Telecom → QoQ | ARPU, subscriber adds, data usage, capex
Real Estate → YoY | Bookings, collections, launches, inventory
Retail → YoY | Same-store sales, footfall, gross margin, inventory days

3. WHAT WENT RIGHT
3-5 crisp bullets. Quantify wherever possible.

4. WHAT WENT WRONG (or needs watching)
3-5 crisp bullets. Be honest. No sugar-coating.

5. MANAGEMENT GUIDANCE & COMMENTARY
Only what management actually said. Group under:
- Revenue/volume outlook
- Margin guidance
- Order book / pipeline
- Capex plans
- Other strategic commentary

6. INVESTOR LENS
One closing sentence only — directional, not mealy-mouthed.

HARD RULES:
- One page only. Brevity is the product.
- Numbers must come from the document. Never invent. If not disclosed, say so.
- No jargon dump. Spell out acronyms on first use.
- No empty phrases like "the company reported strong results."
- Indian numbering: Cr/Lakh (not millions/billions unless company reports in USD).
- Tone: Conversational but precise. Smart analyst friend over coffee.
- NEVER use: buy, sell, hold, accumulate, book profits, exit, should you invest."""


def _call_claude_api(messages, use_web_search=False):
    """Call Claude API and return the text response."""
    import requests
    import json

    tools = []
    if use_web_search:
        tools = [{"type": "web_search_20250305", "name": "web_search"}]

    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "system": messages["system"],
        "messages": messages["messages"],
    }
    if tools:
        payload["tools"] = tools

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )

    if response.status_code != 200:
        return f"API error {response.status_code}: {response.text}"

    data = response.json()
    # Extract all text blocks from response
    text_parts = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
    return "\n\n".join(text_parts) if text_parts else "No response received."


def _render_fa_analyser():
    """Tool 1 — FA Analyser: ticker input → Claude API with web search."""
    st.markdown('<div class="section-label">📊 FA Analyser — Powered by Claude</div>', unsafe_allow_html=True)

    with st.expander("Run Fundamental Analysis", expanded=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            ticker = st.text_input(
                "Stock ticker or name",
                key="fa_ticker",
                label_visibility="collapsed",
                placeholder="e.g. RELIANCE · TCS · HDFCBANK · Infosys"
            )
        with col2:
            horizon = st.selectbox(
                "Horizon",
                ["3 Years", "5 Years", "10 Years"],
                key="fa_horizon",
                label_visibility="collapsed"
            )

        st.caption("Fetches live data via web search. Takes 30–60 seconds.")

        if st.button("▶  Run FA Analysis", key="fa_run_btn", use_container_width=True):
            if not ticker.strip():
                st.warning("Enter a stock ticker first.")
            else:
                with st.spinner(f"Researching {ticker.upper()} — fetching live data, this takes ~30s…"):
                    messages = {
                        "system": FA_SYSTEM_PROMPT,
                        "messages": [
                            {
                                "role": "user",
                                "content": f"Stock: {ticker.strip().upper()}\nInvestment horizon: {horizon}\n\nPlease run the full fundamental analysis."
                            }
                        ]
                    }
                    result = _call_claude_api(messages, use_web_search=True)
                    st.session_state["fa_result"] = result
                    st.session_state["fa_ticker_done"] = ticker.upper()

        # Show result if available
        if st.session_state.get("fa_result"):
            st.markdown("---")
            st.markdown(f"**{st.session_state.get('fa_ticker_done', '')} — Fundamental Analysis**")
            st.markdown(st.session_state["fa_result"])

            # Save to holdings notes button
            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
            if st.button("💾  Save summary to Holdings notes", key="fa_save_btn"):
                ticker_done = st.session_state.get("fa_ticker_done", "UNKNOWN")
                # Save first 500 chars as notes to keep it concise
                summary = st.session_state["fa_result"][:500] + "…"
                db.add_finance(ticker_done, ftype="research", notes=summary)
                st.success(f"Saved {ticker_done} analysis to Research Notes.")


def _render_results_analyser():
    """Tool 2 — Quarterly Results Analyser: PDF upload → Claude API."""
    st.markdown('<div class="section-label">📋 Quarterly Results Analyser — Powered by Claude</div>', unsafe_allow_html=True)

    with st.expander("Analyse Investor Presentation / Results PDF", expanded=False):
        st.caption("Upload the quarterly results PDF or investor presentation. Analysis in ~20 seconds.")

        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            key="results_pdf",
            label_visibility="collapsed"
        )

        company_name = st.text_input(
            "Company name (optional — helps context)",
            key="results_company",
            label_visibility="collapsed",
            placeholder="e.g. Reliance Industries Q3 FY25"
        )

        if st.button("▶  Analyse Results", key="results_run_btn", use_container_width=True):
            if not uploaded_file:
                st.warning("Please upload a PDF first.")
            else:
                import base64
                with st.spinner("Reading the presentation and building your one-pager…"):
                    # Read and encode PDF as base64
                    pdf_bytes = uploaded_file.read()
                    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

                    context = f"Company: {company_name.strip()}\n\n" if company_name.strip() else ""

                    messages = {
                        "system": RESULTS_SYSTEM_PROMPT,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "document",
                                        "source": {
                                            "type": "base64",
                                            "media_type": "application/pdf",
                                            "data": pdf_b64
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{context}Please produce the quarterly results one-pager as per your instructions."
                                    }
                                ]
                            }
                        ]
                    }
                    result = _call_claude_api(messages, use_web_search=False)
                    st.session_state["results_result"] = result
                    st.session_state["results_company_done"] = company_name or uploaded_file.name

        # Show result
        if st.session_state.get("results_result"):
            st.markdown("---")
            st.markdown(f"**{st.session_state.get('results_company_done', 'Results')} — One-Pager**")
            st.markdown(st.session_state["results_result"])

            # Save to research notes
            st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
            save_ticker = st.text_input("Save as ticker (e.g. RELIANCE)", key="results_save_ticker",
                                        label_visibility="collapsed", placeholder="Ticker to save under…")
            if st.button("💾  Save to Research Notes", key="results_save_btn"):
                if save_ticker.strip():
                    summary = st.session_state["results_result"][:500] + "…"
                    db.add_finance(save_ticker.strip().upper(), ftype="research", notes=summary)
                    st.success(f"Saved to Research Notes under {save_ticker.upper()}.")
                else:
                    st.warning("Enter a ticker to save under.")


def render_friday(events):
    _page_header(4, "Finance & Markets Day")
    _week_strip(4)
    _calendar_section(events)

    # ── Quick Links ───────────────────────────────────────────────────────────
    if EXCEL_SHEET_URL:
        st.markdown(
            f'<a href="{EXCEL_SHEET_URL}" target="_blank" style="'
            f'display:inline-block;padding:0.6rem 1.1rem;background:#FFF;border:1px solid #E2E0DC;'
            f'border-radius:8px;text-decoration:none;color:#1A1A1A;font-size:0.85rem;margin-bottom:1.2rem">'
            f'📋 Open Holdings Excel Sheet ↗</a>',
            unsafe_allow_html=True
        )

    # ── Friday Checklist ──────────────────────────────────────────────────────
    st.markdown('<div class="section-label">Friday Checklist</div>', unsafe_allow_html=True)

    rows_html = ""
    for i, item in enumerate(FRIDAY_CHECKLIST):
        tag_color = TAG_COLORS.get(item["tag"], "#888")
        rows_html += f"""
        <div class="task-row">
            <span class="task-idx">{i+1}</span>
            <div style="flex:1">
                <div class="task-text">{item['text']}</div>
                <div class="task-meta" style="color:{tag_color}">{item['tag']}</div>
            </div>
        </div>"""
    st.markdown(rows_html, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:0.6rem'></div>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, item in enumerate(FRIDAY_CHECKLIST):
        with cols[i % 2]:
            st.checkbox(item["text"], key=f"fri_check_{item['id']}")

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── AI Tools ──────────────────────────────────────────────────────────────
    _render_fa_analyser()
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    _render_results_analyser()

    # ── Portfolio & Watchlist ─────────────────────────────────────────────────
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
                fn = st.text_input("Notes / thesis", key=f"fn_{ftype}", label_visibility="collapsed",
                                   placeholder="Why watching? Investment thesis?")
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
