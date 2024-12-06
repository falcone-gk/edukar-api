from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from services.models import Exams

# Create your models here.


class DownloadExams(models.Model):
    exam = models.ForeignKey(Exams, null=False, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    download_successful = models.BooleanField(default=True)
