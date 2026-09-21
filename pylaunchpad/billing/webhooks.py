"""Polar.sh webhook verification and event processing."""

import base64
import hashlib
import hmac
import json
import logging
import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from pylaunchpad.config import settings
from pylaunchpad.models.user import User
from pylaunchpad.models.billing import Order, Subscription
from pylaunchpad.auth.security import hash_password

logger = logging.getLogger(__name__)

WEBHOOK_TOLERANCE_SECONDS = 300  # 5 minutes replay protection


def verify_webhook_signature(
    body: bytes,
    headers: Dict[str, str],
    secret: Optional[str] = None,
) -> bool:
    """Verify Standard Webhooks / Svix signature sent by Polar.sh."""
    signing_secret = secret or settings.POLAR_WEBHOOK_SECRET
    if not signing_secret:
        logger.warning("POLAR_WEBHOOK_SECRET is not configured; cannot verify signature")
        return False

    # Normalise headers
    header_map = {k.lower(): v for k, v in headers.items()}
    msg_id = header_map.get("webhook-id") or header_map.get("svix-id")
    msg_timestamp = header_map.get("webhook-timestamp") or header_map.get("svix-timestamp")
    msg_signature = header_map.get("webhook-signature") or header_map.get("svix-signature")

    if not msg_id or not msg_timestamp or not msg_signature:
        logger.warning("Missing required webhook signature headers")
        return False

    # Check timestamp to prevent replay attacks
    try:
        ts = int(msg_timestamp)
        now = int(time.time())
        if abs(now - ts) > WEBHOOK_TOLERANCE_SECONDS:
            logger.warning("Webhook timestamp out of tolerance: %s vs now %s", ts, now)
            return False
    except ValueError:
        logger.warning("Invalid webhook timestamp: %s", msg_timestamp)
        return False

    # Decode secret key
    try:
        if signing_secret.startswith("whsec_"):
            raw_b64 = signing_secret[6:]
            padding = 4 - (len(raw_b64) % 4)
            if padding != 4:
                raw_b64 += "=" * padding
            secret_bytes = base64.b64decode(raw_b64)
        else:
            secret_bytes = signing_secret.encode("utf-8")
    except Exception:
        secret_bytes = signing_secret.encode("utf-8")

    # Compute expected signature
    signed_payload = f"{msg_id}.{msg_timestamp}.".encode("utf-8") + body
    expected_hmac = hmac.new(secret_bytes, signed_payload, hashlib.sha256).digest()
    expected_sig = base64.b64encode(expected_hmac).decode("utf-8")

    # The header may contain multiple space-delimited signatures like "v1,sig1 v1,sig2"
    passed = False
    for item in msg_signature.split(" "):
        if item.startswith("v1,"):
            candidate = item[3:]
            if hmac.compare_digest(expected_sig, candidate):
                passed = True
                break

    return passed


def process_webhook_event(event_type: str, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Dispatch and process verified Polar.sh webhook event against database models."""
    logger.info("Processing Polar webhook event: %s", event_type)

    if event_type == "order.created":
        return _handle_order_created(data, db)
    elif event_type in ("subscription.created", "subscription.updated", "subscription.active"):
        return _handle_subscription_updated(data, db)
    elif event_type in ("subscription.canceled", "subscription.revoked"):
        return _handle_subscription_canceled(data, db)
    else:
        logger.info("Unhandled Polar webhook event type: %s", event_type)
        return {"status": "ignored", "event_type": event_type}


def _get_or_create_user(customer_email: str, customer_id: Optional[str], db: Session) -> User:
    """Retrieve existing user by email or create a placeholder customer account."""
    user = db.query(User).filter(User.email == customer_email).first()
    if not user:
        # Create unverified user account with random password
        random_pw = hash_password(base64.b64encode(hashlib.sha256(customer_email.encode()).digest()).decode())
        user = User(
            email=customer_email,
            hashed_password=random_pw,
            full_name=customer_email.split("@")[0],
            is_active=True,
            is_verified=False,
            polar_customer_id=customer_id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif customer_id and not user.polar_customer_id:
        user.polar_customer_id = customer_id
        db.commit()
        db.refresh(user)

    return user


def _handle_order_created(data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Provision entitlement for a completed customer order."""
    order_id = str(data.get("id"))
    customer = data.get("customer", {})
    customer_email = customer.get("email") or data.get("customer_email")

    if not customer_email:
        logger.warning("Order %s missing customer email", order_id)
        return {"status": "error", "message": "Missing customer email"}

    customer_id = customer.get("id")
    user = _get_or_create_user(customer_email, customer_id, db)

    # Check for duplicate order processing
    existing_order = db.query(Order).filter(Order.polar_order_id == order_id).first()
    if existing_order:
        logger.info("Order %s already processed", order_id)
        return {"status": "already_processed", "order_id": order_id}

    product = data.get("product", {})
    product_id = str(product.get("id") or data.get("product_id", "default_product"))
    product_name = str(product.get("name") or data.get("product_name", "PyLaunchpad Product"))
    amount = int(data.get("amount", 0))
    currency = str(data.get("currency", "usd")).lower()

    order = Order(
        user_id=user.id,
        polar_order_id=order_id,
        product_id=product_id,
        product_name=product_name,
        amount=amount,
        currency=currency,
        status="paid",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    logger.info("Successfully recorded order %s for user %s", order_id, user.email)
    return {"status": "success", "order_id": order_id, "user_id": user.id}


def _handle_subscription_updated(data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Sync recurring subscription state from Polar."""
    sub_id = str(data.get("id"))
    customer = data.get("customer", {})
    customer_email = customer.get("email") or data.get("customer_email")

    if not customer_email:
        return {"status": "error", "message": "Missing customer email"}

    customer_id = customer.get("id")
    user = _get_or_create_user(customer_email, customer_id, db)

    product_id = str(data.get("product_id") or (data.get("product") or {}).get("id", "default_plan"))
    status_str = str(data.get("status", "active"))
    cancel_at_period_end = bool(data.get("cancel_at_period_end", False))

    subscription = db.query(Subscription).filter(Subscription.polar_subscription_id == sub_id).first()
    if not subscription:
        subscription = Subscription(
            user_id=user.id,
            polar_subscription_id=sub_id,
            product_id=product_id,
            status=status_str,
            cancel_at_period_end=cancel_at_period_end,
        )
        db.add(subscription)
    else:
        subscription.status = status_str
        subscription.product_id = product_id
        subscription.cancel_at_period_end = cancel_at_period_end

    db.commit()
    logger.info("Updated subscription %s status to %s for user %s", sub_id, status_str, user.email)
    return {"status": "success", "subscription_id": sub_id, "state": status_str}


def _handle_subscription_canceled(data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Mark subscription as canceled."""
    sub_id = str(data.get("id"))
    subscription = db.query(Subscription).filter(Subscription.polar_subscription_id == sub_id).first()
    if subscription:
        subscription.status = "canceled"
        db.commit()
        logger.info("Marked subscription %s as canceled", sub_id)
        return {"status": "success", "subscription_id": sub_id, "state": "canceled"}

    return {"status": "not_found", "subscription_id": sub_id}
