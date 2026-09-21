"""Billing, checkout, and customer subscription routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pylaunchpad.database import get_db
from pylaunchpad.models.user import User
from pylaunchpad.models.billing import Order, Subscription
from pylaunchpad.schemas.billing import (
    CheckoutSessionCreate,
    CheckoutSessionResponse,
    OrderRead,
    SubscriptionRead,
)
from pylaunchpad.auth.dependencies import get_current_active_user, get_current_user
from pylaunchpad.billing.polar import polar_client

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout(
    payload: CheckoutSessionCreate,
    current_user: Optional[User] = Depends(get_current_user),
) -> CheckoutSessionResponse:
    """Generate a Polar.sh hosted checkout URL for one-time or subscription purchase."""
    customer_email = payload.customer_email
    if current_user:
        customer_email = current_user.email

    session = await polar_client.create_checkout_session(
        product_id=payload.product_id,
        success_url=payload.success_url,
        customer_email=customer_email,
    )

    url = session.get("url")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate checkout session",
        )

    return CheckoutSessionResponse(checkout_url=url)


@router.post("/portal")
async def get_customer_portal(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Generate customer portal link for authenticated user to manage billing."""
    if not current_user.polar_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active billing profile found for this account",
        )

    portal_url = await polar_client.create_customer_portal_session(current_user.polar_customer_id)
    if not portal_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create customer portal session",
        )

    return {"portal_url": portal_url}


@router.get("/orders", response_model=List[OrderRead])
def list_user_orders(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[Order]:
    """Retrieve purchase history for current user."""
    return db.query(Order).filter(Order.user_id == current_user.id).order_by(Order.created_at.desc()).all()


@router.get("/subscriptions", response_model=List[SubscriptionRead])
def list_user_subscriptions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> List[Subscription]:
    """Retrieve active subscriptions for current user."""
    return db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
