from django.contrib import admin
from notification.models import Notification

# Register your models here.

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'date', 'title', 'description', 'is_read')

admin.site.register(Notification, NotificationAdmin)
