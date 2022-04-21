from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):

    user = models.ForeignKey(User, related_name='profile', on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='profile/', default='default-avatar.jpg')
    about_me = models.TextField(max_length=255, default='No hay información')

    def __str__(self):
        return self.user.username
