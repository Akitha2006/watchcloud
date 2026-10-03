from fastapi.testclient import TestClient
from app import app
from backend.database import init_db, get_db_connection
from backend.state import system_state

init_db()
client = TestClient(app)

def reset_test_user_state():
    system_state.failed_login_counters["user"] = 0
    system_state.locked_accounts.discard("user")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_locked = 0, role = 'USER' WHERE username = 'user'")
    cursor.execute("UPDATE users SET is_locked = 0, role = 'ADMIN' WHERE username = 'admin'")
    conn.commit()
    conn.close()

def test_login_page():
    res = client.get("/login")
    assert res.status_code == 200
    assert "WATCHCLOUD APPLICATION" in res.text

def test_user_login_success():
    reset_test_user_state()
    res = client.post("/login", data={"username": "user", "password": "user123", "login_role": "USER"}, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/user/dashboard"

def test_admin_login_success():
    reset_test_user_state()
    res = client.post("/login", data={"username": "admin", "password": "admin123", "login_role": "ADMIN"}, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/admin/dashboard"

def test_privilege_escalation_detection():
    reset_test_user_state()
    # Login as user
    client.post("/login", data={"username": "user", "password": "user123", "login_role": "USER"})
    # Attempt admin dashboard access -> triggers privilege escalation incident
    res = client.get("/admin/dashboard", follow_redirects=False)
    assert res.status_code == 303
    assert "Access+Denied" in res.headers["location"]
