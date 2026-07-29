# Kahuta Knights Armwrestling — Full Website

A multi-page Flask site: home page with logo hero + core team, an events
timeline, a rankings leaderboard, a full team roster, a contact page, and the
trials registration form (fee screenshot upload) all sharing one theme.

## File structure
```
kahuta_knights_site/
├── app.py                  # Routes + sample data (events, rankings, roster)
├── requirements.txt
├── Dockerfile
├── registrations.csv       # Created automatically on first form submission
├── templates/
│   ├── base.html           # Shared navbar + footer, all pages extend this
│   ├── home.html           # Hero (logo watermark) + core team cards
│   ├── events.html         # Timeline of tournaments/trials
│   ├── rankings.html       # Leaderboard tables by weight class
│   ├── team.html           # Full roster grid
│   ├── contact.html        # Phone / payment / location
│   └── register.html       # Trials registration form (same as before)
└── static/
    ├── css/style.css       # One shared gold/black knight theme
    ├── images/
    │   ├── logo.jpg        # Your uploaded crest
    │   ├── bg.png            # Your uploaded knight background
    │   ├── members/        # Put real athlete photos here
    │   └── gallery/        # Reserved if you add a gallery page later
    └── uploads/            # Fee-payment screenshots land here
```

## ⚠️ Placeholder content — replace before going live
Since no athlete photos, event list, or rankings were provided, the site ships
with sample data so every page has something to show:

- **Core team & roster** (`app.py`, `CORE_MEMBERS` / `TEAM_MEMBERS`): names,
  roles, and gold initial-circles stand in for real photos. Add photos to
  `static/images/members/` and swap the `<span>{{ member.initials }}</span>`
  block in `home.html` / `team.html` for an `<img>` tag once you have them.
- **Events** (`app.py`, `EVENTS`): sample tournament dates/locations — edit
  directly in `app.py`.
- **Rankings** (`app.py`, `RANKINGS`): sample standings by weight class —
  edit directly in `app.py`.
- **Contact page**: has real phone/payment details from your original form,
  but the Instagram/Facebook line is a placeholder — add real links.

Everything above lives as plain Python lists/dicts at the top of `app.py`,
so no database is needed to update it — just edit the values and redeploy.

## Run it locally
```bash
cd kahuta_knights_site
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Deploy
Works the same way as the registration-only version:
- **Render / Cloud Run**: the included `Dockerfile` is picked up automatically.
- **PythonAnywhere**: upload the folder, point the WSGI config at `app.py`,
  no Dockerfile needed there.

Reminder: on hosts without persistent storage (e.g. Render's free tier),
`registrations.csv` and `static/uploads/` can be wiped on restart. Use
PythonAnywhere (persistent disk) if you need registration data to survive
long-term, or move to a proper database/cloud storage later.
