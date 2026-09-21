"""API Key management database model for developer programmatic access."""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from pylaunchpad.models.base import BaseModel


class APIKey(BaseModel):
    """Hashed API keys for authenticating programmatic API requests."""

    __tablename__ = "api_keys"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    key_prefix = Column(String(16), nullable=False)
    key_hash = Column(String(64), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    rate_limit = Column(Integer, default=60, nullable=False)  # requests per minute

    # Relationships
    user = relationship("User", back_populates="api_keys")
