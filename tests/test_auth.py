"""Automated unit and integration tests for authentication and security."""

from datetime import timedelta
from pylaunchpad.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_password_hashing():
    """Verify PBKDF2 password hashing and verification logic."""
    raw = "SuperSecretP@ssword123"
    hashed = hash_password(raw)

    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_token_lifecycle():
    """Verify JWT creation, signature, and decoding."""
    subject = "user_42"
    token = create_access_token(subject=subject, expires_delta=timedelta(minutes=15))

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == subject
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_expired_token():
    """Verify expired token rejection."""
    subject = "user_99"
    expired_token = create_access_token(subject=subject, expires_delta=timedelta(seconds=-10))

    payload = decode_access_token(expired_token)
    assert payload is None


def test_user_registration_and_login(client):
    """Test full user registration and login flow via REST API."""
    user_data = {
        "email": "tester@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test Developer",
    }

    # 1. Register user
    reg_response = client.post("/api/v1/auth/register", json=user_data)
    assert reg_response.status_code == 201
    created = reg_response.json()
    assert created["email"] == user_data["email"]
    assert created["full_name"] == user_data["full_name"]
    assert "id" in created

    # 2. Prevent duplicate registration
    dup_response = client.post("/api/v1/auth/register", json=user_data)
    assert dup_response.status_code == 400

    # 3. Successful login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 4. Access protected profile endpoint
    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    profile = me_response.json()
    assert profile["email"] == user_data["email"]

    # 5. Invalid credentials rejection
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401
