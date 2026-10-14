import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "walletwise.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        merchant TEXT,
        category TEXT,
        payment_mode TEXT,
        description TEXT,
        date TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS budgets (
        month TEXT PRIMARY KEY,
        amount REAL NOT NULL
    );
    """)
    conn.commit()
    conn.close()