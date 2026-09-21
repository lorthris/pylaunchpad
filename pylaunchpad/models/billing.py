"""Billing, order, and subscription database models."""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pylaunchpad.models.base import BaseModel


class Order(BaseModel):
    """Customer one-time purchase record synchronized from Polar.sh."""

    __tablename__ = "orders"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    polar_order_id = Column(String(128), unique=True, index=True, nullable=False)
    product_id = Column(String(128), index=True, nullable=False)
    product_name = Column(String(255), nullable=False)
    amount = Column(Integer, nullable=False)  # Amount in cents (e.g. 2900 = $29.00)
    currency = Column(String(10), default="usd", nullable=False)
    status = Column(String(50), default="paid", nullable=False)

    # Relationships
    user = relationship("User", back_populates="orders")


class Subscription(BaseModel):
    """Customer recurring subscription record synchronized from Polar.sh."""

    __tablename__ = "subscriptions"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    polar_subscription_id = Column(String(128), unique=True, index=True, nullable=False)
    product_id = Column(String(128), index=True, nullable=False)
    status = Column(String(50), default="active", nullable=False)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
