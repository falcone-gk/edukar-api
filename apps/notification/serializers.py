from rest_framework import serializers
from notification.models import Notification

class NotificationReceiverSerializer(serializers.ModelSerializer):

    class Metas:
        model = Notification
        fields = ('notification_receiver', 'date', 'is_read')