"""Billing and checkout validation schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class CheckoutSessionCreate(BaseModel):
    """Request payload for generating a Polar.sh checkout session."""
    product_id: str
    success_url: Optional[str] = None
    customer_email: Optional[str] = None


class CheckoutSessionResponse(BaseModel):
    """Response containing the generated Polar.sh checkout URL."""
    checkout_url: str


class OrderRead(BaseModel):
    """Schema for customer order representation."""
    id: int
    polar_order_id: str
    product_id: str
    product_name: str
    amount: int
    currency: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubscriptionRead(BaseModel):
    """Schema for customer subscription status."""
    id: int
    polar_subscription_id: str
    product_id: str
    status: str
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PolarWebhookPayload(BaseModel):
    """Incoming Polar.sh webhook event envelope."""
    type: str
    data: Dict[str, Any]


class LicenseKeyValidateRequest(BaseModel):
    """Request payload for validating a Polar license key."""
    key: str


class LicenseKeyValidateResponse(BaseModel):
    """Response returned when validating a Polar license key."""
    valid: bool
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
