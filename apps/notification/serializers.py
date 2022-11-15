from rest_framework import serializers
from notification.models import Notification

class NotificationReceiverSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('notification_receiver', 'notification_sender', 'date', 'is_read')