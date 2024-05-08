from django.contrib.auth.models import User
from django.core.files.storage import default_storage as storage
from django.db import models
from django.utils import timezone
from uuid import uuid4
from utils.image import image_resize

# Create your models here.

class BaseContentPublication(models.Model):

    def image_upload(self, filename):
        ext = filename.split('.')[-1]
        new_filename = uuid4().hex
        fullname = '{}.{}'.format(new_filename, ext)
        return f'images/{self.author.id}/{fullname}'

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # TODO: Add custom validation to handle body and image content
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to=image_upload, null=True)
    date = models.DateTimeField(default=timezone.now)

    def time_difference(self):
        
        difference = timezone.now() - self.date
        seconds = difference.total_seconds()

        if seconds / 60 < .5:
            time_difference = 'Justo ahora'
        elif seconds // 60 < 2:
            value = int(seconds // 60)
            time_difference = 'Hace {} minuto'.format(value)
        elif seconds // 60 < 59:
            value = int(seconds // 60)
            time_difference = 'Hace {} minutos'.format(value)
        elif seconds // (60 * 60) < 2:
            value = int(seconds // (60 * 60))
            time_difference = 'Hace {} hora'.format(value)
        elif seconds // (60 * 60) < 24:
            value = int(seconds // (60 * 60))
            time_difference = 'Hace {} horas'.format(value)
        else:
            time_difference = self.date.strftime("%d-%m-%Y")

        return time_difference

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = image_resize(self.image)
            fh = storage.open(self.image.name, "wb")

            img.save(fh, quality=50)
            img.close()
            self.image.close()
            fh.close()

    class Meta:
        abstract = True

class Section(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, null=True, blank=True, unique=True)

    def __str__(self):

        return self.name

class Subsection(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='subsection')
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, null=True, blank=True, unique=True)

    def __str__(self):

        return self.name

class Post(BaseContentPublication):

    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='posts')
    subsection = models.ForeignKey(Subsection, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)
    participants = models.ManyToManyField(User, related_name='participants')

    def __str__(self):

        return self.title

class Comment(BaseContentPublication):

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):

        if len(self.body) > 100:
            return self.body[:100] + '...'

        return self.body

class Reply(BaseContentPublication):

    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):

        if len(self.body) > 100:
            return self.body[:100] + '...'

        return self.body
