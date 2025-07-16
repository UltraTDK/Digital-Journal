import sqlite3
from datetime import datetime

def create_user_table():
    connection = sqlite3.connect("database.db")
    conn = connection.cursor()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    connection.commit()
    connection.close()

def register_user(username, password):
    connection = sqlite3.connect("database.db")
    conn = connection.cursor()

    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        connection.close()

def login_user(username, password):
    connection = sqlite3.connect("database.db")
    conn = connection.cursor()
    conn.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = conn.fetchone()
    connection.close()
    return user[0] if user else None

# Salvare emotie in baza de date
def save_emotion_to_db(user_id, emotion, source):
    connection = sqlite3.connect("database.db")
    conn = connection.cursor()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS emotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            timestamp TEXT,
            emotion TEXT,
            source TEXT
        )
    ''')

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn.execute("INSERT INTO emotions (user_id, timestamp, emotion, source) VALUES (?, ?, ?, ?)",
              (user_id, timestamp, emotion, source))
    
    connection.commit()
    connection.close()