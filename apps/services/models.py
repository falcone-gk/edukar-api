import datetime
import uuid
from decimal import Decimal

from core.models import StatusModel, TimeStampModel
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django_resized import ResizedImageField

from helpers.choices import ProductTypes, SellStatus

# Create your models here.


class BaseProduct(TimeStampModel, StatusModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True


class Product(BaseProduct):
    def product_upload_to(self, filename):
        ext = filename.splut(".")[-1]
        fullname = "{}.{}".format(self.name, ext)
        return f"images/products/{fullname}"

    type = models.PositiveIntegerField(
        choices=ProductTypes.choices, null=False, default=ProductTypes.DOCUMENT
    )
    source = models.URLField(null=False, blank=True)
    product_image = ResizedImageField(
        size=[400, 566],
        quality=50,
        force_format="WebP",
        upload_to=product_upload_to,
        null=True,
    )

    @property
    def is_one_time_purchase(self):
        if (self.type == ProductTypes.DOCUMENT) or (
            self.type == ProductTypes.DOCUMENT
        ):
            return True
        return False

    def __str__(self):
        return self.name


class Package(BaseProduct):
    products = models.ManyToManyField(Product, related_name="packages")

    def __str__(self):
        return self.name


class University(models.Model):
    name = models.CharField(max_length=255)
    siglas = models.CharField(max_length=25)
    exam_types = models.JSONField(null=False, default=list)
    exam_areas = models.JSONField(null=False, default=list)

    def __str__(self):
        return self.name


class Exams(models.Model):
    university = models.ForeignKey(
        University, null=True, on_delete=models.SET_NULL
    )
    type = models.CharField(max_length=255, null=False, blank=True)
    area = models.CharField(max_length=255, null=False, blank=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    cover = ResizedImageField(
        size=[400, 566],
        quality=50,
        force_format="WebP",
        upload_to="cover/",
        null=True,
    )
    year = models.IntegerField()
    slug = models.SlugField(
        max_length=125, null=False, blank=False, unique=True
    )
    source_exam = models.CharField(max_length=200)
    source_video_solution = models.URLField(max_length=200, blank=True)
    source_video_solution_premium = models.URLField(max_length=200, blank=True)
    is_delete = models.BooleanField(null=False, default=False)

    products = models.ManyToManyField(Product, related_name="exams")
    packages = models.ManyToManyField(Package, related_name="exams")

    def save(self, *args, **kwargs):
        # Perform validation
        if self.university:
            if self.type not in self.university.exam_types:
                raise ValidationError(
                    f"The type '{self.type}' is not valid for the university '{self.university.name}'. "
                    f"Allowed types are: {', '.join(self.university.exam_types)}."
                )
            if (self.area) and (self.area not in self.university.exam_areas):
                raise ValidationError(
                    f"The area '{self.area}' is not valid for the university '{self.university.name}'. "
                    f"Allowed areas are: {', '.join(self.university.exam_areas)}."
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


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
    packages = models.ManyToManyField(Package, related_name="sells")
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

    def update_total_cost(self):
        total_cost = Decimal("0.00")
        for product in self.products.all():
            total_cost += product.price
        for package in self.packages.all():
            total_cost += package.price

        self.total_cost = total_cost


class Course(models.Model):
    name = models.CharField(max_length=60)
    image = ResizedImageField(
        size=[400, 566],
        quality=50,
        force_format="WebP",
        upload_to="course/",
        null=True,
    )
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.name
