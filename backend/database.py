import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "webpilot.db"


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def db_session():
    connection = connect()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db():
    with db_session() as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS workflows "
            "(id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL, "
            "status TEXT NOT NULL, applicant TEXT NOT NULL, result TEXT, "
            "created_at TEXT NOT NULL, updated_at TEXT NOT NULL)"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS audit_logs "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, workflow_id TEXT, "
            "action TEXT NOT NULL, details TEXT, source_url TEXT, "
            "status TEXT NOT NULL, timestamp TEXT NOT NULL)"
        )
