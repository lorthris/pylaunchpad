"""Cryptographic security utilities for passwords, tokens, and API keys."""

import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from pylaunchpad.config import settings

PBKDF2_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with cryptographically secure salt."""
    salt = secrets.token_hex(16)
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    hash_hex = hash_bytes.hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${hash_hex}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against stored PBKDF2 hash using constant-time comparison."""
    try:
        algorithm, iterations_str, salt, stored_hash = hashed_password.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_str)
        test_bytes = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return hmac.compare_digest(test_bytes.hex(), stored_hash)
    except Exception:
        return False


def _base64url_encode(data: bytes) -> str:
    """Encode bytes to URL-safe base64 string without trailing padding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64url_decode(data_str: str) -> bytes:
    """Decode URL-safe base64 string with required padding."""
    padding = 4 - (len(data_str) % 4)
    if padding != 4:
        data_str += "=" * padding
    return base64.urlsafe_b64decode(data_str.encode("utf-8"))


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create signed HMAC-SHA256 JSON Web Token (JWT)."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()
    signature_b64 = _base64url_encode(signature)

    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify signature and expiration of JWT, returning payload dictionary or None."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

        expected_sig = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            signing_input,
            hashlib.sha256,
        ).digest()
        provided_sig = _base64url_decode(signature_b64)

        if not hmac.compare_digest(expected_sig, provided_sig):
            return None

        payload_bytes = _base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Check expiration
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if payload.get("exp", 0) < now_ts:
            return None

        return payload
    except Exception:
        return None


def generate_api_key() -> tuple[str, str, str]:
    """Generate a raw API key, its display prefix, and SHA-256 hash for database storage."""
    random_part = secrets.token_hex(24)
    raw_key = f"pylp_live_{random_part}"
    prefix = raw_key[:14]
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return raw_key, prefix, key_hash


def hash_api_key(raw_key: str) -> str:
    """Compute SHA-256 hash of a provided API key for lookup."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
