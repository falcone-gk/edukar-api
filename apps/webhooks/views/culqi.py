import json
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from store.models import Sell

from apps.webhooks.models import WebhooksEvent
from apps.webhooks.serializer import WebhooksSerializer
from utils.products import assign_product_to_user

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class ChangeOrderWebhook(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = WebhooksSerializer
    queryset = WebhooksEvent.objects.none()

    def post(self, request):
        payload = request.data.copy()

        # Registra el payload recibido para depuración
        logger.info(f"Payload recibido: {payload}")

        if payload.get("type") != "order.status.changed":
            logger.error(f"Tipo de webhook no válido: {payload.get('type')}")
            return Response(status=status.HTTP_400_BAD_REQUEST)

        WebhooksEvent.objects.create(
            full_payload=payload,
            webhook="culqi",
        )

        data = json.loads(payload["data"])
        order_id = data["id"]
        order_status = data["state"]
        sells = Sell.objects.filter(order_id=order_id)

        if sells.exists() and order_status == "paid":
            sell = sells.first()
            sell.mark_as_paid(data)
            assign_product_to_user(sell)

            logger.info(
                f"El usuario {sell.user.username} realizó su compra de manera exitosa: "
                f"ID de compra {sell.id}"
            )

        else:
            logger.error(
                f"No se encontró un 'sell' para el ID de orden {order_id} "
                "o el estado de la orden no es 'paid'"
            )

        message = {
            "data": {
                "message": "WEBHOOK CONFIRMED",
            }
        }
        return Response(message, status=status.HTTP_200_OK)
