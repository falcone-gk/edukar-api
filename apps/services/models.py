from django.core.exceptions import ValidationError
from django.db import models
from django_resized import ResizedImageField

# Create your models here.


# class UnivExamsStructure(models.Model):
#     university = models.CharField(max_length=255)
#     siglas = models.CharField(max_length=25)
#     exam_type = models.CharField(max_length=255)
#     area = models.CharField(max_length=255, blank=True)

#     def __str__(self):
#         format_str = "{0}|{1}|{2}"
#         return format_str.format(self.siglas, self.exam_type, self.area)


class University(models.Model):
    name = models.CharField(max_length=255)
    siglas = models.CharField(max_length=25)
    exam_types = models.JSONField(null=False, default=list)
    exam_areas = models.JSONField(null=False, default=list)

    def __str__(self):
        return self.name


class Exams(models.Model):
    # root = models.ForeignKey(
    #     UnivExamsStructure, null=True, on_delete=models.SET_NULL
    # )
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
