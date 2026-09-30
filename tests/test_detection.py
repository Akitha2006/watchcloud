from fastapi.testclient import TestClient
from app import app
from detection.detector import detector

client = TestClient(app)

def test_ddos_detection():
    res = detector.check_traffic(60, "192.168.1.100")
    assert res["detected"] is True
    assert res["type"] == "DDOS_TRAFFIC"
    assert res["severity"] == "CRITICAL"

def test_sql_injection_detection():
    res = detector.check_sql("' OR 1=1;--", "192.168.1.101")
    assert res["detected"] is True
    assert res["type"] == "SQL_INJECTION"

def test_brute_force_detection():
    res = detector.check_brute_force(5, "admin_user", "192.168.1.102")
    assert res["detected"] is True
    assert res["type"] == "BRUTE_FORCE"

def test_privilege_escalation_detection():
    res = detector.check_privilege("normal_user", "admin", "user_1", "192.168.1.103")
    assert res["detected"] is True
    assert res["type"] == "PRIVILEGE_ESCALATION"

def test_simulations_via_api():
    ddos_res = client.post("/simulate/ddos", json={"request_count": 60})
    assert ddos_res.status_code == 200
    assert ddos_res.json()["status"] == "RESOLVED"

    sql_res = client.post("/simulate/sql-injection", json={"payload": "UNION SELECT"})
    assert sql_res.status_code == 200
    assert sql_res.json()["status"] == "RESOLVED"
