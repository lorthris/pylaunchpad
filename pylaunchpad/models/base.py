"""Base models and shared timestamp mixins."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime
from pylaunchpad.database import Base


def utc_now() -> datetime:
    """Return timezone-aware current UTC time."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Shared created_at and updated_at timestamps."""

    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)


class BaseModel(Base, TimestampMixin):
    """Abstract base model with integer primary key and timestamps."""

    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
