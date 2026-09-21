"""Health check and service status endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from pylaunchpad.config import settings
from pylaunchpad.database import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=Dict[str, Any])
def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return health status, active configuration, and database connectivity."""
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return {
        "status": "healthy" if db_ok else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected" if db_ok else "error",
    }
