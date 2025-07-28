import os

from django.core.exceptions import ValidationError
from django.db import models
from django_resized import ResizedImageField
from store.models import Product

# Create your models here.


class University(models.Model):
    name = models.CharField(max_length=255)
    siglas = models.CharField(max_length=25)
    exam_types = models.JSONField(null=False, default=list)
    exam_areas = models.JSONField(null=False, blank=True, default=list)

    def __str__(self):
        return self.name


class Exams(models.Model):
    def upload_cover(self, filename):
        _, ext = os.path.splitext(filename)
        slug = self.slug
        return f"cover/{slug}{ext}"

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
        upload_to=upload_cover,
        null=True,
    )
    year = models.IntegerField()
    slug = models.SlugField(
        max_length=125, null=False, blank=False, unique=True
    )
    source_exam = models.CharField(max_length=200)
    source_video_solution = models.URLField(max_length=200, blank=True)
    source_video_solution_premium = models.URLField(max_length=200, blank=True)

    # Este campo es para vincular el examen con el producto de tipo Video.
    source_video_product = models.ForeignKey(
        Product,
        related_name="exams",
        null=True,
        blank=True,
        help_text="Producto de tipo Video",
        on_delete=models.SET_NULL,
    )

    is_delete = models.BooleanField(null=False, default=False)
    # products = models.ManyToManyField(Product, related_name="exams", blank=True)

    def clean(self):
        """Validate exam type and area before saving."""
        if self.university:
            if self.type not in self.university.exam_types:
                raise ValidationError(
                    {
                        "type": f"The type '{self.type}' is not valid for the university '{self.university.name}'. "
                        f"Allowed types: {', '.join(self.university.exam_types)}."
                    }
                )
            if self.area and self.area not in self.university.exam_areas:
                raise ValidationError(
                    {
                        "area": f"The area '{self.area}' is not valid for the university '{self.university.name}'. "
                        f"Allowed areas: {', '.join(self.university.exam_areas)}."
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


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
