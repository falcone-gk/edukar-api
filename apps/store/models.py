import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from django_resized import ResizedImageField

from helpers.choices import ProductTypes, SellStatus

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=255)
    is_one_time_purchase = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, null=False, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Attribute(models.Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, null=False, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="attributes"
    )

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class AttributeOption(models.Model):
    attribute = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="options"
    )
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.value} ({self.attribute.name})"


class Product(models.Model):
    def product_upload_to(self, filename):
        ext = filename.split(".")[-1]
        fullname = "{}.{}".format(self.name, ext)
        return f"images/products/{fullname}"

    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, null=False, blank=True)
    description = models.TextField(blank=True, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        related_name="products",
        null=True,
        on_delete=models.SET_NULL,
    )
    type = models.PositiveIntegerField(
        choices=ProductTypes.choices, null=False, default=ProductTypes.PRODUCT
    )
    source = models.URLField(null=False, blank=True)
    product_image = ResizedImageField(
        size=[400, 566],
        quality=50,
        force_format="WebP",
        upload_to=product_upload_to,
        null=True,
    )
    show = models.BooleanField(default=True)
    # TODO: Propiedad a agregar cuando tengamos productos de stock
    # stock = models.PositiveSmallIntegerField(null=True)

    items = models.ManyToManyField("self", blank=True)

    @property
    def is_one_time_purchase(self):
        if self.category:
            return self.category.is_one_time_purchase
        return False

    # TODO: Propiedad a agregar cuando tengamos productos de stock
    # @property
    # def is_available(self):
    #     if not self.is_one_time_purchase and self.stock == 0:
    #         return False
    #     return True

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_attributes"
    )
    attribute_option = models.ForeignKey(
        AttributeOption,
        on_delete=models.CASCADE,
        related_name="product_attributes",
    )

    class Meta:
        unique_together = ("product", "attribute_option")

    def __str__(self):
        return f"{self.product.name} - {self.attribute_option.value} ({self.attribute_option.attribute.name})"


class Sell(models.Model):
    def product_upload_to(self, filename):
        # Get the current timestamp and format it as "YYYYMMDD_HHMMSS"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Extract the file extension from the original filename
        ext = filename.split(".")[-1]
        # Construct the new filename using the desired format
        fullname = f"payment_{timestamp}.{ext}"
        # Return the path to save the file
        return f"images/products/{self.user.username}/{fullname}"

    user = models.ForeignKey(
        User, related_name="sells", on_delete=models.CASCADE
    )
    products = models.ManyToManyField(Product, related_name="sells")
    status = models.IntegerField(
        choices=SellStatus.choices, default=SellStatus.ON_CART
    )
    payment_image = ResizedImageField(
        size=[400, 566],
        quality=50,
        force_format="WebP",
        upload_to=product_upload_to,
        null=True,
    )
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    on_cart_at = models.DateTimeField(null=True)
    on_pending_at = models.DateTimeField(null=True)
    paid_at = models.DateTimeField(null=True)

    @classmethod
    def get_user_cart(cls, user: User):
        return cls.objects.get_or_create(user=user, status=SellStatus.ON_CART)

    def get_total_cost(self) -> Decimal:
        total_cost = Decimal("0.00")
        for product in self.products.all():
            total_cost += product.price

        return total_cost
