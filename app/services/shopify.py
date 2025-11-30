import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ShopifyService:
    def __init__(self):
        # Assuming we have these in settings, though not added yet.
        # In a real app, we'd need the shop URL and an access token.
        self.shop_url = "your-shop.myshopify.com" 
        self.access_token = "your_access_token"
        self.base_url = f"https://{self.shop_url}/admin/api/2023-07"
        self.headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }

    async def cancel_order(self, shopify_order_id: str):
        url = f"{self.base_url}/orders/{shopify_order_id}/cancel.json"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=self.headers, json={})
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to cancel Shopify order {shopify_order_id}: {e}")
                # Don't raise, just log for now
                return None

    async def add_order_note(self, shopify_order_id: str, note: str):
        url = f"{self.base_url}/orders/{shopify_order_id}.json"
        payload = {
            "order": {
                "id": shopify_order_id,
                "note": note
            }
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(url, headers=self.headers, json=payload)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Failed to update Shopify order {shopify_order_id}: {e}")
                return None

shopify_service = ShopifyService()
