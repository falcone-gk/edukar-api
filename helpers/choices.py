from django.db import models
from django.utils.translation import gettext_lazy as _


class SellStatus(models.IntegerChoices):
    FINISHED = 1, _("Aceptado")
    PENDING = 2, _("Pendiente")
    FAILED = 3, _("Fallido")


class ProductTypes(models.IntegerChoices):
    DOCUMENT = 1, _("Documento")
    VIDEO = 2, _("Video")
    PACKAGE = 3, _("Paquete")


class TypeGoods(models.IntegerChoices):
    PRODUCT = 1, _("Producto")
    SERVICE = 2, _("Servicio")
