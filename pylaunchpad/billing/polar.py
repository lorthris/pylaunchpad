"""Polar.sh Merchant of Record API client."""

import logging
from typing import Optional, Dict, Any
import httpx
from pylaunchpad.config import settings

logger = logging.getLogger(__name__)


class PolarClient:
    """Client for interacting with Polar.sh API for checkouts and customer management."""

    def __init__(self):
        self.env = settings.POLAR_ENVIRONMENT.lower()
        if self.env == "production":
            self.base_url = "https://api.polar.sh/v1"
            self.checkout_host = "https://buy.polar.sh"
        else:
            self.base_url = "https://sandbox-api.polar.sh/v1"
            self.checkout_host = "https://sandbox.polar.sh"

        self.access_token = settings.POLAR_ACCESS_TOKEN
        self.organization_id = settings.POLAR_ORGANIZATION_ID

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"PyLaunchpad/{settings.APP_VERSION}",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def get_checkout_url(self, product_id: str, success_url: Optional[str] = None, customer_email: Optional[str] = None) -> str:
        """Return direct Polar hosted checkout URL for a product."""
        url = f"{self.checkout_host}/products/{product_id}"
        params = []
        if customer_email:
            params.append(f"customer_email={customer_email}")
        if success_url:
            params.append(f"success_url={success_url}")
        if params:
            url += "?" + "&".join(params)
        return url

    async def create_checkout_session(
        self,
        product_id: str,
        success_url: Optional[str] = None,
        customer_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a hosted checkout session through the Polar API."""
        if not self.access_token:
            # Fallback to direct checkout link when API token is not yet configured
            direct_url = self.get_checkout_url(product_id, success_url, customer_email)
            return {"url": direct_url, "id": f"direct_{product_id}"}

        payload: Dict[str, Any] = {"product_id": product_id}
        if success_url:
            payload["success_url"] = success_url
        if customer_email:
            payload["customer_email"] = customer_email

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/checkouts/custom/",
                    json=payload,
                    headers=self._headers(),
                )
                if response.status_code in (200, 201):
                    return response.json()
                logger.warning("Polar API returned error: %s %s", response.status_code, response.text)
            except Exception as exc:
                logger.error("Failed to connect to Polar API: %s", exc)

        # Fallback to direct checkout link
        return {"url": self.get_checkout_url(product_id, success_url, customer_email), "id": f"direct_{product_id}"}

    async def create_customer_portal_session(self, polar_customer_id: str) -> Optional[str]:
        """Generate customer portal session link for managing billing and subscriptions."""
        if not self.access_token:
            return None

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/customer-portal/sessions/",
                    json={"customer_id": polar_customer_id},
                    headers=self._headers(),
                )
                if response.status_code in (200, 201):
                    data = response.json()
                    return data.get("customer_portal_url")
            except Exception as exc:
                logger.error("Failed to create customer portal session: %s", exc)

        return None

    async def validate_license_key(self, key: str) -> Dict[str, Any]:
        """Validate a Polar license key for product entitlement."""
        if not self.organization_id:
            return {"valid": False, "status": "unconfigured", "message": "Polar organization ID not configured"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/license-keys/validate",
                    json={"key": key.strip(), "organization_id": self.organization_id},
                    headers=self._headers(),
                )
                if response.status_code == 200:
                    data = response.json()
                    status_str = data.get("status", "granted")
                    is_valid = status_str == "granted"
                    return {
                        "valid": is_valid,
                        "status": status_str,
                        "message": "License key is valid and active" if is_valid else f"License key status: {status_str}",
                        "data": data,
                    }
                if response.status_code == 404:
                    return {"valid": False, "status": "not_found", "message": "License key was not found"}
                return {"valid": False, "status": "error", "message": response.text}
            except Exception as exc:
                logger.error("Failed to validate license key with Polar API: %s", exc)
                return {"valid": False, "status": "error", "message": str(exc)}


polar_client = PolarClient()
