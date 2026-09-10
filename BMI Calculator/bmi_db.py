"""
BMI Calculator - Advanced Tier (Data Layer)
SQLite database access module for persisting and querying BMI measurement history.
"""

import sqlite3
from datetime import datetime

DEFAULT_DB_PATH = "bmi_records.db"

class DatabaseError(Exception):
    """Custom exception raised when database operations fail."""
    pass

def _get_connection(db_path=DEFAULT_DB_PATH):
    """Establishes and returns a connection to the SQLite database."""
    return sqlite3.connect(db_path)

def init_db(db_path=DEFAULT_DB_PATH):
    """
    Initializes the SQLite database schema if the table does not exist.
    """
    conn = None
    try:
        conn = _get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )
        """)
        conn.commit()
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to initialize database: {e}") from e
    finally:
        if conn:
            conn.close()

def add_record(user_name, weight, height, bmi, category, db_path=DEFAULT_DB_PATH):
    """
    Inserts a new BMI record into the database with the current timestamp.
    """
    recorded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = None
    try:
        conn = _get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO records (user_name, weight, height, bmi, category, recorded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_name.strip(), float(weight), float(height), float(bmi), category, recorded_at))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to save record to database: {e}") from e
    finally:
        if conn:
            conn.close()

def get_users(db_path=DEFAULT_DB_PATH):
    """
    Retrieves a list of distinct user names present in the database history.
    """
    conn = None
    try:
        conn = _get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT user_name FROM records ORDER BY user_name ASC
        """)
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to fetch user list: {e}") from e
    finally:
        if conn:
            conn.close()

def get_records(user_name, db_path=DEFAULT_DB_PATH):
    """
    Retrieves all records for a specific user, sorted chronologically (oldest first).
    Returns a list of dictionaries with keys: id, user_name, weight, height, bmi, category, recorded_at.
    """
    conn = None
    try:
        conn = _get_connection(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, user_name, weight, height, bmi, category, recorded_at
            FROM records
            WHERE user_name = ?
            ORDER BY id ASC
        """, (user_name.strip(),))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise DatabaseError(f"Failed to fetch records for user '{user_name}': {e}") from e
    finally:
        if conn:
            conn.close()
