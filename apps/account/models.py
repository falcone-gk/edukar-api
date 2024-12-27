from django.contrib.auth.models import User
from django.db import models
from django_resized import ResizedImageField
from rest_framework.exceptions import ValidationError
from store.models import Product

# Create your models here.


class Profile(models.Model):
    def image_upload(self, filename):
        ext = filename.split(".")[-1]
        fullname = "{}.{}".format(self.user.username, ext)
        return f"profile/{fullname}"

    user = models.ForeignKey(
        User, related_name="profile", on_delete=models.CASCADE
    )
    picture = ResizedImageField(
        size=[500, 500],
        quality=75,
        force_format="WebP",
        upload_to=image_upload,
        default="default-avatar.jpg",
    )
    about_me = models.TextField(max_length=255, default="No hay información")

    def __str__(self):
        return self.user.username


class UserProduct(models.Model):
    user = models.ForeignKey(
        User, related_name="products", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="users", on_delete=models.CASCADE
    )
    date = models.DateField(null=False, auto_now_add=True)

    @classmethod
    def validate_product_purchase(cls, user: User, product: Product):
        """
        Validates whether a product can be purchased by the user.
        Raises a ValidationError if the product or its items have already been purchased.
        """

        # Check if the main product is a one-time purchase
        if product.is_one_time_purchase:
            already_purchased = cls.objects.filter(
                user=user, product=product
            ).exists()
            if already_purchased:
                raise ValidationError("El producto ya ha sido comprado.")

        # Filter one-time purchase items
        one_time_items = product.items.filter(
            category__is_one_time_purchase=True
        )

        # Check if any of the items have already been purchased
        if one_time_items.exists():
            purchased_items = cls.objects.filter(
                user=user, product__in=one_time_items
            )
            if purchased_items.exists():
                raise ValidationError(
                    "Ya has comprado uno de los productos del paquete."
                )
