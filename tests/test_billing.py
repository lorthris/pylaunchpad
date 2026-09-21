"""Automated tests for Polar.sh webhook signature verification and billing workflows."""

import base64
import hashlib
import hmac
import json
import time
from pylaunchpad.config import settings
from pylaunchpad.billing.webhooks import verify_webhook_signature
from pylaunchpad.models.user import User
from pylaunchpad.models.billing import Order, Subscription


def _generate_valid_webhook_headers(body_bytes: bytes, secret: str, timestamp_offset: int = 0) -> dict:
    """Helper to craft valid Standard Webhook / Svix signature headers."""
    msg_id = "msg_test_123456"
    msg_timestamp = str(int(time.time()) + timestamp_offset)

    if secret.startswith("whsec_"):
        raw_b64 = secret[6:]
        padding = 4 - (len(raw_b64) % 4)
        if padding != 4:
            raw_b64 += "=" * padding
        secret_bytes = base64.b64decode(raw_b64)
    else:
        secret_bytes = secret.encode("utf-8")

    signed_payload = f"{msg_id}.{msg_timestamp}.".encode("utf-8") + body_bytes
    signature = base64.b64encode(
        hmac.new(secret_bytes, signed_payload, hashlib.sha256).digest()
    ).decode("utf-8")

    return {
        "webhook-id": msg_id,
        "webhook-timestamp": msg_timestamp,
        "webhook-signature": f"v1,{signature}",
        "Content-Type": "application/json",
    }


def test_webhook_signature_verification_success():
    """Verify that a properly signed payload validates successfully."""
    payload = json.dumps({"type": "test.ping", "data": {}}).encode("utf-8")
    secret = settings.POLAR_WEBHOOK_SECRET
    headers = _generate_valid_webhook_headers(payload, secret)

    assert verify_webhook_signature(body=payload, headers=headers, secret=secret) is True


def test_webhook_signature_verification_tampered_payload():
    """Verify that payload tampering causes signature check to fail."""
    payload = json.dumps({"type": "test.ping", "data": {}}).encode("utf-8")
    secret = settings.POLAR_WEBHOOK_SECRET
    headers = _generate_valid_webhook_headers(payload, secret)

    tampered_payload = json.dumps({"type": "test.tampered", "data": {}}).encode("utf-8")
    assert verify_webhook_signature(body=tampered_payload, headers=headers, secret=secret) is False


def test_webhook_signature_verification_replay_attack():
    """Verify that stale timestamps (> 300s) are rejected."""
    payload = json.dumps({"type": "test.ping", "data": {}}).encode("utf-8")
    secret = settings.POLAR_WEBHOOK_SECRET
    # Stale timestamp: 10 minutes in the past
    headers = _generate_valid_webhook_headers(payload, secret, timestamp_offset=-600)

    assert verify_webhook_signature(body=payload, headers=headers, secret=secret) is False


def test_order_created_webhook_endpoint(client, db_session):
    """Test full order.created webhook processing via API endpoint."""
    order_data = {
        "type": "order.created",
        "data": {
            "id": "order_polar_987654",
            "customer": {
                "id": "cust_12345",
                "email": "customer@indiebuilder.com",
            },
            "product": {
                "id": "prod_pylaunchpad_pro",
                "name": "PyLaunchpad Pro Licence",
            },
            "amount": 2900,
            "currency": "usd",
        },
    }
    body_bytes = json.dumps(order_data).encode("utf-8")
    headers = _generate_valid_webhook_headers(body_bytes, settings.POLAR_WEBHOOK_SECRET)

    response = client.post("/api/v1/webhooks/polar", data=body_bytes, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "received"
    assert res_data["event_type"] == "order.created"

    # Verify user and order were created in database
    user = db_session.query(User).filter(User.email == "customer@indiebuilder.com").first()
    assert user is not None
    assert user.polar_customer_id == "cust_12345"

    order = db_session.query(Order).filter(Order.polar_order_id == "order_polar_987654").first()
    assert order is not None
    assert order.amount == 2900
    assert order.product_name == "PyLaunchpad Pro Licence"
    assert order.user_id == user.id


def test_subscription_lifecycle_webhook(client, db_session):
    """Test subscription creation and cancellation webhook events."""
    # 1. subscription.active
    sub_data = {
        "type": "subscription.active",
        "data": {
            "id": "sub_polar_abc123",
            "customer": {
                "id": "cust_sub_555",
                "email": "subscriber@domain.com",
            },
            "product_id": "prod_pro_plan",
            "status": "active",
        },
    }
    body_bytes = json.dumps(sub_data).encode("utf-8")
    headers = _generate_valid_webhook_headers(body_bytes, settings.POLAR_WEBHOOK_SECRET)

    res = client.post("/api/v1/webhooks/polar", data=body_bytes, headers=headers)
    assert res.status_code == 200

    sub = db_session.query(Subscription).filter(Subscription.polar_subscription_id == "sub_polar_abc123").first()
    assert sub is not None
    assert sub.status == "active"

    # 2. subscription.canceled
    cancel_data = {
        "type": "subscription.canceled",
        "data": {
            "id": "sub_polar_abc123",
            "status": "canceled",
        },
    }
    body_bytes_cancel = json.dumps(cancel_data).encode("utf-8")
    headers_cancel = _generate_valid_webhook_headers(body_bytes_cancel, settings.POLAR_WEBHOOK_SECRET)

    res_cancel = client.post("/api/v1/webhooks/polar", data=body_bytes_cancel, headers=headers_cancel)
    assert res_cancel.status_code == 200

    db_session.refresh(sub)
    assert sub.status == "canceled"


def test_validate_license_endpoint(client, monkeypatch):
    """Verify license key validation API endpoint."""
    async def mock_validate_success(key: str):
        return {
            "valid": True,
            "status": "granted",
            "message": "License key is valid and active",
            "data": {"id": "lic_123", "status": "granted"},
        }

    async def mock_validate_invalid(key: str):
        return {
            "valid": False,
            "status": "not_found",
            "message": "License key was not found",
            "data": None,
        }

    from pylaunchpad.api.v1.billing import polar_client

    # Test valid key
    monkeypatch.setattr(polar_client, "validate_license_key", mock_validate_success)
    res = client.post("/api/v1/billing/license/validate", json={"key": "PYLP-VALID-KEY"})
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["status"] == "granted"

    # Test invalid key
    monkeypatch.setattr(polar_client, "validate_license_key", mock_validate_invalid)
    res_invalid = client.post("/api/v1/billing/license/validate", json={"key": "PYLP-INVALID-KEY"})
    assert res_invalid.status_code == 200
    data_invalid = res_invalid.json()
    assert data_invalid["valid"] is False
    assert data_invalid["status"] == "not_found"
