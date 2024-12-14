from django.db import models
from django.utils.translation import gettext_lazy as _


class SellStatus(models.IntegerChoices):
    FINISHED = 1, _("Aceptado")
    PENDING = 2, _("Pendiente")
    ON_CART = 3, _("En carrito")


class ProductTypes(models.IntegerChoices):
    PRODUCT = 1, _("Producto")
    PACKAGE = 2, _("Paquete")
