from fastapi.testclient import TestClient
from app import app
from incidents.manager import incident_manager

client = TestClient(app)

def test_incident_creation_and_retrieval():
    inc = incident_manager.create_incident({
        "type": "BRUTE_FORCE",
        "severity": "HIGH",
        "source": "192.168.1.100",
        "description": "Test incident",
        "evidence": ["5 failed attempts"]
    })

    assert inc["incident_id"].startswith("INC-")
    fetched = incident_manager.get_incident(inc["incident_id"])
    assert fetched["type"] == "BRUTE_FORCE"

def test_api_incidents_endpoints():
    res = client.get("/api/incidents")
    assert res.status_code == 200
    assert "incidents" in res.json()
