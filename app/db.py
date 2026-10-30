import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "studyai.db"


def connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init():
    conn = connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lectures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            course TEXT NOT NULL,
            notes TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def add_lecture(title, course, notes):
    conn = connect()
    cursor = conn.execute(
        "INSERT INTO lectures (title, course, notes) VALUES (?, ?, ?)", (title, course, notes)
    )
    conn.commit()
    lecture_id = cursor.lastrowid
    conn.close()
    return lecture_id


def get_lecture(lecture_id):
    conn = connect()
    row = conn.execute("SELECT * FROM lectures WHERE id = ?", (lecture_id,)).fetchone()
    conn.close()
    return dict(row) if row else None
