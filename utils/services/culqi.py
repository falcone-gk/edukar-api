import json

import requests
from django.conf import settings


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
