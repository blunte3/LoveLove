"""
Script to generate 3 months of realistic journal entries for a college student with bipolar disorder.
This creates entries showing cycles of highs and lows over time.
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random

# Database setup
conn = sqlite3.connect("journal.db")
c = conn.cursor()

# Sample entry templates organized by mood state and journal type

# HIGH/MANIC PERIOD ENTRIES (High energy, euphoric, creative, social)
HIGH_MORNING_ENTRIES = [
    {
        "sleep_quality": "8",
        "sleep_notes": "Woke up at 5am feeling incredible! Slept maybe 4 hours but I'm buzzing with energy. My mind is racing with ideas for my art project and I can't wait to get started.",
        "gratitudes": "Grateful for this amazing energy, for my friends who get my vibe, for the beautiful sunrise I saw, and for feeling like I can accomplish anything today.",
        "affirmations": "I am capable of amazing things. My creativity knows no bounds. I am going to crush today and every day.",
        "goals": "Finish that essay draft, work out for an hour, call mom, start that painting I've been thinking about, maybe check out that new coffee shop downtown",
        "actions": "Hit the gym first thing, then library for focused writing, then creative time in the studio. Maybe see if Sarah wants to grab dinner later.",
        "morning_freetext": "I feel like I'm on top of the world today. Everything seems possible and I'm vibrating with positive energy. Going to channel this into productivity and creativity."
    },
    {
        "sleep_quality": "6",
        "sleep_notes": "Only slept about 5 hours but I feel amazing. Had so many ideas I had to write them down at 3am. The world feels full of possibilities right now.",
        "gratitudes": "So grateful for this burst of inspiration, for my supportive roommate who doesn't mind my late-night energy, for coffee, and for feeling unstoppable.",
        "affirmations": "I am brilliant and creative. I attract amazing opportunities. My energy is a gift.",
        "goals": "Polish that presentation, attend all classes with full engagement, reach out to three new people, work on my side project, go for a long run",
        "actions": "Start with meditation to channel this energy, then tackle all my tasks with focus. Take breaks for movement and social connection.",
        "morning_freetext": "My brain feels like it's on fire in the best way. Ideas are flowing faster than I can process them. Time to harness this and make magic happen."
    },
    {
        "sleep_quality": "7",
        "sleep_notes": "Woke up at 6am feeling like I've had a full night's rest even though I only got about 6 hours. Body feels light and energized.",
        "gratitudes": "Thankful for this clarity of mind, for the opportunities ahead, for my health, and for feeling so connected to everything around me.",
        "affirmations": "I am powerful and capable. I radiate positive energy. Today will be extraordinary.",
        "goals": "Complete all readings ahead of schedule, practice piano for two hours, organize my room, reach out to professors about research opportunities, connect with friends",
        "actions": "Early morning workout, then library for deep work. Schedule social activities for balance. Stay hydrated and grounded.",
        "morning_freetext": "Everything feels heightened and beautiful today. Colors seem brighter, sounds clearer. Going to ride this wave and accomplish so much."
    }
]

HIGH_NIGHT_ENTRIES = [
    {
        "night_gratitudes": "Grateful for an incredibly productive day, for the amazing connections I made, for finishing three major tasks, and for feeling so alive and present.",
        "positives": "Finished my essay ahead of schedule, had great conversations with classmates, felt creative and inspired all day, made progress on my art project, connected with old friends",
        "goal_progress": "Crushed all my goals and then some! Completed everything plus started that new project I've been excited about. Feeling accomplished and motivated.",
        "night_freetext": "What an incredible day! I feel like I'm operating at 200% capacity and loving every minute. The only downside is I'm not tired at all even though it's midnight. My mind is still racing with ideas."
    },
    {
        "night_gratitudes": "So grateful for my amazing friends who matched my energy today, for completing all my assignments, for the beautiful weather, and for feeling so connected to life.",
        "positives": "Had an amazing workout, aced my presentation, made new connections at the student center, worked on my passion project, felt creative and inspired throughout the day",
        "goal_progress": "Accomplished everything on my list plus helped a friend with their project. My productivity today was off the charts. Tomorrow will be even better!",
        "night_freetext": "Today was absolutely phenomenal. I feel like I'm in a flow state where everything comes easily. The only challenge is slowing down my racing thoughts to sleep, but I'm so energized by everything I did today."
    }
]

HIGH_SITUATIONAL_ENTRIES = [
    {
        "situation": "Had an amazing idea for a group project and ended up talking for two hours straight, probably overwhelming my teammates a bit. I was so excited about the possibilities that I couldn't stop sharing.",
        "situation_category": "Interpersonal",
        "feelings": "Excited, energized, creative, confident, maybe a little too intense",
        "used_skills": "No",
        "skills_used": "",
        "after_effect": "My teammates seemed interested but maybe a bit overwhelmed. I should check in with them and make sure they're okay with my energy level. Maybe I can channel this enthusiasm more constructively."
    },
    {
        "situation": "Spent $200 on art supplies and materials for a project I got excited about at 11pm. I had this incredible vision and couldn't wait to start creating.",
        "situation_category": "Intrapersonal",
        "feelings": "Excited, creative, impulsive, confident, inspired",
        "used_skills": "No",
        "skills_used": "",
        "after_effect": "I'm excited about the project but maybe should have waited before spending that much. My creativity feels amazing right now, but I need to balance it with being responsible about money."
    }
]

HIGH_FREEWRITE_ENTRIES = [
    "I feel like I'm vibrating with energy and creativity. Ideas are flowing through me like a river and I can't write fast enough. Everything seems possible right now. I want to paint, write, connect with people, learn new things, experience everything. Life feels incredibly vibrant and full of potential. I know this energy won't last forever, so I'm trying to channel it productively while it's here.",
    "Today was absolutely incredible. I woke up with this surge of motivation and it hasn't stopped. Finished three assignments, started a new creative project, had meaningful conversations with friends, and still have energy for more. I feel like I'm operating at peak performance. The only challenge is that my thoughts are racing so fast it's hard to keep up with them all.",
    "Everything feels heightened right now. Music sounds more beautiful, conversations feel more meaningful, and I'm seeing connections everywhere. I feel incredibly creative and inspired. Part of me knows this is probably a high period, but it feels so good that I don't want it to end."
]

# DEPRESSED/LOW PERIOD ENTRIES (Low energy, sadness, difficulty, isolation)
LOW_MORNING_ENTRIES = [
    {
        "sleep_quality": "3",
        "sleep_notes": "Slept for 12 hours but still feel exhausted. Had trouble falling asleep, then couldn't get out of bed. Everything feels heavy and difficult.",
        "gratitudes": "I'm grateful for my warm bed, for the sunlight coming through my window, for the fact that I woke up at all today.",
        "affirmations": "I am doing my best. Small steps count. I will get through this.",
        "goals": "Get out of bed, brush my teeth, maybe eat something, attend at least one class",
        "actions": "Focus on basic self-care first. Don't push too hard. Just take it one small step at a time.",
        "morning_freetext": "Waking up feels impossible. Everything requires so much effort. I know I should get up but my body feels like it weighs a thousand pounds. I'll try to do at least one thing today."
    },
    {
        "sleep_quality": "2",
        "sleep_notes": "Tossed and turned all night. Mind racing with negative thoughts. Got maybe 5 hours of broken sleep. Feel worse than before I went to bed.",
        "gratitudes": "Grateful that my roommate is understanding, for hot showers, for the fact that I have a place to sleep safely.",
        "affirmations": "This feeling is temporary. I am stronger than I feel right now. One moment at a time.",
        "goals": "Take a shower, drink some water, respond to at least one message, maybe go outside for five minutes",
        "actions": "Start with the smallest possible step. Don't judge myself for what I can't do. Just focus on what's possible right now.",
        "morning_freetext": "Another morning where everything feels overwhelming. The thought of getting through the day exhausts me before I've even started. I know this will pass, but right now it feels permanent."
    },
    {
        "sleep_quality": "4",
        "sleep_notes": "Slept okay but woke up feeling empty and drained. No motivation, no energy, just this heavy sadness that sits in my chest.",
        "gratitudes": "Grateful for my therapist, for medication that helps, for my cat who keeps me company, for small moments of peace.",
        "affirmations": "I am doing enough. My feelings are valid. I will be gentle with myself today.",
        "goals": "Eat one meal, check my email, maybe watch something that makes me feel slightly better",
        "actions": "No pressure, no expectations. Just survive today. That's enough.",
        "morning_freetext": "The gray fog has settled in again. Everything feels muted and far away. I know people care about me, but it's hard to feel it right now. Just going to focus on getting through today."
    }
]

LOW_NIGHT_ENTRIES = [
    {
        "night_gratitudes": "Grateful that I made it through the day, for the one person who checked in on me, for being able to rest now.",
        "positives": "I did get out of bed today. I ate something. I didn't completely isolate. Those are small wins.",
        "goal_progress": "I didn't accomplish much, but I didn't completely shut down either. Taking that as progress.",
        "night_freetext": "Another day done. I'm exhausted even though I didn't do much. Hoping tomorrow feels a little lighter. Right now I just want to sleep and escape for a while."
    },
    {
        "night_gratitudes": "Thankful for the quiet, for my comfortable space, for being able to end the day and rest.",
        "positives": "I managed to take care of some basic needs today. That counts for something, even if it doesn't feel like much.",
        "goal_progress": "Didn't meet most of my goals, but I'm trying not to beat myself up about it. Just being present is hard right now.",
        "night_freetext": "Today was another struggle. Everything feels heavy and hard. I know this is part of the cycle, but it's exhausting. Looking forward to sleep as an escape from my racing thoughts."
    }
]

LOW_SITUATIONAL_ENTRIES = [
    {
        "situation": "Had to cancel plans with friends again because I couldn't get out of bed. I feel guilty for letting them down but also can't find the energy to care enough to force myself.",
        "situation_category": "Interpersonal",
        "feelings": "Guilty, ashamed, isolated, tired, disappointed in myself",
        "used_skills": "Yes",
        "skills_used": "Tried to use self-compassion. Reminded myself that my illness is valid and canceling is okay when I'm struggling.",
        "after_effect": "Still feel bad about it, but I did send them a message explaining I'm having a hard time. They were understanding. Taking care of myself has to come first right now."
    },
    {
        "situation": "Skipped three classes in a row because I couldn't motivate myself to go. Now I'm behind on work and feeling even worse about myself.",
        "situation_category": "Intrapersonal",
        "feelings": "Ashamed, overwhelmed, hopeless, anxious about catching up, frustrated with myself",
        "used_skills": "Yes",
        "skills_used": "Used acceptance - this is where I am right now. Reached out to professors to explain. Made a small plan to catch up slowly.",
        "after_effect": "Still anxious, but feeling slightly more in control. One class at a time, one assignment at a time. I'll get through this."
    },
    {
        "situation": "Broke down crying in the library because I was so overwhelmed by everything I need to do. Felt embarrassed and isolated.",
        "situation_category": "Intrapersonal",
        "feelings": "Overwhelmed, sad, embarrassed, exhausted, hopeless",
        "used_skills": "No",
        "skills_used": "",
        "after_effect": "A kind stranger asked if I was okay, which helped a bit. I'm trying to remember that it's okay to struggle. Going to reach out to my therapist about this."
    }
]

LOW_FREEWRITE_ENTRIES = [
    "Everything feels too hard today. The simplest tasks feel impossible. I know this is depression talking, but that knowledge doesn't make it easier. I feel like I'm watching my life pass by from behind a glass wall, unable to fully participate. I just want to feel normal again.",
    "Another day where I've done the bare minimum and still feel exhausted. I know I should be doing more, but I can't find the motivation or energy. The guilt about not being productive makes everything worse. I'm trying to be kind to myself, but it's hard when everything feels so dark.",
    "The emptiness is back. It's not sadness exactly, just... nothing. No joy, no interest, no motivation. Just existing. I know people care, but I can't feel their love right now. Everything feels distant and muted. I just want to sleep until this passes."
]

# MIXED/STABLE PERIOD ENTRIES (Normal fluctuations, balanced)
MIXED_MORNING_ENTRIES = [
    {
        "sleep_quality": "7",
        "sleep_notes": "Got about 7 hours of sleep. Feel reasonably rested, maybe a bit groggy but that's normal for Monday morning.",
        "gratitudes": "Grateful for a decent night's sleep, for my morning coffee, for having a routine, and for feeling relatively stable today.",
        "affirmations": "I am capable and balanced. I can handle what comes my way. Today will be manageable.",
        "goals": "Attend all classes, finish that reading, grab lunch with a friend, work on assignments for a couple hours",
        "actions": "Follow my routine - breakfast, classes, study time, some social connection. Keep things balanced.",
        "morning_freetext": "Feeling pretty stable today. Not super high, not super low - just... normal. It's nice to feel steady. Going to make the most of this balanced energy."
    },
    {
        "sleep_quality": "6",
        "sleep_notes": "Slept okay, about 6.5 hours. Woke up a bit tired but that's manageable. Feeling neutral about the day ahead.",
        "gratitudes": "Thankful for my medication working, for having structure in my day, for friends who understand, and for small moments of peace.",
        "affirmations": "I am managing well. Balance is possible. I can handle challenges as they come.",
        "goals": "Get through classes, do some homework, maybe go for a walk, check in with family",
        "actions": "Take it steady. Don't push too hard, don't hold back too much. Just maintain balance.",
        "morning_freetext": "Today feels... manageable. Not exciting, not depressing, just regular. I'm learning to appreciate these stable days. They're a gift after the extremes."
    }
]

MIXED_NIGHT_ENTRIES = [
    {
        "night_gratitudes": "Grateful for a productive but balanced day, for meaningful connections, for getting work done without burning out, and for feeling steady.",
        "positives": "Attended all my classes, had good conversations with friends, made progress on assignments, took a nice walk, felt stable throughout the day",
        "goal_progress": "Accomplished most of what I set out to do without overdoing it. Feeling good about maintaining balance.",
        "night_freetext": "Today was a good day - not spectacular, but solid. I got things done, connected with people, took care of myself. This is what stability feels like and I'm grateful for it."
    }
]

MIXED_SITUATIONAL_ENTRIES = [
    {
        "situation": "Had a disagreement with my roommate about cleaning. We both got a bit frustrated but were able to talk it through calmly.",
        "situation_category": "Interpersonal",
        "feelings": "Slightly frustrated but reasonable, willing to compromise, stable",
        "used_skills": "Yes",
        "skills_used": "Used communication skills and de-escalation. Stayed calm and focused on finding a solution rather than being reactive.",
        "after_effect": "We came to a compromise that works for both of us. Feeling good about handling conflict in a healthy way."
    }
]

MIXED_FREEWRITE_ENTRIES = [
    "Today was a pretty normal day. Got things done, felt okay, nothing extreme either way. I'm learning to appreciate these balanced moments. After experiencing the highs and lows, stability feels like a gift. I'm trying to build routines and habits that help maintain this equilibrium.",
    "Feeling relatively stable right now, which is nice. I'm staying on top of my medication, going to therapy, maintaining routines. Life isn't perfect but it's manageable. I'm grateful for the tools and support that help me find this balance."
]

def generate_date_range(start_date, days):
    """Generate a list of dates starting from start_date for the specified number of days"""
    dates = []
    current = start_date
    for _ in range(days):
        dates.append(current)
        current += timedelta(days=1)
    return dates

def simulate_bipolar_cycle(days):
    """Simulate bipolar mood cycles over the specified days"""
    # Roughly simulate cycles: hypomanic periods (7-14 days), depressive periods (10-21 days), stable periods (varies)
    states = []
    current_state = "stable"
    state_duration = 0
    
    for day in range(days):
        # Transition logic
        if current_state == "stable":
            if state_duration >= 5:
                # Transition to either high or low
                current_state = random.choice(["high", "low"])
                state_duration = 0
        elif current_state == "high":
            if state_duration >= random.randint(5, 12):
                # Crash to low or stabilize
                current_state = random.choice(["low", "stable"])
                state_duration = 0
        elif current_state == "low":
            if state_duration >= random.randint(10, 18):
                # Improve to stable or sometimes go high
                if random.random() < 0.3:  # 30% chance of going high after low
                    current_state = "high"
                else:
                    current_state = "stable"
                state_duration = 0
        
        states.append(current_state)
        state_duration += 1
    
    return states

def create_entry(date, journal_type, title, entry_data, hour=10, minute=0):
    """Create a journal entry in the database"""
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")
    if not date_str.endswith(" 00:00:00"):
        date_str = f"{date.strftime('%Y-%m-%d')} {hour:02d}:{minute:02d}:00"
    
    c.execute("INSERT INTO entries (date, title, journal_type, content) VALUES (?, ?, ?, ?)",
              (date_str, title, journal_type, json.dumps(entry_data)))
    conn.commit()

def generate_entries():
    """Generate 3 months (90 days) of journal entries"""
    start_date = datetime.now() - timedelta(days=90)
    dates = generate_date_range(start_date, 90)
    mood_states = simulate_bipolar_cycle(90)
    
    entry_count = 0
    
    for i, (date, state) in enumerate(zip(dates, mood_states)):
        # Decide how many entries per day based on state
        if state == "high":
            num_entries = random.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
        elif state == "low":
            num_entries = random.choices([0, 1], weights=[0.4, 0.6])[0]
        else:  # stable
            num_entries = random.choices([0, 1, 2], weights=[0.3, 0.5, 0.2])[0]
        
        entry_types_today = []
        
        for _ in range(num_entries):
            # Choose journal type based on state and what hasn't been used today
            if state == "high":
                if "Daily Journal - Morning" not in entry_types_today and random.random() < 0.4:
                    journal_type = "Daily Journal - Morning"
                    entry_data = random.choice(HIGH_MORNING_ENTRIES)
                    hour = random.randint(7, 9)
                    title = f"High Energy Morning - {date.strftime('%b %d')}"
                elif "Daily Journal - Night" not in entry_types_today and random.random() < 0.3:
                    journal_type = "Daily Journal - Night"
                    entry_data = random.choice(HIGH_NIGHT_ENTRIES)
                    hour = random.randint(21, 23)
                    title = f"Amazing Day - {date.strftime('%b %d')}"
                elif "Situational Journal" not in entry_types_today and random.random() < 0.2:
                    journal_type = "Situational Journal"
                    entry_data = random.choice(HIGH_SITUATIONAL_ENTRIES)
                    hour = random.randint(14, 18)
                    title = f"High Energy Moment - {date.strftime('%b %d')}"
                else:
                    journal_type = "Free Write"
                    entry_data = {"content": random.choice(HIGH_FREEWRITE_ENTRIES)}
                    hour = random.randint(10, 22)
                    title = f"Inspired Thoughts - {date.strftime('%b %d')}"
            
            elif state == "low":
                if "Daily Journal - Morning" not in entry_types_today and random.random() < 0.5:
                    journal_type = "Daily Journal - Morning"
                    entry_data = random.choice(LOW_MORNING_ENTRIES)
                    hour = random.randint(10, 12)
                    title = f"Struggling Morning - {date.strftime('%b %d')}"
                elif "Daily Journal - Night" not in entry_types_today and random.random() < 0.3:
                    journal_type = "Daily Journal - Night"
                    entry_data = random.choice(LOW_NIGHT_ENTRIES)
                    hour = random.randint(20, 23)
                    title = f"End of Hard Day - {date.strftime('%b %d')}"
                elif "Situational Journal" not in entry_types_today and random.random() < 0.2:
                    journal_type = "Situational Journal"
                    entry_data = random.choice(LOW_SITUATIONAL_ENTRIES)
                    hour = random.randint(14, 18)
                    title = f"Difficult Situation - {date.strftime('%b %d')}"
                else:
                    journal_type = "Free Write"
                    entry_data = {"content": random.choice(LOW_FREEWRITE_ENTRIES)}
                    hour = random.randint(10, 22)
                    title = f"Hard Day - {date.strftime('%b %d')}"
            
            else:  # stable
                if "Daily Journal - Morning" not in entry_types_today and random.random() < 0.3:
                    journal_type = "Daily Journal - Morning"
                    entry_data = random.choice(MIXED_MORNING_ENTRIES)
                    hour = random.randint(7, 9)
                    title = f"Balanced Morning - {date.strftime('%b %d')}"
                elif "Daily Journal - Night" not in entry_types_today and random.random() < 0.2:
                    journal_type = "Daily Journal - Night"
                    entry_data = random.choice(MIXED_NIGHT_ENTRIES)
                    hour = random.randint(20, 22)
                    title = f"Stable Day - {date.strftime('%b %d')}"
                elif "Situational Journal" not in entry_types_today and random.random() < 0.1:
                    journal_type = "Situational Journal"
                    entry_data = random.choice(MIXED_SITUATIONAL_ENTRIES)
                    hour = random.randint(14, 17)
                    title = f"Normal Situation - {date.strftime('%b %d')}"
                else:
                    journal_type = "Free Write"
                    entry_data = {"content": random.choice(MIXED_FREEWRITE_ENTRIES)}
                    hour = random.randint(10, 20)
                    title = f"Reflection - {date.strftime('%b %d')}"
            
            create_entry(date, journal_type, title, entry_data, hour, random.randint(0, 59))
            entry_types_today.append(journal_type)
            entry_count += 1
            
            if entry_count % 10 == 0:
                print(f"Generated {entry_count} entries...")
    
    print(f"\nTotal entries generated: {entry_count}")
    print(f"Entries span from {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    print("Generating 3 months of journal entries...")
    print("This may take a moment...\n")
    
    # Check if entries already exist
    c.execute("SELECT COUNT(*) FROM entries")
    count = c.fetchone()[0]
    
    if count > 0:
        response = input(f"Found {count} existing entries. Add new entries? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            conn.close()
            exit()
    
    generate_entries()
    
    print("\nDone! Journal entries have been generated.")
    conn.close()

