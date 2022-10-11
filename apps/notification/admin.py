from django.contrib import admin
from notification.models import Notification, NotificationTypes

# Register your models here.

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'notif_type', 'source_id', 'date')

admin.site.register(Notification, NotificationAdmin)
admin.site.register(NotificationTypes)