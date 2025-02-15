import json
import logging

import requests
from django.conf import settings
from store.models import Order

logger = logging.getLogger(__name__)


class Culqi:
    def __init__(self):
        self.api_key = settings.CULQI_API_KEY
        self.base_url = "https://api.culqi.com/v2"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def create_charge(self, amount, email, source_id, currency_code):
        payload = {
            "amount": amount * 100,
            "email": email,
            "source_id": source_id,
            "currency_code": currency_code,
        }
        url = f"{self.base_url}/charges"
        response = requests.post(url, json=payload, headers=self.headers)
        content = json.loads(response.content)
        return content

    def create_order(self, order: Order):
        payload = {
            "amount": order.amount * 100,
            "description": order.description,
            "order_number": f"edk-ord-{str(order.id).zfill(8)}",
            "currency_code": order.currency_code,
            "expiration_date": order.expiration_date,
            "client_details": order.client_details,
            "confirm": False,
        }
        url = f"{self.base_url}/orders"
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Orden creada exitosamente con id: {order.id}")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error al crear orden: {str(e)}")
            return {"error": str(e)}
