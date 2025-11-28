from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3
from datetime import datetime, timedelta
import json
from collections import Counter
import re

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: TextBlob not installed. Installing sentiment analysis requires: pip install textblob")

app = Flask(__name__)

skills_db = {
    "Coping Thoughts": {
        "category": "Emotion Regulation",
        "tags": ["cognition", "reframe", "self-talk"],
        "definition": "Short, structured ways to notice and change unhelpful thinking patterns to reduce distress.",
        "how_to": [
            "Notice the automatic negative thought.",
            "Label it (e.g., 'catastrophizing').",
            "Ask for evidence for/against it.",
            "Replace with a balanced alternative thought."
        ],
        "example": "If you think 'I always fail', ask: 'Always? What evidence contradicts that?' then form: 'I've succeeded before and can try again.'"
    },
    "Grounding": {
        "category": "Distress Tolerance",
        "tags": ["present moment", "senses", "5-4-3-2-1"],
        "definition": "Use your senses and surroundings to bring attention to the present and reduce overwhelm.",
        "how_to": [
            "Look for 5 things you can see.",
            "Touch 4 things and name their textures.",
            "Listen for 3 sounds, identify 2 smells, and taste 1 thing if possible."
        ],
        "example": "At your desk, name 5 visible objects, touch your mug, and notice 3 sounds to steady your mind."
    },
    "Deep Breathing": {
        "category": "Distress Tolerance",
        "tags": ["breath", "DB", "relaxation"],
        "definition": "Intentional breathing patterns used to calm the nervous system and reduce acute stress.",
        "how_to": [
            "Sit comfortably and relax your shoulders.",
            "Inhale slowly through your nose for 4 counts.",
            "Hold for 2 counts, then exhale for 6 counts.",
            "Repeat for 4–6 cycles, adjusting counts as needed."
        ],
        "example": "Before a call, practice 5 cycles of 4-2-6 breathing to lower your heart rate."
    },
    "DEAR MAN": {
        "category": "Interpersonal Effectiveness",
        "tags": ["assertiveness", "communication", "dbt"],
        "definition": "A structured script (Describe, Express, Assert, Reinforce, Mindful, Appear confident, Negotiate) for asking for what you want effectively.",
        "how_to": [
            "Describe the situation briefly and objectively.",
            "Express feelings and wishes clearly.",
            "Assert your request and note the benefits (Reinforce).",
            "Stay mindful, appear confident, and be ready to negotiate alternatives."
        ],
        "example": "Ask your manager for flexible hours: describe the issue, express how it helps productivity, assert the request, and offer compromises."
    },
    "PMR": {
        "category": "Distress Tolerance",
        "tags": ["progressive", "tension-release", "relaxation"],
        "definition": "Progressive Muscle Relaxation: systematically tense and relax muscle groups to reduce physical tension.",
        "how_to": [
            "Find a quiet place and sit or lie down.",
            "Tense one muscle group for ~5 seconds, then release slowly.",
            "Move through major groups from head to toe (or vice versa)."
        ],
        "example": "Before bed, tense your fists, release, then forearms, shoulders, and so on to unwind."
    },
    "Mindfulness": {
        "category": "Mindfulness",
        "tags": ["present", "attention", "nonjudgment"],
        "definition": "The practice of paying attention to the present moment with curiosity and without judgement.",
        "how_to": [
            "Choose an anchor (breath, sensation, or sounds).",
            "Gently bring attention back when the mind wanders.",
            "Notice thoughts without following or judging them."
        ],
        "example": "Spend 5 minutes noticing breath sensations; when mind wanders, note 'thinking' and return to breathing."
    },
    "Distraction": {
        "category": "General Coping",
        "tags": ["shift focus", "short-term", "activities"],
        "definition": "Temporarily redirect attention to neutral or positive activities to reduce emotional intensity.",
        "how_to": [
            "Pick a brief activity you enjoy (walk, puzzle, call a friend).",
            "Engage fully for a set period (10–30 minutes).",
            "Return to the triggering thought when you feel calmer."
        ],
        "example": "If stuck in rumination, do a 15-minute walk or solve a crossword to shift perspective."
    },
    "Opposite Action": {
        "category": "Emotion Regulation",
        "tags": ["behavioral", "mood", "act-opposite"],
        "definition": "Deliberately do the opposite of an emotion-driven urge when the emotion is unhelpful or unjustified.",
        "how_to": [
            "Identify the emotion and the urge it causes.",
            "Decide if the emotion fits the facts and goals.",
            "If not, choose an opposite action (e.g., socialize when avoiding)."
        ],
        "example": "If you feel like isolating out of sadness, schedule a short coffee with a friend to counteract the urge."
    },
    "Radical Acceptance": {
        "category": "Distress Tolerance",
        "tags": ["acceptance", "reality", "reduce-resistance"],
        "definition": "Completely acknowledging reality as it is in order to reduce suffering caused by resistance.",
        "how_to": [
            "Notice what is happening and name it objectively.",
            "Acknowledge what you cannot change right now.",
            "Choose how to respond rather than fighting reality."
        ],
        "example": "When a flight is delayed, accept the delay and use the time to read or plan instead of ruminating."
    },
    "Walk": {
        "category": "Distress Tolerance",
        "tags": ["movement", "outdoors", "mood-boost"],
        "definition": "Using walking intentionally to shift mood, ground attention, and get light exercise.",
        "how_to": [
            "Choose a comfortable route and pace.",
            "Focus on sensations (feet, breath, scenery).",
            "Allow thoughts to pass and notice changes in mood."
        ],
        "example": "Take a 10–20 minute outdoor walk when stressed to clear your head."
    },
    "Eat": {
        "category": "Distress Tolerance",
        "tags": ["self-care", "nourish", "mindful-eating"],
        "definition": "Mindful or planned eating to support physical stability and emotional regulation.",
        "how_to": [
            "Choose nourishing foods and regular meal times.",
            "Eat mindfully: notice flavors, textures, and hunger cues.",
            "Avoid skipping meals when stressed."
        ],
        "example": "Pack a balanced snack and eat it consciously to prevent energy crashes during a stressful day."
    },
    "Meditate": {
        "category": "Distress Tolerance",
        "tags": ["practice", "breath", "awareness"],
        "definition": "Formal practice to train attention and awareness, reducing reactivity over time.",
        "how_to": [
            "Set a short time (5–10 minutes) and find a quiet place.",
            "Choose a technique (breath, body scan, loving-kindness).",
            "Return your attention gently when it wanders."
        ],
        "example": "Do a 10-minute breath-focused meditation each morning to improve baseline calm."
    },
    "Hobbies": {
        "category": "Emotion Regulation",
        "tags": ["meaningful-activity", "skill", "pleasure"],
        "definition": "Engaging in enjoyable or meaningful activities to restore positive affect and build identity.",
        "how_to": [
            "List activities you enjoy or want to try.",
            "Schedule regular, small blocks of time for them.",
            "Start small to reduce overwhelm and build momentum."
        ],
        "example": "Spend 30 minutes twice a week on painting or playing guitar to boost mood."
    },
    "Exercise": {
        "category": "Emotion Regulation",
        "tags": ["movement", "endurance", "mood-regulation"],
        "definition": "Planned physical activity that supports mood, sleep, and stress resilience.",
        "how_to": [
            "Pick an activity you can maintain (walk, swim, gym).",
            "Set realistic frequency and duration goals.",
            "Track small wins and adjust when needed."
        ],
        "example": "A 20-minute jog three times per week to help manage anxiety symptoms."
    },
    "Seeking Help": {
        "category": "Interpersonal Effectiveness",
        "tags": ["support", "ask-for-help", "resources"],
        "definition": "Identifying and reaching out to people or professionals when you need support.",
        "how_to": [
            "Identify what kind of help you need (practical, emotional, medical).",
            "Choose who to ask and how (call, text, email).",
            "Be specific about what would help and offer potential times or options."
        ],
        "example": "Email a coworker: 'Could you cover my meeting Tuesday? I need 30 minutes to handle a personal matter.'"
    },
    "Aromatherapy": {
        "category": "Distress Tolerance",
        "tags": ["scent", "self-care", "relaxation"],
        "definition": "Using scents (essential oils, candles) intentionally to cue calm or uplift mood.",
        "how_to": [
            "Choose a scent that soothes or energizes you.",
            "Use a diffuser or inhale briefly from a cloth.",
            "Pair scent with a calming routine (breath, reading)."
        ],
        "example": "Diffuse lavender during an evening wind-down to signal relaxation."
    },
    "Reading": {
        "category": "General Coping",
        "tags": ["distraction", "learning", "escape"],
        "definition": "Using books or articles to calm the mind, learn new skills, or get a brief escape.",
        "how_to": [
            "Pick material that matches your goal (calming fiction, helpful non-fiction).",
            "Set a short reading window (15–30 minutes).",
            "Notice if reading helps mood or causes avoidance; adjust accordingly."
        ],
        "example": "Read a soothing short story for 20 minutes before bed to unwind."
    },
    "Contributing": {
        "category": "Interpersonal Effectiveness",
        "tags": ["helping", "volunteer", "connection"],
        "definition": "Helping others or contributing to a community to build meaning and improve mood.",
        "how_to": [
            "Choose an avenue (volunteer, help a neighbor, mentor).",
            "Start with a small, doable action.",
            "Reflect on how the contribution felt afterward."
        ],
        "example": "Volunteer two hours a month at a local shelter to increase connection and purpose."
    },
    "Comparison": {
        "category": "Emotion Regulation",
        "tags": ["self-evaluation", "perspective", "social-media"],
        "definition": "Noticing comparison urges and using strategies to reduce their negative impact.",
        "how_to": [
            "Notice when you compare and what triggers it.",
            "Remind yourself of differences in context and partial information.",
            "Shift focus to personal values or small progress metrics."
        ],
        "example": "If social media triggers comparison, limit scrolling to 10 minutes and list three personal wins after."
    },
    "Opposite Emotion": {
        "category": "Emotion Regulation",
        "tags": ["behavioral", "mood-shift", "skill"],
        "definition": "Intentionally generating an emotion that opposes and counteracts an unhelpful one (e.g., produce calm when anxious).",
        "how_to": [
            "Identify the unhelpful emotion and a healthy opposite (e.g., calm vs. panic).",
            "Choose activities that reliably produce the opposite (deep breathing, soothing music).",
            "Practice until the opposite emotion is accessible."
        ],
        "example": "Play slow, calming music and do deep breathing to shift from panic toward calm."
    },
    "Sensations": {
        "category": "Distress Tolerance",
        "tags": ["body", "interoception", "awareness"],
        "definition": "Focusing on bodily sensations to anchor attention and differentiate physical from emotional signals.",
        "how_to": [
            "Scan the body and name sensations (warmth, tension, tingling).",
            "Note intensity and location without judgment.",
            "Use grounding touch (hold ice, splash water) if needed."
        ],
        "example": "Notice the pressure of your feet on the floor and lengthen that awareness during a stress spike."
    },
    "Self-Soothing": {
        "category": "Distress Tolerance",
        "tags": ["comfort", "5-senses", "calm"],
        "definition": "Use comforting activities across the five senses to soothe emotional distress.",
        "how_to": [
            "List soothing actions for each sense (e.g., warm tea for taste, soft blanket for touch).",
            "Try one or two that are available and notice their effect.",
            "Make a 'self-soothe kit' for future use."
        ],
        "example": "Wrap in a soft blanket, sip chamomile, and listen to gentle music when upset."
    },
    "Imagery": {
        "category": "Emotion Regulation",
        "tags": ["visualization", "calm", "mental-prep"],
        "definition": "Using guided or self-created mental images to change mood or rehearse coping.",
        "how_to": [
            "Close your eyes and imagine a calm, safe place with details.",
            "Engage all senses in the image (sight, sound, smell).",
            "Use the image when feeling stressed or to rehearse a challenge."
        ],
        "example": "Visualize a peaceful beach—feel the sun and hear waves—before giving a presentation."
    },
    "Vacation": {
        "category": "Distress Tolerance",
        "tags": ["rest", "recharge", "planning"],
        "definition": "Planned time away from routine to rest, reset priorities, and reduce chronic stress.",
        "how_to": [
            "Plan time off, even short breaks, and set realistic expectations.",
            "Decide activities that replenish you (relaxation vs. adventure).",
            "Disconnect from work as much as possible and reflect on rest needs."
        ],
        "example": "Take a long weekend, put email on low-priority, and do low-effort enjoyable activities to recharge."
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

# Emotion keywords dictionary
EMOTION_KEYWORDS = {
    "Joy": ["happy", "glad", "joyful", "excited", "pleased", "delighted", "cheerful", "ecstatic", 
            "thrilled", "wonderful", "amazing", "great", "good", "love", "loved", "enjoy", "enjoying",
            "grateful", "gratitude", "blessed", "lucky", "fortunate", "smile", "laugh", "laughing",
            "proud", "accomplished", "success", "successful", "win", "wonderful", "fantastic"],
    "Sadness": ["sad", "depressed", "down", "unhappy", "melancholy", "upset", "disappointed", 
                "hurt", "pain", "painful", "crying", "tears", "lonely", "loneliness", "empty",
                "hopeless", "helpless", "grief", "grieving", "mourn", "loss", "lost", "miss",
                "regret", "sorry", "guilty", "shame", "worthless"],
    "Anger": ["angry", "mad", "furious", "rage", "raging", "annoyed", "irritated", "frustrated",
              "frustration", "hate", "hatred", "resent", "resentment", "hostile", "outraged",
              "upset", "livid", "enraged", "bitter", "bitterness"],
    "Fear": ["afraid", "fear", "fearful", "scared", "terrified", "anxious", "anxiety", "worried",
             "worry", "nervous", "panic", "panicked", "dread", "dreadful", "horror", "horrified",
             "threat", "threatened", "unsafe", "unsure", "uncertain", "uncomfortable"],
    "Surprise": ["surprised", "surprise", "shocked", "shock", "amazed", "amazing", "astonished",
                 "unexpected", "unbelievable", "wow", "incredible", "stunned", "stunning"],
    "Neutral": ["okay", "fine", "normal", "alright", "ok", "neutral", "average", "regular"]
}

def analyze_sentiment(text):
    """Analyze sentiment of text and return polarity (-1 to 1)"""
    if not text or not text.strip():
        return 0.0
    
    if TEXTBLOB_AVAILABLE:
        try:
            blob = TextBlob(text)
            return round(blob.sentiment.polarity, 3)
        except:
            pass
    
    # Fallback: simple keyword-based sentiment if TextBlob not available
    text_lower = text.lower()
    positive_words = ["good", "great", "happy", "love", "wonderful", "excellent", "amazing", 
                     "pleased", "joyful", "grateful", "blessed", "lucky", "proud"]
    negative_words = ["bad", "sad", "angry", "hate", "terrible", "awful", "horrible", 
                     "disappointed", "hurt", "pain", "lonely", "hopeless", "fear", "worried"]
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count + neg_count == 0:
        return 0.0
    
    return round((pos_count - neg_count) / (pos_count + neg_count), 3)

def detect_emotion(text):
    """Detect primary emotion in text based on keywords"""
    if not text or not text.strip():
        return "Neutral"
    
    text_lower = text.lower()
    emotion_scores = {}
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            emotion_scores[emotion] = score
    
    if not emotion_scores:
        return "Neutral"
    
    # Return emotion with highest score
    return max(emotion_scores.items(), key=lambda x: x[1])[0]

def extract_entry_text(content, excluded_fields):
    """Extract user-entered text from entry content"""
    try:
        content_dict = json.loads(content)
        text_parts = []
        for key, value in content_dict.items():
            if key not in excluded_fields and value:
                text_parts.append(str(value))
        return " ".join(text_parts)
    except:
        return content if content else ""

def filter_rows_by_period(rows, time_period):
    """Filter rows by time period"""
    if time_period == 'all_time':
        return rows
    
    now = datetime.now()
    filtered_rows = []
    
    for date_str, journal_type, content in rows:
        try:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            
            if time_period == 'last_week':
                if (now - entry_date) <= timedelta(days=7):
                    filtered_rows.append((date_str, journal_type, content))
            elif time_period == 'last_month':
                if (now - entry_date) <= timedelta(days=30):
                    filtered_rows.append((date_str, journal_type, content))
            elif time_period == 'last_3months':
                if (now - entry_date) <= timedelta(days=90):
                    filtered_rows.append((date_str, journal_type, content))
        except:
            # If date parsing fails, skip it (don't include in filtered results)
            pass
    
    return filtered_rows

@app.route("/")
def home():
    # Get sort and search parameters
    sort_by = request.args.get('sort', 'date_desc')  # date_desc, date_asc, type
    search_date = request.args.get('date', '')  # YYYY-MM-DD format
    
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    
    # Build query based on sort and search
    if search_date:
        # Search by specific date
        c.execute("SELECT id, date, title, journal_type, content FROM entries WHERE date LIKE ? ORDER BY date DESC", 
                  (f"{search_date}%",))
    else:
        # Normal query with sorting
        if sort_by == 'date_asc':
            c.execute("SELECT id, date, title, journal_type, content FROM entries ORDER BY date ASC")
        elif sort_by == 'type':
            c.execute("SELECT id, date, title, journal_type, content FROM entries ORDER BY journal_type, date DESC")
        else:  # date_desc (default)
            c.execute("SELECT id, date, title, journal_type, content FROM entries ORDER BY date DESC")
    
    entries = c.fetchall()
    conn.close()

    decoded_entries = []
    for entry in entries:
        entry_id, date, title, journal_type, content = entry

        # Default title to date if missing or blank
        if not title or title.strip() == "":
            title = date

        decoded_entries.append((entry_id, date, title, journal_type, ""))

    return render_template("home.html", entries=decoded_entries, sort_by=sort_by, search_date=search_date)

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
    # Get separate time period filters from query parameters
    sentiment_period = request.args.get('sentiment_period', 'all_time')
    emotion_period = request.args.get('emotion_period', 'all_time')
    
    # Validate periods
    valid_periods = ['all_time', 'last_week', 'last_month', 'last_3months']
    if sentiment_period not in valid_periods:
        sentiment_period = 'all_time'
    if emotion_period not in valid_periods:
        emotion_period = 'all_time'
    
    conn = sqlite3.connect("journal.db")
    c = conn.cursor()
    c.execute("SELECT date, journal_type, content FROM entries ORDER BY date")
    all_rows = c.fetchall()
    conn.close()

    # Keep all rows for other analytics (entry types, common words, etc.)
    rows = all_rows
    total_entries = len(rows)

    # Fields to exclude (choice/select fields) - only analyze user-entered text
    excluded_fields = {'journal_type', 'situation_category', 'used_skills', 'title'}
    
    # Common stop words to filter out (words with no meaningful weight)
    stop_words = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 
        'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 
        'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 
        'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 
        'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 
        'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 
        'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had', 'does', 'did', 'were', 'being', 'been', 
        'may', 'might', 'must', 'shall', 'should', 'would', 'could', 'ought', 'these', 'those', 'own', 'same', 
        'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 
        'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 
        'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn'
    }

    # --- 1. Entry Type Counts ---
    type_counts = {}
    for _, journal_type, _ in rows:
        type_counts[journal_type] = type_counts.get(journal_type, 0) + 1
    
    # Find most frequent type
    most_frequent_type = "N/A"
    if type_counts:
        most_frequent_type = max(type_counts.items(), key=lambda x: x[1])[0]

    # --- 2. Combine all text for common words ---
    
    all_text = ""
    for _, _, content in rows:
        try:
            content_dict = json.loads(content)
            # Only include text from user-entered fields (exclude choice/select fields)
            for key, value in content_dict.items():
                if key not in excluded_fields and value:
                    all_text += str(value) + " "
        except:
            # For old entries that might not be JSON, treat as text entry
            if content:
                all_text += content + " "
    
    # Extract words (minimum 3 characters) and filter out stop words
    words = re.findall(r'\b[a-z]{3,}\b', all_text.lower())
    filtered_words = [word for word in words if word not in stop_words]
    common_words = Counter(filtered_words).most_common(20)

    # --- 3. Weekly Writing Frequency (entries per weekday) ---
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weekly_counts = {d: 0 for d in weekdays}
    for date_str, _, _ in rows:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            weekly_counts[dt.strftime("%a")] += 1
        except:
            pass

    # --- 4. Sentiment Trend (real sentiment analysis) - filtered by sentiment_period ---
    sentiment_rows = filter_rows_by_period(all_rows, sentiment_period)
    sentiment_by_date = {}
    
    for date_str, _, content in sentiment_rows:
        try:
            entry_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            date_key = entry_date.strftime("%Y-%m-%d")
            
            # Extract text from entry
            text = extract_entry_text(content, excluded_fields)
            
            if text:
                sentiment_score = analyze_sentiment(text)
                
                if date_key not in sentiment_by_date:
                    sentiment_by_date[date_key] = []
                sentiment_by_date[date_key].append(sentiment_score)
        except:
            continue
    
    # Calculate average sentiment per day
    sentiment_trend = {}
    for date_key, scores in sentiment_by_date.items():
        if scores:
            sentiment_trend[date_key] = round(sum(scores) / len(scores), 3)
    
    # Sort by date for proper chart display
    sentiment_trend = dict(sorted(sentiment_trend.items()))

    # --- 5. Emotion Distribution (real emotion detection) - filtered by emotion_period ---
    emotion_rows = filter_rows_by_period(all_rows, emotion_period)
    emotion_counts = {
        "Joy": 0,
        "Sadness": 0,
        "Anger": 0,
        "Fear": 0,
        "Surprise": 0,
        "Neutral": 0
    }
    
    for date_str, _, content in emotion_rows:
        text = extract_entry_text(content, excluded_fields)
        if text:
            emotion = detect_emotion(text)
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

    # --- 6. Words by Day of Week (average word count) ---
    words_by_day = {d: 0 for d in weekdays}
    counts_by_day = {d: 0 for d in weekdays}

    for date_str, _, content in rows:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            weekday = dt.strftime("%a")
            try:
                content_dict = json.loads(content)
                # Only include text from user-entered fields (exclude choice/select fields)
                text_parts = []
                for key, value in content_dict.items():
                    if key not in excluded_fields and value:
                        text_parts.append(str(value))
                text = " ".join(text_parts)
            except:
                text = content if content else ""
            
            # Extract words and filter out stop words
            words = re.findall(r'\b[a-z]{3,}\b', text.lower())
            filtered_words = [word for word in words if word not in stop_words]
            word_count = len(filtered_words)
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
        most_frequent_type=most_frequent_type,
        common_words=common_words,
        weekly_counts=weekly_counts,
        sentiment_trend=sentiment_trend,
        emotion_counts=emotion_counts,
        words_by_day=words_by_day,
        sentiment_period=sentiment_period,
        emotion_period=emotion_period
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
    # Build category and tag lists for client-side filters
    categories = sorted({s["category"] for s in skills_db.values()})
    tags = sorted({tag for s in skills_db.values() for tag in s["tags"]})
    return render_template("skills.html", skills=skills_db, categories=categories, tags=tags)


@app.route("/skill/<name>")
def skill_detail(name):
    skill = skills_db.get(name)
    if not skill:
        # graceful fallback - skill not found
        return render_template("skill_details.html", skill={
            "name": name,
            "category": "Unknown",
            "tags": [],
            "definition": "Skill not found.",
            "how_to": [],
            "example": ""
        }), 404
    # provide name inside object for template convenience
    skill_with_name = dict(skill)
    skill_with_name["name"] = name
    return render_template("skill_details.html", skill=skill_with_name)




if __name__ == "__main__":
    app.run(debug=True)
