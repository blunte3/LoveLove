from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
from collections import Counter
import re

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    journal_type TEXT,
                    content TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ------------------------------
# Home route
# ------------------------------
@app.route("/")
def home():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT id, date, journal_type, content FROM entries ORDER BY id DESC")
    entries = c.fetchall()
    conn.close()
    return render_template("home.html", entries=entries)

# ------------------------------
# New entry route
# ------------------------------
@app.route("/new", methods=["GET", "POST"])
def new_entry():
    if request.method == "POST":
        journal_type = request.form.get("journal_type")
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Handle each journal type and combine its inputs into a single string
        if journal_type == "Free Write":
            content = request.form.get("content", "")

        elif journal_type == "Daily Journal - Morning":
            sleep_quality = request.form.get("sleep_quality", "")
            sleep_notes = request.form.get("sleep_notes", "")
            gratitudes = request.form.get("gratitudes", "")
            affirmations = request.form.get("affirmations", "")
            goals = request.form.get("goals", "")
            actions = request.form.get("actions", "")
            morning_freetext = request.form.get("morning_freetext", "")
            content = (
                f"🌅 Daily Journal - Morning\n"
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
                f"🌙 Daily Journal - Night\n"
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
                f"🧠 Situational Journal\n"
                f"Situation: {situation}\n"
                f"Category: {category}\n\n"
                f"Feelings: {feelings}\n\n"
                f"Used Skills: {used_skills}\n"
                f"Skills Used: {skills_used}\n\n"
                f"After Effect: {after_effect}"
            )

        else:
            # fallback in case form type not recognized
            content = "No content submitted."

        # Save entry
        conn = sqlite3.connect("journal.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO entries (date, journal_type, content) VALUES (?, ?, ?)",
            (date, journal_type, content)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    return render_template("new_entry.html")

# ------------------------------
# Analytics route
# ------------------------------
@app.route("/analytics")
def analytics():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT journal_type, content FROM entries")
    rows = c.fetchall()
    conn.close()

    total_entries = len(rows)

    # Count entries per type
    type_counts = {}
    for journal_type, _ in rows:
        type_counts[journal_type] = type_counts.get(journal_type, 0) + 1

    # Word frequency across all entries
    all_text = " ".join(content for _, content in rows).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_text)  # words >= 3 letters
    common_words = Counter(words).most_common(10)

    return render_template(
        "analytics.html",
        total_entries=total_entries,
        type_counts=type_counts,
        common_words=common_words
    )

# ------------------------------
# Run app
# ------------------------------
if __name__ == "__main__":
    app.run(debug=True)
