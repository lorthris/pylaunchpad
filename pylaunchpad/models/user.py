"""User account database model."""

from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from pylaunchpad.models.base import BaseModel


class User(BaseModel):
    """User account entity for authentication and customer relations."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Polar.sh customer identifier
    polar_customer_id = Column(String(128), unique=True, index=True, nullable=True)

    # Relationships
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
