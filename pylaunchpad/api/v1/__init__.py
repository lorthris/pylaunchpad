"""API v1 router aggregation."""

from fastapi import APIRouter
from pylaunchpad.api.v1.health import router as health_router
from pylaunchpad.api.v1.auth import router as auth_router
from pylaunchpad.api.v1.billing import router as billing_router
from pylaunchpad.api.v1.apikeys import router as apikeys_router
from pylaunchpad.api.v1.webhook import router as webhook_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(billing_router)
api_v1_router.include_router(apikeys_router)
api_v1_router.include_router(webhook_router)

__all__ = ["api_v1_router"]
