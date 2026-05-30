"""
database.py — SQLite setup and all DB operations.
"""

import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path("data/otf.db")


def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            text        TEXT    NOT NULL,
            day_key     INTEGER NOT NULL,
            category    TEXT    DEFAULT '',
            priority    INTEGER DEFAULT 2,
            status      TEXT    DEFAULT 'pending',
            recurring   INTEGER DEFAULT 1,
            done_count  INTEGER DEFAULT 0,
            created_at  TEXT    DEFAULT (date('now')),
            done_at     TEXT    DEFAULT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS captures (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            text       TEXT NOT NULL,
            type       TEXT DEFAULT 'note',
            processed  INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            type        TEXT DEFAULT 'reel',
            status      TEXT DEFAULT 'idea',
            notes       TEXT DEFAULT '',
            created_at  TEXT DEFAULT (date('now')),
            updated_at  TEXT DEFAULT (date('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS finance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker      TEXT NOT NULL,
            type        TEXT DEFAULT 'watchlist',
            notes       TEXT DEFAULT '',
            target      REAL DEFAULT 0,
            created_at  TEXT DEFAULT (date('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS watch_queue (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            url         TEXT DEFAULT '',
            category    TEXT DEFAULT 'general',
            watched     INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (date('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS shoot_day (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL UNIQUE,
            day   TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    _seed_default_tasks()


# ── Tasks ─────────────────────────────────────────────────────────────────────

def get_tasks(day_key=None, status="pending"):
    conn = get_conn()
    q = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if day_key is not None:
        q += " AND (day_key=? OR day_key=7)"
        params.append(day_key)
    if status:
        q += " AND status=?"
        params.append(status)
    q += " ORDER BY priority ASC, id ASC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_carried_tasks():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE status='carried' ORDER BY priority ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_task(text, day_key, category="", priority=2, recurring=True):
    conn = get_conn()
    conn.execute(
        "INSERT INTO tasks (text, day_key, category, priority, recurring) VALUES (?,?,?,?,?)",
        (text, day_key, category, priority, int(recurring))
    )
    conn.commit()
    conn.close()


def mark_task_done(task_id, recurring):
    conn = get_conn()
    if recurring:
        conn.execute(
            "UPDATE tasks SET done_count=done_count+1, status='pending', done_at=date('now') WHERE id=?",
            (task_id,)
        )
    else:
        conn.execute(
            "UPDATE tasks SET done_count=done_count+1, status='done', done_at=date('now') WHERE id=?",
            (task_id,)
        )
    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()


# ── Quick Capture ─────────────────────────────────────────────────────────────

def add_capture(text, ctype="note"):
    conn = get_conn()
    conn.execute("INSERT INTO captures (text, type) VALUES (?,?)", (text, ctype))
    conn.commit()
    conn.close()


def get_captures(processed=False):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM captures WHERE processed=? ORDER BY created_at DESC",
        (int(processed),)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def process_capture(capture_id):
    conn = get_conn()
    conn.execute("UPDATE captures SET processed=1 WHERE id=?", (capture_id,))
    conn.commit()
    conn.close()


def delete_capture(capture_id):
    conn = get_conn()
    conn.execute("DELETE FROM captures WHERE id=?", (capture_id,))
    conn.commit()
    conn.close()


# ── Content ───────────────────────────────────────────────────────────────────

def get_content(ctype=None, status=None):
    conn = get_conn()
    q = "SELECT * FROM content WHERE 1=1"
    params = []
    if ctype:
        q += " AND type=?"
        params.append(ctype)
    if status:
        q += " AND status=?"
        params.append(status)
    q += " ORDER BY updated_at DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_content(title, ctype="reel", notes=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO content (title, type, notes) VALUES (?,?,?)",
        (title, ctype, notes)
    )
    conn.commit()
    conn.close()


def update_content_status(content_id, status):
    conn = get_conn()
    conn.execute(
        "UPDATE content SET status=?, updated_at=date('now') WHERE id=?",
        (status, content_id)
    )
    conn.commit()
    conn.close()


def delete_content(content_id):
    conn = get_conn()
    conn.execute("DELETE FROM content WHERE id=?", (content_id,))
    conn.commit()
    conn.close()


# ── Finance ───────────────────────────────────────────────────────────────────

def get_finance(ftype=None):
    conn = get_conn()
    q = "SELECT * FROM finance WHERE 1=1"
    params = []
    if ftype:
        q += " AND type=?"
        params.append(ftype)
    q += " ORDER BY ticker ASC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_finance(ticker, ftype="watchlist", notes="", target=0):
    conn = get_conn()
    conn.execute(
        "INSERT INTO finance (ticker, type, notes, target) VALUES (?,?,?,?)",
        (ticker.upper(), ftype, notes, target)
    )
    conn.commit()
    conn.close()


def delete_finance(fid):
    conn = get_conn()
    conn.execute("DELETE FROM finance WHERE id=?", (fid,))
    conn.commit()
    conn.close()


# ── Watch Queue ───────────────────────────────────────────────────────────────

def get_watch_queue(category=None, watched=False):
    conn = get_conn()
    q = "SELECT * FROM watch_queue WHERE watched=?"
    params = [int(watched)]
    if category and category != "all":
        q += " AND category=?"
        params.append(category)
    q += " ORDER BY created_at DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_watch_item(title, url="", category="general"):
    conn = get_conn()
    conn.execute(
        "INSERT INTO watch_queue (title, url, category) VALUES (?,?,?)",
        (title, url, category)
    )
    conn.commit()
    conn.close()


def mark_watched(item_id):
    conn = get_conn()
    conn.execute("UPDATE watch_queue SET watched=1 WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def delete_watch_item(item_id):
    conn = get_conn()
    conn.execute("DELETE FROM watch_queue WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


# ── Shoot Day ─────────────────────────────────────────────────────────────────

def get_shoot_day(month_str=None):
    if not month_str:
        month_str = date.today().strftime("%Y-%m")
    conn = get_conn()
    row = conn.execute(
        "SELECT day FROM shoot_day WHERE month=?", (month_str,)
    ).fetchone()
    conn.close()
    return row["day"] if row else None


def set_shoot_day(day_str):
    month_str = day_str[:7]
    conn = get_conn()
    conn.execute(
        "INSERT INTO shoot_day (month, day) VALUES (?,?) "
        "ON CONFLICT(month) DO UPDATE SET day=excluded.day",
        (month_str, day_str)
    )
    conn.commit()
    conn.close()


# ── Seed defaults ─────────────────────────────────────────────────────────────

def _seed_default_tasks():
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    conn.close()
    if count > 0:
        return

    defaults = [
        ("Review ophthalmology journal / latest guidelines", 0, "academics", 1, True),
        ("Study one surgical technique or case",             0, "academics", 1, True),
        ("Organise clinical notes from the week",            0, "academics", 2, True),
        ("Add 3 items to reading queue",                     0, "academics", 2, True),
        ("Plan 3 new content ideas",                         1, "content",   1, True),
        ("Write or finish one script",                       1, "content",   1, True),
        ("Update content calendar",                          1, "content",   2, True),
        ("Schedule / batch pending posts",                   1, "content",   2, True),
        ("Watch 2 saved videos from queue",                  2, "learning",  1, True),
        ("Read 20 pages (book / article)",                   2, "learning",  1, True),
        ("Journal: reflection + gratitude (10 min)",         2, "learning",  2, True),
        ("Workout or walk",                                  2, "learning",  2, True),
        ("Cut and edit main video project",                  3, "editing",   1, True),
        ("Audio cleanup + subtitles",                        3, "editing",   1, True),
        ("Export and review final cut",                      3, "editing",   2, True),
        ("Prep thumbnail + upload checklist",                3, "editing",   2, True),
        ("Review portfolio performance",                     4, "finance",   1, True),
        ("Read 2 financial / market articles",               4, "finance",   1, True),
        ("Update watchlist + notes",                         4, "finance",   2, True),
        ("Weekly investment journal entry",                  4, "finance",   2, True),
        ("Clear any carried-forward tasks",                  5, "flex",      1, True),
        ("Reply to pending messages",                        5, "flex",      2, True),
        ("Plan priorities for next week",                    5, "flex",      2, True),
        ("Weekly review: wins + learnings",                  6, "personal",  1, True),
        ("Family / rest / spirituality time",                6, "personal",  1, True),
        ("Prep desk + plan Monday",                          6, "personal",  2, True),
    ]

    conn = get_conn()
    for text, day_key, cat, pri, rec in defaults:
        conn.execute(
            "INSERT INTO tasks (text, day_key, category, priority, recurring) VALUES (?,?,?,?,?)",
            (text, day_key, cat, pri, int(rec))
        )
    conn.commit()
    conn.close()

# ── Daily Progress (persists tick-offs across reloads) ────────────────────────

def init_progress_table():
    """Create daily_progress table if not exists."""
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_progress (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            day_key    TEXT    NOT NULL,  -- e.g. 'friday', 'monday'
            task_id    TEXT    NOT NULL,  -- e.g. 'f1', 'm3'
            week_year  TEXT    NOT NULL,  -- e.g. '2026-W22'
            done       INTEGER DEFAULT 1,
            done_at    TEXT    DEFAULT (datetime('now')),
            UNIQUE(day_key, task_id, week_year)
        )
    """)
    conn.commit()
    conn.close()


def get_week_year():
    """Return current week string like '2026-W22'."""
    from datetime import date
    d = date.today()
    return f"{d.year}-W{d.isocalendar()[1]:02d}"


def mark_task_done_persistent(day_key, task_id):
    """Mark a checklist task as done for this week."""
    init_progress_table()
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO daily_progress (day_key, task_id, week_year) VALUES (?,?,?)",
        (day_key, task_id, get_week_year())
    )
    conn.commit()
    conn.close()


def unmark_task_done_persistent(day_key, task_id):
    """Unmark a checklist task."""
    init_progress_table()
    conn = get_conn()
    conn.execute(
        "DELETE FROM daily_progress WHERE day_key=? AND task_id=? AND week_year=?",
        (day_key, task_id, get_week_year())
    )
    conn.commit()
    conn.close()


def get_done_tasks_persistent(day_key):
    """Return set of task_ids done this week for a given day."""
    init_progress_table()
    conn = get_conn()
    rows = conn.execute(
        "SELECT task_id FROM daily_progress WHERE day_key=? AND week_year=?",
        (day_key, get_week_year())
    ).fetchall()
    conn.close()
    return {r["task_id"] for r in rows}


def reset_day_progress(day_key):
    """Reset all progress for a day this week."""
    init_progress_table()
    conn = get_conn()
    conn.execute(
        "DELETE FROM daily_progress WHERE day_key=? AND week_year=?",
        (day_key, get_week_year())
    )
    conn.commit()
    conn.close()


def mark_patient_done(week_year=None):
    """Mark this week's patient as done."""
    init_progress_table()
    if not week_year:
        week_year = get_week_year()
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO daily_progress (day_key, task_id, week_year) VALUES (?,?,?)",
        ("monday", "patient", week_year)
    )
    conn.commit()
    conn.close()


def is_patient_done(week_year=None):
    """Check if this week's patient is done."""
    init_progress_table()
    if not week_year:
        week_year = get_week_year()
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM daily_progress WHERE day_key='monday' AND task_id='patient' AND week_year=?",
        (week_year,)
    ).fetchone()
    conn.close()
    return row is not None


# ── Carry Forward ─────────────────────────────────────────────────────────────

def init_carry_table():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS carry_forward (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            task_text   TEXT NOT NULL,
            from_day    TEXT NOT NULL,
            to_day      INTEGER NOT NULL,
            week_year   TEXT NOT NULL,
            done        INTEGER DEFAULT 0,
            created_at  TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


def add_carry_forward(task_text, from_day, to_day_key):
    """Carry a task forward to another day."""
    init_carry_table()
    conn = get_conn()
    conn.execute(
        "INSERT INTO carry_forward (task_text, from_day, to_day, week_year) VALUES (?,?,?,?)",
        (task_text, from_day, to_day_key, get_week_year())
    )
    conn.commit()
    conn.close()


def get_carry_forward(to_day_key):
    """Get all carried tasks for a given day this week."""
    init_carry_table()
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM carry_forward WHERE to_day=? AND week_year=? AND done=0 ORDER BY created_at ASC",
        (to_day_key, get_week_year())
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_carry_done(carry_id):
    conn = get_conn()
    conn.execute("UPDATE carry_forward SET done=1 WHERE id=?", (carry_id,))
    conn.commit()
    conn.close()


def delete_carry(carry_id):
    conn = get_conn()
    conn.execute("DELETE FROM carry_forward WHERE id=?", (carry_id,))
    conn.commit()
    conn.close()
