from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB_FILE = "journal.db"

# ------------------------------
# Initialize database if not exists
# ------------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            journal_type TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ------------------------------
# Home Page
# ------------------------------
@app.route("/")
def home():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, date, journal_type, content FROM entries ORDER BY id DESC")
    entries = c.fetchall()
    conn.close()
    return render_template("home.html", entries=entries)

# ------------------------------
# New Entry Page
# ------------------------------
@app.route("/new", methods=["GET", "POST"])
def new_entry():
    if request.method == "POST":
        journal_type = request.form.get("journal_type")
        date = datetime.now().strftime("%Y-%m-%d %H:%M")

        # ------------------------------
        # Handle each journal type
        # ------------------------------
        if journal_type == "Free Write":
            content = request.form.get("content")

        elif journal_type == "Daily Journal - Morning":
            sleep_quality = request.form.get("sleep_quality", "")
            sleep_notes = request.form.get("sleep_notes", "")
            gratitudes = request.form.get("gratitudes", "")
            affirmations = request.form.get("affirmations", "")
            goals = request.form.get("goals", "")
            actions = request.form.get("actions", "")
            morning_freetext = request.form.get("morning_freetext", "")
            # Combine into single content string
            content = (
                f"Sleep Quality: {sleep_quality}\n"
                f"Notes: {sleep_notes}\n\n"
                f"Gratitudes:\n{gratitudes}\n\n"
                f"Affirmations:\n{affirmations}\n\n"
                f"Goals:\n{goals}\n\n"
                f"Action Plans:\n{actions}\n\n"
                f"Free Thoughts:\n{morning_freetext}"
            )

        elif journal_type == "Daily Journal - Night":
            night_gratitudes = request.form.get("night_gratitudes", "")
            positives = request.form.get("positives", "")
            goal_progress = request.form.get("goal_progress", "")
            night_freetext = request.form.get("night_freetext", "")
            content = (
                f"Gratitudes: {night_gratitudes}\n\n"
                f"Positive Actions/Thoughts: {positives}\n\n"
                f"Goal Progress: {goal_progress}\n\n"
                f"Free Thoughts: {night_freetext}"
            )

        elif journal_type == "Situational Journal":
            situation = request.form.get("situation", "")
            category = request.form.get("situation_category", "")
            feelings = request.form.get("feelings", "")
            used_skills = request.form.get("used_skills", "")
            skills_used = request.form.get("skills_used", "")
            after_effect = request.form.get("after_effect", "")
            content = (
                f"Situation: {situation}\n"
                f"Category: {category}\n\n"
                f"Feelings: {feelings}\n\n"
                f"Used Skills: {used_skills}\n"
                f"Skills Used: {skills_used}\n\n"
                f"After Effect: {after_effect}"
            )

        else:
            content = request.form.get("content", "")

        # ------------------------------
        # Save to database
        # ------------------------------
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO entries (date, journal_type, content) VALUES (?, ?, ?)",
                  (date, journal_type, content))
        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    return render_template("new_entry.html")

# ------------------------------
# Analytics Placeholder
# ------------------------------
@app.route("/analytics")
def analytics():
    return "<h1>Analytics page coming soon!</h1><p>Will visualize journal patterns, mood trends, etc.</p>"

# ------------------------------
# Run the app
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
