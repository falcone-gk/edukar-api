import logging
import time

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class Culqi:
    def __init__(self):
        self.api_key = settings.CULQI_API_KEY
        self.base_url = "https://api.culqi.com/v2"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def create_charge(self, sell, **kwargs):
        payload = {
            "amount": int(sell.total_cost * 100),
            "email": kwargs.get("email"),
            "source_id": kwargs.get("token"),
            "currency_code": "PEN",
            "antifraud_details": {
                "first_name": kwargs.get("first_name"),
                "last_name": kwargs.get("last_name"),
                "email": kwargs.get("email"),
                "phone_number": kwargs.get("phone_number"),
                "device_finger_print": kwargs.get("device_id"),
            },
            "authentication_3DS": kwargs.get("parameters_3DS", None),
        }
        url = f"{self.base_url}/charges"
        response = requests.post(url, json=payload, headers=self.headers)

        return response

    def create_order(self, sell):
        products = list(sell.products.values_list("id", flat=True))
        payload = {
            "amount": int(sell.total_cost * 100),
            "description": f"Compra de los productos con ID {', '.join(map(str, products))}",
            "order_number": sell.order_number,
            "currency_code": "PEN",
            "expiration_date": int(time.time()) + 60 * 60,  # 1 hora
            "client_details": {
                "first_name": sell.user_name,
                "last_name": sell.user_last_name,
                "email": sell.user_email,
                "phone_number": sell.user_phone_number,
            },
            "confirm": False,
        }
        url = f"{self.base_url}/orders"
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Orden creada exitosamente con id: {response.json()}")
            return response.json()
        except requests.HTTPError:
            error_data = response.json()
            merchant_message = error_data.get("merchant_message")
            logger.error(f"Error al crear orden: {merchant_message}")
            return {
                "error": merchant_message,
                "status_code": response.status_code,
                "response_text": error_data.get("user_message"),
            }
        except requests.RequestException as e:
            logger.error(f"Error al crear orden: {str(e)}")
            return {"error": str(e)}
