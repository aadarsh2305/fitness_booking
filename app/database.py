import sqlite3
import threading

conn = sqlite3.connect(":memory:", check_same_thread=False)
conn.row_factory = sqlite3.Row
lock = threading.Lock()

def init_db():
    with lock:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                datetime TEXT NOT NULL,
                instructor TEXT NOT NULL,
                total_slots INTEGER NOT NULL,
                available_slots INTEGER NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                client_name TEXT NOT NULL,
                client_email TEXT NOT NULL,
                booking_time TEXT NOT NULL,
                FOREIGN KEY (class_id) REFERENCES classes(id)
            )
        """)
        conn.commit()

def seed_db():
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
    now = datetime.now(IST).replace(microsecond=0, second=0, minute=0)
    classes = [
        ("Yoga", now + timedelta(days=1, hours=7), "Aadarsh Gupta", 12, 12),
        ("Zumba", now + timedelta(days=2, hours=8), "Kavita Joshi", 10, 10),
        ("HIIT", now + timedelta(days=3, hours=6, minutes=30), "Rohan Bhatt", 15, 15),
    ]
    with lock:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO classes (name, datetime, instructor, total_slots, available_slots) VALUES (?, ?, ?, ?, ?)",
            [(name, dt.isoformat(), instructor, total, avail) for name, dt, instructor, total, avail in classes]
        )
        conn.commit()
