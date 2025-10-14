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

# Home route
@app.route("/")
def home():
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT id, date, journal_type, content FROM entries ORDER BY id DESC")
    entries = c.fetchall()
    conn.close()
    return render_template("home.html", entries=entries)

# New entry route
@app.route("/new", methods=["GET", "POST"])
def new_entry():
    if request.method == "POST":
        journal_type = request.form["journal_type"]
        content = request.form["content"]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect("journal.db")
        c = conn.cursor()
        c.execute("INSERT INTO entries (date, journal_type, content) VALUES (?, ?, ?)", (date, journal_type, content))
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

    # Simple word frequency (across all entries)
    all_text = " ".join(content for _, content in rows).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_text)  # words >= 3 letters
    common_words = Counter(words).most_common(10)

    return render_template("analytics.html",
                           total_entries=total_entries,
                           type_counts=type_counts,
                           common_words=common_words)

if __name__ == "__main__":
    app.run(debug=True)
