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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lecture_id INTEGER NOT NULL REFERENCES lectures(id),
            question INTEGER NOT NULL,
            concept TEXT NOT NULL,
            picked INTEGER NOT NULL,
            correct INTEGER NOT NULL,
            answered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS flashcard_reviews (
            lecture_id INTEGER NOT NULL REFERENCES lectures(id),
            card INTEGER NOT NULL,
            concept TEXT NOT NULL,
            repetitions INTEGER NOT NULL,
            interval_days INTEGER NOT NULL,
            ease REAL NOT NULL,
            due TEXT NOT NULL,
            reviewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (lecture_id, card)
        )
        """
    )
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(lectures)")}
    if "source" not in columns:
        conn.execute("ALTER TABLE lectures ADD COLUMN source TEXT NOT NULL DEFAULT 'pasted notes'")
    conn.commit()
    conn.close()


def add_lecture(title, course, notes, source="pasted notes"):
    conn = connect()
    cursor = conn.execute(
        "INSERT INTO lectures (title, course, notes, source) VALUES (?, ?, ?, ?)", (title, course, notes, source)
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


def list_lectures():
    conn = connect()
    rows = conn.execute("SELECT * FROM lectures ORDER BY created_at DESC, id DESC").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_attempt(lecture_id, question, concept, picked, correct):
    conn = connect()
    conn.execute(
        "INSERT INTO quiz_attempts (lecture_id, question, concept, picked, correct) VALUES (?, ?, ?, ?, ?)",
        (lecture_id, question, concept, picked, int(correct)),
    )
    conn.commit()
    conn.close()


def quiz_progress(lecture_id):
    conn = connect()
    row = conn.execute(
        "SELECT COUNT(*) AS answered, COALESCE(SUM(correct), 0) AS correct FROM quiz_attempts WHERE lecture_id = ?",
        (lecture_id,),
    ).fetchone()
    conn.close()
    return dict(row)


def card_states(lecture_id):
    conn = connect()
    rows = conn.execute("SELECT * FROM flashcard_reviews WHERE lecture_id = ?", (lecture_id,)).fetchall()
    conn.close()
    return {
        row["card"]: {
            "repetitions": row["repetitions"],
            "interval": row["interval_days"],
            "ease": row["ease"],
            "due": row["due"],
        }
        for row in rows
    }


def save_review(lecture_id, card, concept, state):
    conn = connect()
    conn.execute(
        """
        INSERT INTO flashcard_reviews (lecture_id, card, concept, repetitions, interval_days, ease, due)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (lecture_id, card) DO UPDATE SET
            concept = excluded.concept,
            repetitions = excluded.repetitions,
            interval_days = excluded.interval_days,
            ease = excluded.ease,
            due = excluded.due,
            reviewed_at = CURRENT_TIMESTAMP
        """,
        (lecture_id, card, concept, state["repetitions"], state["interval"], state["ease"], state["due"]),
    )
    conn.commit()
    conn.close()
