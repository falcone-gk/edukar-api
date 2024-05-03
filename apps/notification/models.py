from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.utils import timezone
# from forum.models import Post

# Create your models here.

# class NotificationTypes(models.Model):
#
#     type_notif = models.CharField(max_length=15, unique=True)
#     desc_receiver = models.CharField(max_length=60, unique=True)
#     desc_sender = models.CharField(max_length=60, unique=True, null=True, blank=True)
#
#     def __str__(self):
#         return self.type_notif

class Notification(models.Model):

    title = models.CharField(max_length=150, null=False, blank=True)
    description = models.TextField(null=False, blank=True)
    user = models.ForeignKey(User, related_name='notif', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='notif_sent', on_delete=models.CASCADE)
    # source_id = models.ForeignKey(Post, related_name='notif_post', on_delete=models.CASCADE)
    # notif_type = models.ForeignKey(NotificationTypes, related_name='notif_type', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    source_path = models.CharField(max_length=255, null=False, blank=True)

    def __str__(self):

        format_str = f'{self.title} | {self.user}'
        return format_str

    @property
    def full_source_path(self):
        full_source_path = f'http://{settings.DOMAIN}{self.source_path}'
        return full_source_path

    @property
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

    # def notification_receiver(self):
    #
    #     format_str = f'{self.sender.username} {self.notif_type.desc_receiver} en {self.source_id.title}'
    #     return format_str
    #
    # def notification_sender(self):
    #
    #     format_str = f'{self.notif_type.desc_sender} a {self.user.username} en {self.source_id.title}'
    #     return format_str
