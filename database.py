import sqlite3

conn = sqlite3.connect("burnout.db")
cursor = conn.cursor()

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

# Daily logs with extended inputs
cursor.execute("""
CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    study_hours INTEGER,
    sleep_hours INTEGER,
    deadlines INTEGER,
    stress_level INTEGER,
    breaks INTEGER,
    screen_time REAL,
    physical_activity TEXT,
    log_date DATE,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

# Burnout score table
cursor.execute("""
CREATE TABLE IF NOT EXISTS burnout_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    score REAL,
    risk_level TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

conn.commit()
conn.close()

print("Database initialized with Tier-2 inputs")

input("Press Enter to close the terminal...")
