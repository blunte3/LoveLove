from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import json
from collections import Counter
import re

app = Flask(__name__)

skills_db = {
    "Grounding": {
        "category": "Distress Tolerance",
        "definition": "A technique to help you stay present by focusing on physical sensations or immediate surroundings.",
        "steps": [
            "Notice 5 things you can see.",
            "Notice 4 things you can touch.",
            "Notice 3 things you can hear.",
            "Notice 2 things you can smell.",
            "Notice 1 thing you can taste."
        ],
        "enhancement": "breathe"
    },
    "Mindfulness": {
        "category": "Mindfulness",
        "definition": "Being aware of the present moment without judgment.",
        "steps": [
            "Focus on your breathing.",
            "Notice when your mind wanders.",
            "Gently bring your focus back to the breath."
        ],
        "enhancement": "reflection"
    },
    "Radical Acceptance": {
        "category": "Distress Tolerance",
        "definition": "Accepting reality as it is — even when painful — without trying to fight it.",
        "steps": [
            "Acknowledge the situation.",
            "Recognize what you can and can’t control.",
            "Choose acceptance rather than resistance."
        ],
        "enhancement": "audio"
    },
    "Reframing": {
        "category": "Goals & Values",
        "definition": "Changing your perspective on a situation to view it in a more constructive way.",
        "steps": [
            "Identify the negative thought.",
            "Ask: 'Is this 100% true?'",
            "Replace it with a more balanced thought."
        ],
        "enhancement": "reflection"
    },
    # ---- NEW SKILLS ----
    "Cognitive Reframing": {
        "category": "Cognitive Techniques",
        "definition": "Helps identify unhelpful thoughts and reinterpret them in a more balanced, realistic way to reduce stress or anxiety.",
        "steps": [
            "Notice a negative thought or assumption.",
            "Ask: 'Is this thought entirely accurate?'",
            "Reframe it into a more neutral or positive statement.",
            "Reflect on how this changes your emotions."
        ],
        "enhancement": "reflection"
    },
    "Progressive Muscle Relaxation": {
        "category": "Stress Management",
        "definition": "A relaxation technique that involves tensing and relaxing muscle groups one at a time to reduce physical tension and promote calm.",
        "steps": [
            "Find a quiet space and get comfortable.",
            "Tense a specific muscle group for about 5 seconds.",
            "Release the tension and focus on the feeling of relaxation.",
            "Move progressively through your body."
        ],
        "enhancement": "audio"
    }
}

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
    c.execute("PRAGMA table_info(entries)")
    columns = [col[1] for col in c.fetchall()]
    if "title" not in columns:
        c.execute("ALTER TABLE entries ADD COLUMN title TEXT")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    # include title
    c.execute("SELECT id, date, title, journal_type, content FROM entries ORDER BY id DESC")
    entries = c.fetchall()
    conn.close()

    decoded_entries = []
    for entry in entries:
        entry_id, date, title, journal_type, content = entry

        # Default title to date if missing or blank
        if not title or title.strip() == "":
            title = date

        # Create content preview (for non-Free Write entries)
        try:
            content_dict = json.loads(content)
            text_preview = content_dict.get("content") or next(iter(content_dict.values()), "")
            text_preview = (text_preview[:120] + "...") if len(text_preview) > 120 else text_preview
        except:
            text_preview = content

        decoded_entries.append((entry_id, date, title, journal_type, text_preview))

    return render_template("home.html", entries=decoded_entries)

@app.route("/new", methods=["GET", "POST"])
def new_entry():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        journal_type = request.form["journal_type"]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Default title to date only if not provided
        if not title:
            title = date

        entry_data = {key: value for key, value in request.form.items()}

        conn = sqlite3.connect("journal.db")
        c = conn.cursor()
        c.execute("INSERT INTO entries (date, title, journal_type, content) VALUES (?, ?, ?, ?)",
                  (date, title, journal_type, json.dumps(entry_data)))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))

    return render_template("new_entry.html")

@app.route("/analytics")
def analytics():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT date, journal_type, content FROM entries")
    rows = c.fetchall()
    conn.close()

    total_entries = len(rows)

    # --- 1. Entry Type Counts ---
    type_counts = {}
    for _, journal_type, _ in rows:
        type_counts[journal_type] = type_counts.get(journal_type, 0) + 1

    # --- 2. Combine all text for common words ---
    all_text = ""
    for _, _, content in rows:
        try:
            content_dict = json.loads(content)
            all_text += " ".join(content_dict.values()) + " "
        except:
            all_text += content + " "
    words = re.findall(r'\b[a-z]{3,}\b', all_text.lower())
    common_words = Counter(words).most_common(20)

    # --- 3. Weekly Writing Frequency (entries per weekday) ---
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly_counts = {d: 0 for d in weekdays}
    for date_str, _, _ in rows:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            weekly_counts[dt.strftime("%a")] += 1
        except:
            pass

    # --- 4. Sentiment Trend (dummy data for now) ---
    # In future, compute this using a sentiment analysis library (e.g., TextBlob or VADER)
    sentiment_trend = {}
    for i, (date_str, _, content) in enumerate(rows[-10:]):  # last 10 entries
        sentiment_trend[date_str.split(" ")[0]] = (i % 5 - 2) / 2  # dummy sentiment between -1 and +1

    # --- 5. Emotion Distribution (placeholder data) ---
    # Replace with your emotion detection logic if you have one
    emotion_counts = {
        "Joy": 10,
        "Sadness": 5,
        "Anger": 3,
        "Fear": 4,
        "Surprise": 2,
        "Neutral": 8
    }

    # --- 6. Words by Day of Week (average word count) ---
    words_by_day = {d: 0 for d in weekdays}
    counts_by_day = {d: 0 for d in weekdays}

    for date_str, _, content in rows:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            weekday = dt.strftime("%a")
            try:
                content_dict = json.loads(content)
                text = " ".join(content_dict.values())
            except:
                text = content
            word_count = len(re.findall(r'\b[a-z]{3,}\b', text.lower()))
            words_by_day[weekday] += word_count
            counts_by_day[weekday] += 1
        except:
            continue

    # Avoid divide by zero
    for day in words_by_day:
        if counts_by_day[day] > 0:
            words_by_day[day] = round(words_by_day[day] / counts_by_day[day], 1)

    # --- 7. Render Template ---
    return render_template(
        "analytics.html",
        total_entries=total_entries,
        type_counts=type_counts,
        common_words=common_words,
        weekly_counts=weekly_counts,
        sentiment_trend=sentiment_trend,
        emotion_counts=emotion_counts,
        words_by_day=words_by_day
    )


@app.route("/entry/<int:entry_id>")
def view_entry(entry_id):
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT date, journal_type, content FROM entries WHERE id = ?", (entry_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return "Entry not found.", 404

    date, journal_type, content = row
    try:
        entry_data = json.loads(content)
    except:
        entry_data = {"content": content}

    return render_template("entry.html", date=date, journal_type=journal_type, entry_data=entry_data, content=content)

@app.route("/skills")
def skills():
    return render_template("skills.html", skills=skills_db)


@app.route("/skill/<name>")
def skill_detail(name):
    skill = skills_db.get(name)
    if not skill:
        return render_template("skill_detail.html", skill={
            "name": name,
            "category": "Unknown",
            "definition": "Skill not found.",
            "how_to": [],
            "enhancements": {}
        })
    skill["name"] = name
    return render_template("skill_detail.html", skill=skill)

if __name__ == "__main__":
    app.run(debug=True)
