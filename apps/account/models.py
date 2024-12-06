from django.contrib.auth.models import User
from django.db import models
from django_resized import ResizedImageField
from services.models import Product

# Create your models here.


class Profile(models.Model):
    def image_upload(self, filename):
        ext = filename.split(".")[-1]
        fullname = "{}.{}".format(self.user.username, ext)
        return f"profile/{fullname}"

    user = models.ForeignKey(
        User, related_name="profile", on_delete=models.CASCADE
    )
    picture = ResizedImageField(
        size=[500, 500],
        quality=75,
        force_format="WebP",
        upload_to=image_upload,
        default="default-avatar.jpg",
    )
    about_me = models.TextField(max_length=255, default="No hay información")

    def __str__(self):
        return self.user.username


class UserProduct(models.Model):
    user = models.ForeignKey(
        User, related_name="products", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="users", on_delete=models.CASCADE
    )
    date = models.DateField(null=False, auto_now_add=True)
