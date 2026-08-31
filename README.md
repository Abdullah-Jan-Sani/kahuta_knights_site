# Kahuta Knights Armwrestling — Full Website

## Features
- **Multi-Page Layout**: Includes Home, Team Roster, Rankings, Events, Contact, and Trials Registration pages.
- **Dynamic Content (No DB Required)**: Roster, events, and rankings are driven by simple Python dictionaries in `app.py`. Update the site by just changing the text in the file.
- **Registration System**: Collects athlete details and fee payment screenshots.
- **CSV Data Storage**: Automatically saves all trial registrations to `registrations.csv`.
- **Responsive Design**: Custom CSS that works seamlessly on desktop and mobile devices.

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


## Run it locally
```bash
cd kahuta_knights_site
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## How to Update Site Content
Because this site doesn't require a complex SQL database, updating content is incredibly easy. Open app.py in any text editor and look for the uppercase variables at the top:

CORE_MEMBERS & TEAM_MEMBERS: Edit names, weight classes, and stats here.

EVENTS: Add or remove upcoming tournaments and seminars.

RANKINGS: Update the top 2 pullers for each weight class.

Adding Photos: Right now, the site uses gold circles with initials as placeholders. Once you have photos of the team, add them to static/images/members/, and in team.html and home.html, replace the <div class="avatar-circle">...</div> with an <img src="..."> tag pointing to your image.

## Deploy
- **PythonAnywhere**: upload the folder, point the WSGI config at `app.py`,
  no Dockerfile needed there.

