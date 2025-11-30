import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.default_api_token = settings.WHATSAPP_API_TOKEN
        self.default_phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID

    def _get_headers(self, api_token):
        return {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def _get_url(self, phone_number_id):
        return f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"

    async def send_template_message(self, to_phone: str, template_name: str, language_code: str = "en", components: list = None, merchant=None):
        api_token = merchant.whatsapp_api_token if merchant and merchant.whatsapp_api_token else self.default_api_token
        phone_number_id = merchant.whatsapp_phone_number_id if merchant and merchant.whatsapp_phone_number_id else self.default_phone_number_id
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self._get_url(phone_number_id), 
                    headers=self._get_headers(api_token), 
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"WhatsApp API Error: {e.response.text}")
                raise e
            except Exception as e:
                logger.error(f"Error sending WhatsApp message: {str(e)}")
                raise e

    async def send_interactive_message(self, to_phone: str, body_text: str, buttons: list, merchant=None):
        api_token = merchant.whatsapp_api_token if merchant and merchant.whatsapp_api_token else self.default_api_token
        phone_number_id = merchant.whatsapp_phone_number_id if merchant and merchant.whatsapp_phone_number_id else self.default_phone_number_id

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body_text
                },
                "action": {
                    "buttons": buttons
                }
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self._get_url(phone_number_id), 
                    headers=self._get_headers(api_token), 
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"WhatsApp API Error: {e.response.text}")
                raise e

    async def send_list_message(self, to_phone: str, body_text: str, button_text: str, sections: list, merchant=None):
        api_token = merchant.whatsapp_api_token if merchant and merchant.whatsapp_api_token else self.default_api_token
        phone_number_id = merchant.whatsapp_phone_number_id if merchant and merchant.whatsapp_phone_number_id else self.default_phone_number_id

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {
                    "text": body_text
                },
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self._get_url(phone_number_id), 
                    headers=self._get_headers(api_token), 
                    json=payload
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"WhatsApp API Error: {e.response.text}")
                raise e

whatsapp_service = WhatsAppService()
