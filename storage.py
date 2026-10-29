import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path("outreach.db")

def connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS outreach (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            profile_url TEXT NOT NULL UNIQUE,
            email TEXT,
            subject TEXT,
            email_message TEXT,
            dm_message TEXT,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)

def was_contacted(profile_url):
    if not profile_url:
        return False
    with connect() as conn:
        row = conn.execute("SELECT 1 FROM outreach WHERE profile_url = ?", (profile_url,)).fetchone()
    return row is not None

def log_outreach(name, profile_url, email, subject, email_message, dm_message, status):
    if not profile_url:
        raise ValueError("Profile URL is required to prevent duplicate outreach.")
    with connect() as conn:
        conn.execute("""
        INSERT INTO outreach (name, profile_url, email, subject, email_message, dm_message, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, profile_url, email, subject, email_message, dm_message, status))

def get_outreach_log():
    with connect() as conn:
        return pd.read_sql_query("SELECT name, profile_url, email, subject, status, created_at FROM outreach ORDER BY created_at DESC", conn)
