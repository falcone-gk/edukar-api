from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.

class BaseContentPublication(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
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
    subsection = models.ForeignKey(Subsection, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)

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