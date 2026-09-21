"""Automated tests for API key management, health checks, and security headers."""

from pylaunchpad.models.user import User
from pylaunchpad.auth.security import hash_password, create_access_token


def test_health_check_endpoint(client):
    """Verify health endpoint response and database connectivity."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "PyLaunchpad"
    assert data["database"] == "connected"
    assert "version" in data


def test_security_headers_middleware(client):
    """Verify that required security headers and execution timing are attached."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "X-Process-Time-Ms" in response.headers


def test_api_key_lifecycle_and_authentication(client, db_session):
    """Test full API key generation, usage in X-API-Key header, and revocation."""
    # 1. Create a user
    user = User(
        email="apikey_tester@example.com",
        hashed_password=hash_password("Pass123456!"),
        full_name="API Tester",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(str(user.id))
    auth_headers = {"Authorization": f"Bearer {token}"}

    # 2. Create API Key
    create_res = client.post(
        "/api/v1/apikeys",
        json={"name": "CLI Integration Key", "rate_limit": 100},
        headers=auth_headers,
    )
    assert create_res.status_code == 201
    key_data = create_res.json()
    assert "api_key" in key_data
    raw_key = key_data["api_key"]
    key_id = key_data["id"]
    assert raw_key.startswith("pylp_live_")

    # 3. List API keys (verifies plaintext key is not leaked)
    list_res = client.get("/api/v1/apikeys", headers=auth_headers)
    assert list_res.status_code == 200
    keys_list = list_res.json()
    assert len(keys_list) == 1
    assert "api_key" not in keys_list[0]
    assert keys_list[0]["key_prefix"] == raw_key[:14]

    # 4. Revoke API Key
    del_res = client.delete(f"/api/v1/apikeys/{key_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # 5. List keys again to ensure it is marked inactive
    list_res2 = client.get("/api/v1/apikeys", headers=auth_headers)
    assert list_res2.status_code == 200
    assert list_res2.json()[0]["is_active"] is False
