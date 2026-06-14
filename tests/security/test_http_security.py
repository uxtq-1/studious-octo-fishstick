from fastapi.testclient import TestClient

from travel_agent.config import Settings
from travel_agent.main import create_app


def _client(**settings_overrides):
    settings = Settings(**settings_overrides)
    return TestClient(create_app(settings))


def test_security_headers_are_present():
    with _client() as client:
        response = client.get("/")
    assert response.headers["content-security-policy"].startswith("default-src 'self'")
    assert response.headers["cross-origin-opener-policy"] == "same-origin"
    assert response.headers["cross-origin-embedder-policy"] == "credentialless"
    assert response.headers["cross-origin-resource-policy"] == "same-origin"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"]
    assert "strict-transport-security" not in response.headers


def test_hsts_is_enabled_in_production():
    with _client(environment="production", dev_auth_enabled=False) as client:
        response = client.get("/health/live")
    assert response.headers["strict-transport-security"].startswith("max-age=31536000")


def test_cors_rejects_unapproved_origin():
    with _client(allowed_origins=["https://travel.example.test"]) as client:
        response = client.options(
            "/api/v1/security/whoami",
            headers={
                "Origin": "https://attacker.example",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_protected_route_requires_authentication():
    with _client() as client:
        response = client.get("/api/v1/security/whoami")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
    assert "requestId" in response.json()


def test_wrong_role_cannot_access_admin_route():
    with _client() as client:
        response = client.get(
            "/api/v1/security/admin-check",
            headers={"X-Debug-User-Id": "user-1", "X-Debug-Role": "end_consumer"},
        )
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden"


def test_admin_role_can_access_admin_route():
    with _client() as client:
        response = client.get(
            "/api/v1/security/admin-check",
            headers={"X-Debug-User-Id": "admin-1", "X-Debug-Role": "platform_admin"},
        )
    assert response.status_code == 200
    assert response.json() == {"status": "authorized", "userId": "admin-1"}
    assert response.headers["cache-control"] == "no-store"


def test_oversized_content_length_is_rejected():
    with _client(max_request_body_bytes=1024) as client:
        response = client.post(
            "/api/v1/security/whoami",
            content=b"{}",
            headers={"Content-Type": "application/json", "Content-Length": "2048"},
        )
    assert response.status_code == 413


def test_mutation_requires_json_content_type():
    with _client() as client:
        response = client.post(
            "/api/v1/security/whoami",
            content="test",
            headers={"Content-Type": "text/plain"},
        )
    assert response.status_code == 415
