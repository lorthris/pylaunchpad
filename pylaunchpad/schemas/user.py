"""User account validation schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Shared user properties."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for registering a new user."""
    password: str = Field(min_length=8, max_length=128, description="Password must be at least 8 characters")


class UserUpdate(BaseModel):
    """Schema for updating existing user profile."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)


class UserRead(UserBase):
    """Public user response schema."""
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """Schema for user credentials authentication."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT Bearer access token response."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT payload data."""
    sub: str
    exp: int
