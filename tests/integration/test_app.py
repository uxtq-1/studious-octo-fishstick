from fastapi.testclient import TestClient

from travel_agent.main import create_app


def test_application_starts_and_reports_health():
    with TestClient(create_app()) as client:
        response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_home_discloses_simulation_mode():
    with TestClient(create_app()) as client:
        response = client.get("/")
    assert response.status_code == 200
    assert "Demonstration mode" in response.text
    assert "no real reservations or payments" in response.text
