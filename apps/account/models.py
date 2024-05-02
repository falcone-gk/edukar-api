from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage as storage
from uuid import uuid4

from utils.image import image_resize

# Create your models here.

class Profile(models.Model):

    def image_upload(self, filename):
        ext = filename.split('.')[-1]
        fullname = '{}.{}'.format(self.user.username, ext)
        return f'profile/{fullname}'

    user = models.ForeignKey(User, related_name='profile', on_delete=models.CASCADE)
    picture = models.ImageField(upload_to=image_upload, default='default-avatar.jpg')
    about_me = models.TextField(max_length=255, default='No hay información')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.picture.name != 'default-avatar.jpg':
            img = image_resize(self.picture)
            fh = storage.open(self.picture.name, "wb")

            img.save(fh, quality=20)
            img.close()
            self.picture.close()
            fh.close()

class UserImage(models.Model):

    def image_upload(self, filename):
        ext = filename.split('.')[-1]
        new_filename = uuid4().hex
        fullname = '{}.{}'.format(new_filename, ext)
        return f'images/{self.module}/{self.author.id}/{fullname}'

    author = models.ForeignKey(User, related_name='images_upload', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload)
    created_at = models.DateField(auto_now_add=True)
    module = models.CharField(null=False, blank=False, max_length=50)
    is_used = models.BooleanField(default=False, null=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = image_resize(self.image)
        fh = storage.open(self.image.name, "wb")

        img.save(fh, quality=50)
        img.close()
        self.image.close()
        fh.close()
