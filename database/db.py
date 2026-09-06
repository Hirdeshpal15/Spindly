import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()
    finally:
        conn.close()


def seed_db():
    conn = get_db()
    try:
        row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
        if row["count"] > 0:
            return

        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash),
        )
        user_id = cursor.lastrowid

        today = date.today()
        y, m = today.year, today.month

        sample_expenses = [
            (user_id, 450.00,  "Food",          f"{y:04d}-{m:02d}-02", "Grocery shopping"),
            (user_id, 120.50,  "Transport",     f"{y:04d}-{m:02d}-03", "Auto rickshaw fare"),
            (user_id, 1500.00, "Bills",         f"{y:04d}-{m:02d}-05", "Electricity bill"),
            (user_id, 600.00,  "Health",        f"{y:04d}-{m:02d}-08", "Pharmacy purchase"),
            (user_id, 350.00,  "Entertainment", f"{y:04d}-{m:02d}-10", "Movie tickets"),
            (user_id, 2200.00, "Shopping",      f"{y:04d}-{m:02d}-14", "New shoes"),
            (user_id, 90.00,   "Other",         f"{y:04d}-{m:02d}-18", "Miscellaneous purchase"),
            (user_id, 275.75,  "Food",          f"{y:04d}-{m:02d}-22", "Dinner with friends"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) "
            "VALUES (?, ?, ?, ?, ?)",
            sample_expenses,
        )
        conn.commit()
    finally:
        conn.close()
