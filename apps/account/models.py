from django.db import models
from django.contrib.auth.models import User
# from django.core.files.storage import default_storage as storage
from django_resized import ResizedImageField

# from utils.image import image_resize

# Create your models here.

class Profile(models.Model):

    def image_upload(self, filename):
        ext = filename.split('.')[-1]
        fullname = '{}.{}'.format(self.user.username, ext)
        return f'profile/{fullname}'

    user = models.ForeignKey(User, related_name='profile', on_delete=models.CASCADE)
    # picture = models.ImageField(upload_to=image_upload, default='default-avatar.jpg')
    picture = ResizedImageField(
        size=[500, 500], quality=75, force_format="WebP",
        upload_to=image_upload, default='default-avatar.jpg'
    )
    about_me = models.TextField(max_length=255, default='No hay información')

    def __str__(self):
        return self.user.username

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #
    #     if self.picture.name != 'default-avatar.jpg':
    #         img = image_resize(self.picture)
    #         fh = storage.open(self.picture.name, "wb")
    #
    #         img.save(fh, quality=20)
    #         img.close()
    #         # self.picture.close()
    #         fh.close()
