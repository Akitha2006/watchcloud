import sqlite3
import os
import hashlib
from backend.config import DATA_DIR

DB_PATH = os.path.join(DATA_DIR, "watchcloud.db")

def get_db_connection():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'USER',
        is_locked INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Try adding email column if missing in existing database table
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except Exception:
        pass

    # Create Incidents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        severity TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        source TEXT NOT NULL,
        description TEXT NOT NULL,
        evidence TEXT NOT NULL,
        possible_cause TEXT,
        remediation TEXT,
        verification TEXT,
        status TEXT NOT NULL DEFAULT 'DETECTED',
        report TEXT
    );
    """)

    # Create Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        level TEXT NOT NULL,
        event TEXT NOT NULL,
        message TEXT NOT NULL,
        source TEXT NOT NULL,
        metadata TEXT
    );
    """)

    # Create Agent Activities Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        incident_id TEXT NOT NULL,
        agent TEXT NOT NULL,
        status TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()

    # Seed Default Accounts if missing
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'user'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role, is_locked) VALUES (?, ?, ?, ?, ?)",
            ("user", "user@watchcloud.io", hash_password("user123"), "USER", 0)
        )
    else:
        cursor.execute("UPDATE users SET email = 'user@watchcloud.io' WHERE username = 'user' AND (email IS NULL OR email = '')")

    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role, is_locked) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin@watchcloud.io", hash_password("admin123"), "ADMIN", 0)
        )
    else:
        cursor.execute("UPDATE users SET email = 'admin@watchcloud.io' WHERE username = 'admin' AND (email IS NULL OR email = '')")

    conn.commit()
    conn.close()
