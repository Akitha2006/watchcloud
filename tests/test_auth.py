from fastapi.testclient import TestClient
from app import app
from backend.database import init_db

init_db()
client = TestClient(app)

def test_login_page():
    res = client.get("/login")
    assert res.status_code == 200
    assert "WATCHCLOUD APPLICATION" in res.text

def test_user_login_success():
    res = client.post("/login", data={"username": "user", "password": "user123"}, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/user/dashboard"

def test_admin_login_success():
    res = client.post("/login", data={"username": "admin", "password": "admin123"}, follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/admin/dashboard"

def test_privilege_escalation_detection():
    # Login as user
    client.post("/login", data={"username": "user", "password": "user123"})
    # Attempt admin dashboard access -> triggers privilege escalation incident
    res = client.get("/admin/dashboard", follow_redirects=False)
    assert res.status_code == 303
    assert "Access+Denied" in res.headers["location"]
