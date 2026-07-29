import os
import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "kahuta-knights-secret-key"
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
# ---------- Configuration ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
TEAM_DATA_FILE = os.path.join(BASE_DIR, "team_registrations.csv")
EVENT_DATA_FILE = os.path.join(BASE_DIR, "event_registrations.csv")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "xls", "csv", "jpg", "jpeg", "png", "gif"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB max upload

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
    },
    {
        "name": "M.Zain Ijaz",
        "weight_class": "-60kg Class",
        "initials": "ZI",
        "note": "Known for explosive starts and a strong top-roll technique.",
    },
    {
        "name": "Waqas Bhatti",
        "weight_class": "-80kg Class",
        "initials": "WB",
        "note": "Rising talent, undefeated in local trials this season.",
    },
    {
        "name": "Hamza Khan",
        "weight_class": "-80kg Class",
        "initials": "HK",
        "note": "Known for explosive starts and a strong top-roll technique.",
    },
    {
        "name": "Skiandar Satti",
        "weight_class": "80kg+ Class",
        "initials": "SS",
        "note": "Team strongman, and Coach",
    },
    {
        "name": "Sajjad Khan",
        "weight_class": "-70kg Class",
        "initials": "SK",
        "note": "Known for Strong toproll and Bone lock",
    },
]
# Normalize core members so they also render correctly on the /team grid
for m in TEAM_MEMBERS[:2]:
    m.setdefault("weight_class", "Core Team")
    m.setdefault("note", m.get("bio", ""))

EVENTS = [
    {
        "day": "14",
        "month": "August",
        "year": "2026",
        "title": " Armwrestling Championship ",
        "location": "International fitness Tycon Gym, Motor Chowk, Kahuta, Punjab",
        "description": "Open Tournment organized by Kahuta Knights at Nationals.",
        "status": "Upcoming",
    },
    
]

RANKINGS = [
    {
        "name": "-60kg Class",
        "rows": [
            {"rank": 1, "name": "Zain Ijaz",},
            {"rank": 2, "name": "Farhan",},
            {"rank": 3, "name": "Ayan", },
        ],
        "left_rows": [
            {"rank": 1, "name": "Zain Ijaz",},
            {"rank": 2, "name": "Meeshan Ali",},
            {"rank": 3, "name": "Farhan", },
        ],
    },
    {
        "name": "-70kg Class",
        "rows": [
            {"rank": 1, "name": "Abdullah Jan Sani",},
            {"rank": 2, "name": "Sajjad Khan",},
            {"rank": 3, "name": "Hamid", },
        ],
        "left_rows": [
            {"rank": 1, "name": "Sajjad",},
            {"rank": 2, "name": "Abdullah Jan",},
            {"rank": 3, "name": "Hamid", },
        ],
    },
    {
        "name": "-80kg Class",
        "rows": [
            {"rank": 1, "name": "Hamza Khan", },
            {"rank": 2, "name": "Sajjad Khan", },
            {"rank": 3, "name": "Abdull Rehman", },
        ],
        "left_rows": [
            {"rank": 1, "name": "Abdull Rehman", },
            {"rank": 2, "name": "Sajjad Khan", },
            {"rank": 3, "name": "Shams", },
        ],
    },
]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_csv(file_path, headers, row):
    """Append a row to a CSV file, creating headers if needed."""
    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)


def read_csv_rows(file_path):
    """Read CSV rows as dictionaries, or return an empty list if the file is missing."""
    if not os.path.isfile(file_path):
        return []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


@app.context_processor
def inject_globals():
    return {"current_year": datetime.now().year}


# ======================================================================
# ROUTES
# ======================================================================

@app.route("/")
def home():
    return render_template(
        "home.html", active="home",
        core_members=CORE_MEMBERS, team_members=TEAM_MEMBERS, events=EVENTS
    )


@app.route("/events")
def events():
    return render_template("events.html", active="events", events=EVENTS)


@app.route("/rankings")
def rankings():
    return render_template("rankings.html", active="rankings", rankings=RANKINGS)


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


@app.route("/admin/access", methods=["GET", "POST"])
def admin_access():
    target = request.args.get("target", "event")
    if request.method == "POST":
        password = request.form.get("password", "")
        target = request.form.get("target", "event")
        if password == ADMIN_PASSWORD:
            session["admin_authenticated"] = True
            if target == "team":
                return redirect(url_for("admin_team_registration"))
            return redirect(url_for("admin_event_registration"))
        flash("Incorrect password. Please try again.", "error")

    return render_template(
        "admin_access.html",
        active="admin",
        target=target,
    )


@app.route("/admin/event_registration")
def admin_event_registration():
    rows = read_csv_rows(EVENT_DATA_FILE)
    columns = rows[0].keys() if rows else ["Timestamp", "Full Name", "Phone", "Team Name", "Email", "Age", "Weight", "Screenshot File"]
    return render_template(
        "admin_registration.html",
        active="admin",
        page_title="Event Payment Verification",
        page_heading="Event Registration Verification",
        rows=rows,
        columns=columns,
        note="Review submitted tournament payments and participant details.",
    )


@app.route("/admin/team_registration")
def admin_team_registration():
    rows = read_csv_rows(TEAM_DATA_FILE)
    columns = rows[0].keys() if rows else ["Timestamp", "Full Name", "Phone", "Email", "Age", "Weight"]
    return render_template(
        "admin_registration.html",
        active="admin",
        page_title="Team Join Verification",
        page_heading="Team Registration Verification",
        rows=rows,
        columns=columns,
        note="Review team join requests before adding new members.",
    )


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
        save_csv(
            TEAM_DATA_FILE,
            ["Timestamp", "Full Name", "Phone", "Email", "Age", "Weight"],
            [
                datetime.now().isoformat(timespec="seconds"),
                full_name,
                phone,
                email,
                age,
                weight,
            ],
        )
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
