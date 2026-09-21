"""API Key validation schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class APIKeyCreate(BaseModel):
    """Payload for creating a new developer API key."""
    name: str = Field(min_length=1, max_length=100, description="Descriptive name for the API key")
    rate_limit: int = Field(default=60, ge=1, le=1000, description="Allowed requests per minute")


class APIKeyRead(BaseModel):
    """Schema for listing user API keys without revealing secret."""
    id: int
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: Optional[datetime] = None
    rate_limit: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIKeyCreatedResponse(APIKeyRead):
    """Response returned upon key creation containing the plaintext key once."""
    api_key: str = Field(description="Full secret API key. Store safely; not shown again.")
