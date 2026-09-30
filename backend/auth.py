import uuid
from typing import Optional, Dict
from fastapi import Request, HTTPException, status
from backend.database import get_db_connection, hash_password

# In-memory session store: session_id -> {username, role}
active_sessions: Dict[str, dict] = {}

def create_session(username: str, role: str) -> str:
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "username": username,
        "role": role
    }
    return session_id

def destroy_session(session_id: str):
    if session_id in active_sessions:
        del active_sessions[session_id]

def get_current_user_from_request(request: Request) -> Optional[dict]:
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in active_sessions:
        return None
    return active_sessions[session_id]

def authenticate_user(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return None, "user_not_found"

    if user["is_locked"] == 1:
        return None, "account_locked"

    if user["password_hash"] != hash_password(password):
        return None, "invalid_password"

    return dict(user), "success"

def register_new_user(username: str, password: str) -> tuple:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists."

    hashed = hash_password(password)
    # Always register as USER role (never ADMIN)
    cursor.execute(
        "INSERT INTO users (username, password_hash, role, is_locked) VALUES (?, ?, ?, ?)",
        (username, hashed, "USER", 0)
    )
    conn.commit()
    conn.close()
    return True, "User registered successfully."
