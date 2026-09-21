"""Polar.sh incoming webhook receiver."""

import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.orm import Session

from pylaunchpad.database import get_db
from pylaunchpad.billing.webhooks import verify_webhook_signature, process_webhook_event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/polar", status_code=status.HTTP_200_OK)
async def handle_polar_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Verify and process incoming Standard Webhook events from Polar.sh."""
    raw_body = await request.body()
    headers = dict(request.headers)

    # 1. Verify cryptographic signature
    is_valid = verify_webhook_signature(body=raw_body, headers=headers)
    if not is_valid:
        logger.warning("Rejected Polar webhook: invalid HMAC signature")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook signature",
        )

    # 2. Parse payload
    try:
        payload = json.loads(raw_body.decode("utf-8"))
        event_type = payload.get("type", "unknown")
        event_data = payload.get("data", {})
    except Exception as exc:
        logger.error("Malformed webhook JSON payload: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload",
        )

    # 3. Process event against database
    result = process_webhook_event(event_type=event_type, data=event_data, db=db)
    return {"status": "received", "event_type": event_type, "result": result}
