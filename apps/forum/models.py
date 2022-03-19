from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.

class BaseContentPublication(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, default=None, blank=True, related_name='liked_content')

    def get_time_difference(self):
        
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

class Post(BaseContentPublication):

    SECTION_CHOICES = [
        ('Cursos', (
                ('aritmetica', 'Aritmética'),
                ('rm', 'Razonamiento Matemático'),
                ('quimica', 'Química')
            ),
        ),
        ('articulos-y-noticias', 'Artículos y Noticias')
    ]

    section = models.CharField(choices=SECTION_CHOICES, max_length=30)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, null=True, blank=True, unique=True)

    def __str__(self):

        return self.slug