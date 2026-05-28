# One Thing Forward — Personal Life OS

A calm, minimal personal dashboard built for a doctor + content creator + investor.

## Project Structure

```
one-thing-forward/
├── app.py                  ← Main Streamlit app (run this)
├── requirements.txt
├── credentials.json        ← Google Calendar (you add this — see setup)
├── data/
│   └── otf.db              ← SQLite database (auto-created on first run)
└── modules/
    ├── __init__.py
    ├── database.py         ← All SQLite operations
    ├── styles.py           ← All CSS + day config
    ├── calendar_api.py     ← Google Calendar integration
    └── day_views.py        ← Each day's unique dashboard
```

## Quick Start (Local)

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/one-thing-forward.git
cd one-thing-forward

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

The database is created automatically on first run with your default tasks pre-loaded.

## Google Calendar Setup (Optional)

1. Go to https://console.cloud.google.com
2. Create a project → enable **Google Calendar API**
3. Go to **Credentials** → Create **OAuth 2.0 Client ID** → Desktop App
4. Download the JSON file → rename to `credentials.json` → place in project root
5. Run the app → a browser window opens for Google sign-in
6. After sign-in, `token.json` is created automatically

The app works fully without calendar — that section just shows a friendly message.

## Weekly System

| Day       | Theme                  | Key Modules                          |
|-----------|------------------------|--------------------------------------|
| Monday    | Academics              | Task list, reading queue             |
| Tuesday   | Content Engine         | Quick capture, pipeline, ideas vault |
| Wednesday | Self Help & Growth     | Watch queue, reading, journaling     |
| Thursday  | Video Editing          | Editing pipeline, distraction-free   |
| Friday    | Finance & Markets      | Watchlist, holdings, research notes  |
| Saturday  | Flex / Catch-up        | Carried tasks, captures, admin       |
| Sunday    | Personal / Shoot Day   | Rest OR monthly shoot day checklist  |

## Sidebar Navigation

- **Today** — Dynamic day dashboard (auto-detects weekday)
- **All Tasks** — Full weekly task view
- **Captures** — Quick idea inbox
- **Content Pipeline** — Full content OS
- **Finance** — Watchlist, holdings, research
- **Watch Queue** — YouTube / learning queue
- **Settings** — Google Calendar setup, shoot day config

## Extending Later

- Add stock price fetching (yfinance)
- Add Notion sync
- Add mobile PWA wrapper
- Add weekly email digest
- Export data to CSV
