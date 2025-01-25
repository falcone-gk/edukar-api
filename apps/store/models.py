import datetime
import locale
import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django_resized import ResizedImageField

from helpers.choices import ProductTypes, SellStatus, TypeGoods

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

    @classmethod
    def get_solutionary_category(cls):
        return cls.objects.get(name="Solucionario")


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
        choices=ProductTypes.choices, null=False, default=ProductTypes.DOCUMENT
    )
    source = models.CharField(max_length=255, null=False, blank=True)
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
    identifier = models.CharField(
        max_length=12, unique=True, editable=False, null=True, blank=True
    )

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

    def generate_identifier(self):
        """Generate a unique identifier."""
        return uuid.uuid4().hex[:12].upper()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        if not self.identifier:
            self.identifier = self.generate_identifier()

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


class VideoPart(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="video_parts",
        on_delete=models.CASCADE,
        limit_choices_to={"type": ProductTypes.VIDEO},
    )
    slug = models.CharField(max_length=255, null=False, blank=True, unique=True)
    url = models.CharField(max_length=255)
    part_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["part_number"]
        unique_together = ("product", "part_number")

    def __str__(self):
        return f"Part {self.part_number} of {self.product.name}"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


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

    def receipt_upload_to(self, filename):
        # Get the current timestamp and format it as "YYYYMMDD_HHMMSS"
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        # Construct the new filename using the desired format
        fullname = f"receipt_{timestamp}.pdf"
        # Return the path to save the file
        return f"receipts/{self.user.username}/{fullname}"

    user = models.ForeignKey(
        User, related_name="sells", on_delete=models.CASCADE
    )
    products = models.ManyToManyField(Product, related_name="sells")
    # This field is not necessary? ¿Deberia usar este campo cuando el usuario
    # agrega elementos a su carrito?
    status = models.IntegerField(
        choices=SellStatus.choices, default=SellStatus.ON_CART
    )
    receipt = models.FileField(upload_to=receipt_upload_to, null=True)
    # Este campo debe ser eliminado ya que usaremos pasarela
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

    @property
    def to_receipt_json(self):
        # Set locale to Spanish for date formatting
        try:
            locale.setlocale(
                locale.LC_TIME, "es_ES.UTF-8"
            )  # For Unix/Linux systems
        except locale.Error:
            locale.setlocale(
                locale.LC_TIME, "es_ES"
            )  # Fallback for some systems

        # Format the date
        formatted_date = self.paid_at.strftime("%d de %B de %Y")

        # Generate the product list
        product_list = [
            {
                "id": product.id,
                "name": product.name,
                "quantity": 1,  # Assuming each product is added once; adjust as necessary
                "price": product.price,
                "total": product.price,
            }
            for product in self.products.all()
        ]

        # Construct the JSON response
        receipt = {
            "company_name": "Edukar",
            "receipt_number": f"EDK-{timezone.now().year}-{str(self.id).zfill(8)}",
            "customer": {
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "email": self.user.email,
            },
            "products": product_list,
            "total": self.total_cost,
            "date": formatted_date,
        }

        return receipt


class Claim(models.Model):
    def claim_upload_to(self, filename):
        # Get the current timestamp and format it as "YYYYMMDD_HHMMSS"
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        # Construct the new filename using the desired format
        fullname = f"claim_{timestamp}.pdf"
        # Return the path to save the file
        return f"claims/{fullname}"

    # General Information
    date = models.DateField(auto_now_add=True)

    # Consumer Information
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    dni = models.CharField(max_length=20)  # DNI/CE
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=50)
    is_minor = models.BooleanField(default=False)

    # Proxy Information (for minors)
    proxy_name = models.CharField(max_length=100, blank=True, null=True)

    # Contracted Good
    type_good = models.IntegerField(choices=TypeGoods.choices, null=False)
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)

    # Claim Details
    claim_detail = models.TextField()
    request = models.TextField()

    claim_file = models.FileField(upload_to=claim_upload_to, null=True)

    def __str__(self):
        return f"Claim {self.id} by {self.name}"

    @property
    def form_data(self):
        """Transform the model data to fit the template."""
        try:
            locale.setlocale(
                locale.LC_TIME, "es_ES.UTF-8"
            )  # For Unix/Linux systems
        except locale.Error:
            locale.setlocale(
                locale.LC_TIME, "es_ES"
            )  # Fallback for some systems

        # Get the date components
        day = self.date.day
        month = self.date.strftime("%B")  # Full month name
        year = self.date.year

        return {
            "claim_number": f"{str(self.id).zfill(8)}-{timezone.now().year}",
            "day": day,
            "month": month,
            "year": year,
            "name": self.name,
            "address": self.address,
            "dni": self.dni,
            "email": self.email,
            "phone": self.phone,
            "is_minor": self.is_minor,
            "proxy_name": self.proxy_name if self.is_minor else "",
            "product": self.type_good == TypeGoods.PRODUCT,
            "service": self.type_good == TypeGoods.SERVICE,
            "claim_amount": f"{self.claim_amount:.2f}",
            "description": self.description,
            "claim_detail": self.claim_detail,
            "request": self.request,
        }
