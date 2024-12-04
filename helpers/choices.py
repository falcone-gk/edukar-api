from django.db import models
from django.utils.translation import gettext_lazy as _


class SellStatus(models.IntegerChoices):
    FINISHED = 1, _("Aceptado")
    PENDING = 2, _("Pendiente")
    INTERESTED = 3, _("Interesado")
