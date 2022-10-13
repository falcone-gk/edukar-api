from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from forum.models import Post

# Create your models here.

class NotificationTypes(models.Model):

    type_notif = models.CharField(max_length=15, unique=True)
    desc_receiver = models.CharField(max_length=60, unique=True)
    desc_sender = models.CharField(max_length=60, unique=True, null=True, blank=True)

    def __str__(self):
        return self.type_notif

class Notification(models.Model):

    user = models.ForeignKey(User, related_name='notif', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='notif_sent', on_delete=models.CASCADE)
    source_id = models.ForeignKey(Post, related_name='notif_post', on_delete=models.CASCADE)
    notif_type = models.ForeignKey(NotificationTypes, related_name='notif_type', on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):

        format_str = f'{self.sender.username} | {self.notif_type.type_notif} | {self.user}'
        return format_str

    def notification_receiver(self):

        format_str = f'{self.sender.username} {self.notif_type.desc_receiver} en {self.source_id.title}'
        return format_str

    def notification_sender(self):

        format_str = f'{self.notif_type.desc_sender} a {self.user.username} en {self.source_id.title}'
        return format_str