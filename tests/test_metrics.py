from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "cpu" in data
    assert "memory" in data
    assert "disk" in data
    assert "network_sent" in data
    assert "network_received" in data
