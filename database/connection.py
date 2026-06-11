import sqlite3
from pathlib import Path
from config import DATABASE_PATH, ensure_dirs


def get_connection():
    ensure_dirs()
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
        if not cursor.fetchone():
            schema_path = Path(__file__).parent / 'migrations' / 'schema.sql'
            with open(schema_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
        conn.commit()
