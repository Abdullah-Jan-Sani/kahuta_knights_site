import os
import csv
import json
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app.secret_key = os.environ.get("SECRET_KEY")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

# ---------- Configuration ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
TEAM_DATA_FILE = os.path.join(BASE_DIR, "team_registrations.csv")
EVENT_DATA_FILE = os.path.join(BASE_DIR, "event_registrations.csv")
RANKINGS_FILE = os.path.join(BASE_DIR, "rankings.json")
EVENTS_FILE = os.path.join(BASE_DIR, "events.json")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "csv", "jpg", "jpeg", "png", "gif"}
ALLOWED_POSTER_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
MAX_CONTENT_LENGTH = 15 * 1024 * 1024  # 15 MB max upload (posters/screenshots only, no more video uploads)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ======================================================================
# PLACEHOLDER CONTENT
# Everything below is sample data so the site has something to show.
# Replace with real athletes, events, and standings whenever you're ready.
# ======================================================================

CORE_MEMBERS = [
    {
        "name": "Abdullah Jan Sani",
        "role": "Founder & Head Coach",
        "initials": "Aj",
        "bio": "Founded Kahuta Knights and leads training, trials, and tournament strategy.",
    },
    {
        "name": "M.Zain Ijaz",
        "role": "Team Captain",
        "initials": "ZI",
        "bio": "Reigning regional champion in the 80kg class, leads the roster into every event.",
    },
]

TEAM_MEMBERS = CORE_MEMBERS + [
    {
        "name": "Abdullah Jan Sani",
        "weight_class": "-70kg Class",
        "initials": "Aj",
        "note": "Known for strong and Defensive Hook technique.",
        "photo_filename": "abdullah.png"
    },
    {
        "name": "M.Zain Ijaz",
        "weight_class": "-60kg Class",
        "initials": "ZI",
        "note": "Known for explosive starts and a strong top-roll technique.",
        "photo_filename": "zain.png"
    },
    {
        "name": "Waqas Bhatti",
        "weight_class": "-80kg Class",
        "initials": "WB",
        "note": "Rising talent, undefeated in local trials this season.",
        "photo_filename": "waqas.png"
    },
    {
        "name": "Hamza Khan",
        "weight_class": "-80kg Class",
        "initials": "HK",
        "note": "Known for explosive starts and a strong top-roll technique.",
        "photo_filename": "hamza.png"
    },
    {
        "name": "Skiandar Satti",
        "weight_class": "80kg+ Class",
        "initials": "SS",
        "note": "Team strongman, and Coach",
        "photo_filename": "sikandar.png"
    },
    {
        "name": "Sajjad Khan",
        "weight_class": "-70kg Class",
        "initials": "SK",
        "note": "Known for Strong toproll and Bone lock",
        "photo_filename": "sajjad.png"
    },
    {
        "name": "Farhan",
        "initials": "F",
        "weight_class": "-60KG CLASS",
        "note": "Known for Strong hook and hand control.",
        "photo_filename": "farhan.png"
    },
]
# Normalize core members so they also render correctly on the /team grid
for m in TEAM_MEMBERS[:2]:
    m.setdefault("weight_class", "Core Team")
    m.setdefault("note", m.get("bio", ""))

# Default events used only the very first time the app runs (to seed events.json).
# After that, all reads/writes go through EVENTS_FILE so admin edits persist.
DEFAULT_EVENTS = [
    {
        "day": "14",
        "month": "August",
        "year": "2026",
        "title": " Armwrestling Championship ",
        "location": "International fitness Tycon Gym, Motor Chowk, Kahuta, Punjab",
        "description": "Open Tournment organized by Kahuta Knights at Nationals.",
        "status": "Upcoming",
        "event_type": "tournament",
        "poster_filename": "",
        "video_links": {"youtube": "", "tiktok": "", "instagram": ""},
    },

]

# Default rankings used only the very first time the app runs (to seed rankings.json).
# After that, all reads/writes go through RANKINGS_FILE so admin edits persist.
DEFAULT_RANKINGS = [
    {
        "name": "-60kg Class",
        "rows": [
            {"rank": 1, "name": "Zain Ijaz"},
            {"rank": 2, "name": "Ayan"},
            {"rank": 3, "name": "Farhan"},
            {"rank": 4, "name": "Meeshan Ali"},
        ],
        "left_rows": [
            {"rank": 1, "name": "Zain Ijaz"},
            {"rank": 2, "name": "Meeshan Ali"},
            {"rank": 3, "name": "Farhan"},
            {"rank": 4, "name": "Ahad"},
        ],
    },
    {
        "name": "-70kg Class",
        "rows": [
            {"rank": 1, "name": "Abdullah Jan "},
            {"rank": 2, "name": "Sajjad Khan"},
            {"rank": 3, "name": "Hamid"},
            {"rank": 4, "name": "Zain Ijaz"},
        ],
        "left_rows": [
            {"rank": 1, "name": "Sajjad Khan"},
            {"rank": 2, "name": "Shahwaiz"},
            {"rank": 3, "name": "Abdullah Khan"},
            {"rank": 4, "name": "Abdullah Jan"},
            
        ],
    },
    {
        "name": "Open Class",
        "rows": [
            {"rank": 1, "name": "Hamza Khan"},
            {"rank": 2, "name": "Sajjad Khan"},
            {"rank": 3, "name": "Abdull Rehman"},
            {"rank": 4, "name": "Shehzad Khan"},
        ],
        "left_rows": [
            {"rank": 1, "name": "Abdull Rehman"},
            {"rank": 2, "name": "Shamas Hashmi"},
            {"rank": 3, "name": "Shehzad Khan"},
            {"rank": 4, "name": "Sajjad Khan"},
        ],
    },
]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_poster(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_POSTER_EXTENSIONS


def save_csv(file_path, headers, row):
    """Append a row to a CSV file, creating headers if needed."""
    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)


def save_csv_rows(file_path, fieldnames, rows):
    """Write a full list of CSV rows with explicit headers."""
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_team_registration(row):
    """Persist team registration rows and include an approval status."""
    rows = read_csv_rows(TEAM_DATA_FILE)
    for existing_row in rows:
        existing_row.setdefault("Status", "Pending")

    row.setdefault("Status", "Pending")
    rows.append(row)
    save_csv_rows(
        TEAM_DATA_FILE,
        ["Timestamp", "Full Name", "Phone", "Email", "Age", "Weight", "Status"],
        rows,
    )


def read_csv_rows(file_path):
    """Read CSV rows as dictionaries, or return an empty list if the file is missing."""
    if not os.path.isfile(file_path):
        return []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_rankings():
    """Load rankings from rankings.json, seeding it with defaults on first run."""
    if not os.path.isfile(RANKINGS_FILE):
        save_rankings(DEFAULT_RANKINGS)
        return DEFAULT_RANKINGS
    with open(RANKINGS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Normalize legacy 'arrow' key to 'move' and ensure every entry has a move value
    changed = False
    for category in data:
        for key in ("rows", "left_rows"):
            for entry in category.get(key, []):
                if "move" not in entry and "arrow" in entry:
                    entry["move"] = entry.pop("arrow")
                    changed = True
                if "move" not in entry:
                    entry["move"] = "none"
                    changed = True

    # Persist normalization so templates and future edits see a consistent key
    if changed:
        save_rankings(data)

    return data


def save_rankings(data):
    """Persist rankings to rankings.json."""
    with open(RANKINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _event_sort_key(event):
    """
    Groups Upcoming (0) first, then Completed (1).
    For Upcoming: sorts chronologically ascending (soonest date first at top).
    For Completed: sorts chronologically descending (most recent past date at the top of the completed section).
    """
    status = event.get("status", "Upcoming")
    status_rank = 1 if status == "Completed" else 0
    
    try:
        date_obj = datetime.strptime(
            f"{event.get('day', '1')} {event.get('month', 'January')} {event.get('year', '1970')}",
            "%d %B %Y",
        )
        timestamp = date_obj.timestamp()
    except ValueError:
        timestamp = 0

    # If upcoming, we want smaller timestamps first (ascending -> positive timestamp)
    # If completed, we want to control their internal order too. 
    # Returning a tuple where status comes first ensures Upcoming is always above Completed.
    if status_rank == 0:
        return (0, timestamp)     # Soonest upcoming date comes first
    else:
        return (1, -timestamp)    # Reverse chronological for completed items at the bottom


def load_events():
    """Load events from events.json, seeding it with defaults on first run.
    Returns events sorted with Upcoming first (soonest first at the top), then Completed."""
    if not os.path.isfile(EVENTS_FILE):
        save_events(DEFAULT_EVENTS)
        data = DEFAULT_EVENTS
    else:
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
    # Sort by status group first (Upcoming = 0, Completed = 1), 
    # then chronologically (earliest/soonest dates first)
    return sorted(data, key=_event_sort_key, reverse=False)

def save_events(data):
    """Persist events to events.json."""
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def login_required(view_func):
    """Redirect to the admin login screen if the session isn't authenticated."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            flash("Please log in as admin to continue.", "error")
            return redirect(url_for("admin_access", target=request.endpoint))
        return view_func(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}


# ======================================================================
# PUBLIC ROUTES
# ======================================================================

@app.route("/")
def home():
    events = load_events()
    nearest_tournament = next(
        (
            event for event in events
            if event.get("status") == "Upcoming" and event.get("event_type") == "tournament"
        ),
        None,
    )
    return render_template(
        "home.html",
        active="home",
        core_members=CORE_MEMBERS,
        team_members=TEAM_MEMBERS,
        events=events,
        nearest_tournament=nearest_tournament,
    )


@app.route("/events")
def events():
    return render_template(
        "events.html",
        active="events",
        events=load_events(),
        is_admin=bool(session.get("admin_authenticated")),
    )


@app.route("/rankings")
def rankings():
    return render_template(
        "rankings.html",
        active="rankings",
        rankings=load_rankings(),
        is_admin=bool(session.get("admin_authenticated")),
    )


@app.route("/team")
def team():
    return render_template("team.html", active="team", team_members=TEAM_MEMBERS)


@app.route("/contact")
def contact():
    return render_template("contact.html", active="contact")


@app.route("/register", methods=["GET"])
def register():
    return render_template(
        "register.html",
        active="register",
        form_type="team",
        page_title="Join The Team",
        page_description="Fill in your details to join Kahuta Knights.",
        submit_label="Join Now"
    )


@app.route("/register-event", methods=["GET"])
def register_event():
    return render_template(
        "register.html",
        active="register",
        form_type="event",
        page_title="Event Registration",
        page_description="Sign up for the tournament and upload your registration fee proof.",
        submit_label="Register for Event"
    )


# ======================================================================
# ADMIN AUTH
# ======================================================================

@app.route("/admin/access", methods=["GET", "POST"])
def admin_access():
    target = request.args.get("target", "events")

    if request.method == "POST":
        password = request.form.get("password", "")
        target = request.form.get("target", "events")
        if password == ADMIN_PASSWORD:
            session["admin_authenticated"] = True
            if target == "team":
                return redirect(url_for("admin_team_registration"))
            if target == "rankings" or target == "admin_rankings":
                return redirect(url_for("admin_rankings"))
            return redirect(url_for("admin_events"))
        flash("Incorrect password. Please try again.", "error")
    elif session.get("admin_authenticated"):
        flash("Please re-enter the admin password to continue.", "error")

    return render_template(
        "admin_access.html",
        active="admin",
        target=target,
    )


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_authenticated", None)
    flash("Logged out.", "success")
    return redirect(url_for("home"))


@app.route("/admin/event_registration")
@login_required
def admin_event_registration():
    rows = read_csv_rows(EVENT_DATA_FILE)
    columns = rows[0].keys() if rows else ["Timestamp", "Full Name", "Phone", "Team Name", "Email", "Age", "Weight", "Screenshot File"]
    return render_template(
        "admin_registration.html",
        active="admin",
        admin_tab="event_registration",
        page_title="Event Payment Verification",
        page_heading="Event Registration Verification",
        rows=rows,
        columns=columns,
        note="Review submitted tournament payments and participant details.",
    )


@app.route("/admin/team_registration")
@login_required
def admin_team_registration():
    rows = read_csv_rows(TEAM_DATA_FILE)
    for index, row in enumerate(rows):
        row.setdefault("Status", "Pending")
        row["_row_index"] = index

    if rows:
        columns = [c for c in rows[0].keys() if not c.startswith("_")]
        if "Actions" not in columns:
            columns.append("Actions")
    else:
        columns = ["Timestamp", "Full Name", "Phone", "Email", "Age", "Weight", "Status", "Actions"]

    return render_template(
        "admin_registration.html",
        active="admin",
        admin_tab="team_registration",
        page_title="Team Join Verification",
        page_heading="Team Registration Verification",
        rows=rows,
        columns=columns,
        note="Review team join requests before adding new members.",
    )


@app.route("/admin/team_registration/<int:row_index>/<action>", methods=["POST"])
@login_required
def admin_team_registration_action(row_index, action):
    rows = read_csv_rows(TEAM_DATA_FILE)
    if not (0 <= row_index < len(rows)):
        flash("Team registration not found.", "error")
        return redirect(url_for("admin_team_registration"))

    for row in rows:
        row.setdefault("Status", "Pending")

    if action == "approve":
        rows[row_index]["Status"] = "Approved"
        flash("Team registration approved.", "success")
    elif action == "reject":
        rows[row_index]["Status"] = "Rejected"
        flash("Team registration rejected.", "success")
    else:
        flash("Invalid action.", "error")
        return redirect(url_for("admin_team_registration"))

    save_csv_rows(
        TEAM_DATA_FILE,
        ["Timestamp", "Full Name", "Phone", "Email", "Age", "Weight", "Status"],
        rows,
    )
    return redirect(url_for("admin_team_registration"))


# ======================================================================
# ADMIN: RANKINGS MANAGEMENT
# ======================================================================

@app.route("/admin/rankings")
@login_required
def admin_rankings():
    return render_template(
        "admin_rankings.html",
        active="admin",
        admin_tab="rankings",
        rankings=load_rankings(),
    )


@app.route("/admin/rankings/category/add", methods=["POST"])
@login_required
def admin_rankings_add_category():
    name = request.form.get("category_name", "").strip()
    if not name:
        flash("Category name is required.", "error")
        return redirect(url_for("admin_rankings"))

    data = load_rankings()
    data.append({"name": name, "rows": [], "left_rows": []})
    save_rankings(data)
    flash(f'Added category "{name}".', "success")
    return redirect(url_for("admin_rankings"))


@app.route("/admin/rankings/category/<int:cat_index>/delete", methods=["POST"])
@login_required
def admin_rankings_delete_category(cat_index):
    data = load_rankings()
    if 0 <= cat_index < len(data):
        removed = data.pop(cat_index)
        save_rankings(data)
        flash(f'Deleted category "{removed["name"]}".', "success")
    else:
        flash("Category not found.", "error")
    return redirect(url_for("admin_rankings"))


@app.route("/admin/rankings/<int:cat_index>/<side>/add", methods=["POST"])
@login_required
def admin_rankings_add_row(cat_index, side):
    side = "rows" if side == "right" else "left_rows"
    rank = request.form.get("rank", "").strip()
    name = request.form.get("name", "").strip()
    move = request.form.get("move", "none").strip()

    data = load_rankings()
    if not (0 <= cat_index < len(data)):
        flash("Category not found.", "error")
        return redirect(url_for("admin_rankings"))
    if not name or not rank:
        flash("Rank and name are required.", "error")
        return redirect(url_for("admin_rankings"))

    try:
        rank = int(rank)
    except ValueError:
        flash("Rank must be a number.", "error")
        return redirect(url_for("admin_rankings"))

    data[cat_index].setdefault(side, []).append({"rank": rank, "name": name, "move": move})
    data[cat_index][side].sort(key=lambda r: r["rank"])
    save_rankings(data)
    flash("Wrestler added.", "success")
    return redirect(url_for("admin_rankings"))


@app.route("/admin/rankings/<int:cat_index>/<side>/<int:row_index>/edit", methods=["POST"])
@login_required
def admin_rankings_edit_row(cat_index, side, row_index):
    side = "rows" if side == "right" else "left_rows"
    rank = request.form.get("rank", "").strip()
    name = request.form.get("name", "").strip()
    move = request.form.get("move", "none").strip()

    data = load_rankings()
    if not (0 <= cat_index < len(data)) or not (0 <= row_index < len(data[cat_index].get(side, []))):
        flash("Entry not found.", "error")
        return redirect(url_for("admin_rankings"))
    if not name or not rank:
        flash("Rank and name are required.", "error")
        return redirect(url_for("admin_rankings"))

    try:
        rank = int(rank)
    except ValueError:
        flash("Rank must be a number.", "error")
        return redirect(url_for("admin_rankings"))

    # Preserve other keys if present, but update rank, name, and move
    entry = data[cat_index][side][row_index]
    entry["rank"] = rank
    entry["name"] = name
    entry["move"] = move
    data[cat_index][side][row_index] = entry
    data[cat_index][side].sort(key=lambda r: r["rank"])
    save_rankings(data)
    flash("Ranking updated.", "success")
    return redirect(url_for("admin_rankings"))


@app.route("/admin/rankings/<int:cat_index>/<side>/<int:row_index>/delete", methods=["POST"])
@login_required
def admin_rankings_delete_row(cat_index, side, row_index):
    side = "rows" if side == "right" else "left_rows"
    data = load_rankings()
    if 0 <= cat_index < len(data) and 0 <= row_index < len(data[cat_index].get(side, [])):
        removed = data[cat_index][side].pop(row_index)
        save_rankings(data)
        flash(f'Removed "{removed["name"]}".', "success")
    else:
        flash("Entry not found.", "error")
    return redirect(url_for("admin_rankings"))


# ======================================================================
# ADMIN: EVENTS MANAGEMENT
# ======================================================================

def _save_uploaded_file(file_storage, prefix):
    """Save an uploaded file with a timestamped, sanitized filename. Returns the stored filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    safe_name = secure_filename(file_storage.filename)
    stored_filename = f"{prefix}_{timestamp}_{safe_name}"
    file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], stored_filename))
    return stored_filename


def _delete_uploaded_file(filename):
    """Remove a previously uploaded file from disk, ignoring if it's already gone."""
    if not filename:
        return
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass


@app.route("/admin/events")
@login_required
def admin_events():
    return render_template(
        "admin_events.html",
        active="admin",
        admin_tab="events",
        events=load_events(),
    )


@app.route("/admin/events/add", methods=["POST"])
@login_required
def admin_events_add():
    event_type = request.form.get("event_type", "tournament")
    day = request.form.get("day", "").strip()
    month = request.form.get("month", "").strip()
    year = request.form.get("year", "").strip()
    title = request.form.get("title", "").strip()
    location = request.form.get("location", "").strip()
    description = request.form.get("description", "").strip()
    status = request.form.get("status", "Upcoming")

    if not (day and month and year and title):
        flash("Day, month, year, and title are required.", "error")
        return redirect(url_for("admin_events"))

    poster_filename = ""
    poster = request.files.get("poster")
    if poster and poster.filename:
        if not allowed_poster(poster.filename):
            flash("Poster must be an image file (jpg, png, gif, webp).", "error")
            return redirect(url_for("admin_events"))
        poster_filename = _save_uploaded_file(poster, "poster")

    video_links = {"youtube": "", "tiktok": "", "instagram": ""}
    if event_type == "super_fight":
        video_links["youtube"] = request.form.get("youtube_link", "").strip()
        video_links["tiktok"] = request.form.get("tiktok_link", "").strip()
        video_links["instagram"] = request.form.get("instagram_link", "").strip()

    data = load_events()
    data.append({
        "day": day,
        "month": month,
        "year": year,
        "title": title,
        "location": location,
        "description": description,
        "status": status,
        "event_type": event_type,
        "poster_filename": poster_filename,
        "video_links": video_links,
    })
    save_events(data)
    flash(f'Added event "{title}".', "success")
    return redirect(url_for("admin_events"))


@app.route("/admin/events/<int:event_index>/edit", methods=["POST"])
@login_required
def admin_events_edit(event_index):
    data = load_events()
    if not (0 <= event_index < len(data)):
        flash("Event not found.", "error")
        return redirect(url_for("admin_events"))

    event = data[event_index]
    event["event_type"] = request.form.get("event_type", event.get("event_type", "tournament"))
    event["day"] = request.form.get("day", "").strip() or event.get("day", "")
    event["month"] = request.form.get("month", "").strip() or event.get("month", "")
    event["year"] = request.form.get("year", "").strip() or event.get("year", "")
    event["title"] = request.form.get("title", "").strip() or event.get("title", "")
    event["location"] = request.form.get("location", "").strip()
    event["description"] = request.form.get("description", "").strip()
    event["status"] = request.form.get("status", event.get("status", "Upcoming"))

    poster = request.files.get("poster")
    if poster and poster.filename:
        if not allowed_poster(poster.filename):
            flash("Poster must be an image file (jpg, png, gif, webp).", "error")
            return redirect(url_for("admin_events"))
        _delete_uploaded_file(event.get("poster_filename", ""))
        event["poster_filename"] = _save_uploaded_file(poster, "poster")

    if event["event_type"] == "super_fight":
        event["video_links"] = {
            "youtube": request.form.get("youtube_link", "").strip(),
            "tiktok": request.form.get("tiktok_link", "").strip(),
            "instagram": request.form.get("instagram_link", "").strip(),
        }
    else:
        # Not a super fight: clear any video links this event might already have.
        event["video_links"] = {"youtube": "", "tiktok": "", "instagram": ""}

    data[event_index] = event
    save_events(data)
    flash("Event updated.", "success")
    return redirect(url_for("admin_events"))


@app.route("/admin/events/<int:event_index>/delete", methods=["POST"])
@login_required
def admin_events_delete(event_index):
    data = load_events()
    if 0 <= event_index < len(data):
        removed = data.pop(event_index)
        _delete_uploaded_file(removed.get("poster_filename", ""))
        save_events(data)
        flash(f'Deleted event "{removed["title"]}".', "success")
    else:
        flash("Event not found.", "error")
    return redirect(url_for("admin_events"))


# ======================================================================
# REGISTRATION SUBMISSION
# ======================================================================

@app.route("/submit", methods=["POST"])
def submit():
    form_type = request.form.get("form_type", "team")
    full_name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    team_name = request.form.get("team_name", "").strip()
    age = request.form.get("age", "").strip()
    weight = request.form.get("weight", "").strip()
    screenshot = request.files.get("screenshot")

    errors = []
    if not full_name:
        errors.append("Full name is required.")
    if not phone:
        errors.append("Phone number is required.")
    if form_type == "team" and not email:
        errors.append("Email is required for team registration.")
    if form_type == "event":
        if not team_name:
            errors.append("Team name is required for event registration.")
        if not email:
            errors.append("Email is required for event registration.")
        if not screenshot or screenshot.filename == "":
            errors.append("Registration fee screenshot is required.")
        elif not allowed_file(screenshot.filename):
            errors.append("Screenshot file type not allowed.")

    if errors:
        for e in errors:
            flash(e, "error")
        return redirect(url_for("register_event" if form_type == "event" else "register"))

    stored_filename = ""
    if form_type == "event":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = secure_filename(screenshot.filename)
        stored_filename = f"{timestamp}_{safe_name}"
        screenshot.save(os.path.join(app.config["UPLOAD_FOLDER"], stored_filename))

    if form_type == "team":
        save_team_registration({
            "Timestamp": datetime.now().isoformat(timespec="seconds"),
            "Full Name": full_name,
            "Phone": phone,
            "Email": email,
            "Age": age,
            "Weight": weight,
        })
    else:
        save_csv(
            EVENT_DATA_FILE,
            ["Timestamp", "Full Name", "Phone", "Team Name", "Email", "Age", "Weight", "Screenshot File"],
            [
                datetime.now().isoformat(timespec="seconds"),
                full_name,
                phone,
                team_name,
                email,
                age,
                weight,
                stored_filename,
            ],
        )

    flash("Registration submitted successfully!", "success")
    return redirect(url_for("register_event" if form_type == "event" else "register"))


if __name__ == "__main__":
    app.run(debug=True)