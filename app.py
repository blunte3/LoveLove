from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import json
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

# Home route
@app.route("/")
def home():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT id, date, journal_type, content FROM entries ORDER BY id DESC")
    entries = c.fetchall()
    conn.close()

    # Decode JSON if possible for display
    decoded_entries = []
    for entry in entries:
        try:
            content_dict = json.loads(entry[3])
            text_preview = content_dict.get("content") or next(iter(content_dict.values()), "")
            text_preview = (text_preview[:120] + "...") if len(text_preview) > 120 else text_preview
        except:
            text_preview = entry[3]
        decoded_entries.append((entry[0], entry[1], entry[2], text_preview))

    return render_template("home.html", entries=decoded_entries)

# New entry route
@app.route("/new", methods=["GET", "POST"])
def new_entry():
    if request.method == "POST":
        journal_type = request.form["journal_type"]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store all form data as JSON
        entry_data = {key: value for key, value in request.form.items()}

        conn = sqlite3.connect("journal.db")
        c = conn.cursor()
        c.execute("INSERT INTO entries (date, journal_type, content) VALUES (?, ?, ?)",
                  (date, journal_type, json.dumps(entry_data)))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))

    return render_template("new_entry.html")

# Analytics route
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

    # Combine all text content
    all_text = ""
    for _, content in rows:
        try:
            content_dict = json.loads(content)
            all_text += " ".join(content_dict.values()) + " "
        except:
            all_text += content + " "

    words = re.findall(r'\b[a-z]{3,}\b', all_text.lower())
    common_words = Counter(words).most_common(10)

    return render_template("analytics.html",
                           total_entries=total_entries,
                           type_counts=type_counts,
                           common_words=common_words)

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

    # Parse JSON safely
    import json
    try:
        entry_data = json.loads(content)
    except:
        entry_data = {"content": content}

    return render_template("entry.html", date=date, journal_type=journal_type, entry_data=entry_data, content=content)

if __name__ == "__main__":
    app.run(debug=True)
