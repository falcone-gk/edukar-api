from django.db import models

# Create your models here.

class UnivExamsStructure(models.Model):

    university = models.CharField(max_length=255)
    siglas = models.CharField(max_length=25)
    exam_type = models.CharField(max_length=255)
    area = models.CharField(max_length=255, blank=True)

    def __str__(self):

        format_str = '{0}|{1}|{2}'

        return format_str.format(self.siglas, self.exam_type, self.area)

class Exams(models.Model):

    root = models.ForeignKey(UnivExamsStructure, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    cover = models.ImageField(upload_to='cover/')
    year = models.IntegerField()
    source_exam = models.URLField(max_length=200)
    source_video_solution = models.URLField(max_length=200, blank=True)
    source_video_solution_premium = models.URLField(max_length=200, blank=True)

class Course(models.Model):

    name = models.CharField(max_length=60)
    image = models.ImageField(upload_to='course/')
    url = models.URLField(max_length=200)

    def __str__(self):

        return self.name
