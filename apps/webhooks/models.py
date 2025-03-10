# Create your models here.
from django.db import models

from apps.core.models import TimeStampModel


class WebhooksEvent(TimeStampModel):
    """Eventos de webhooks"""

    class Meta:
        db_table = "webhooks_events"

    # payload recibido
    full_payload = models.JSONField(null=True)

    # culqi
    webhook = models.CharField(max_length=50)
