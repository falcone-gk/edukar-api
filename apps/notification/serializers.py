from rest_framework import serializers
from notification.models import Notification

class NotificationReceiverSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('notification_receiver', 'date', 'is_read')

class NotificationSenderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('notification_sender', 'date')

class ArrayOfIdsSerializer(serializers.Serializer):

    id_ = serializers.IntegerField(required=False)
    selected_notifications = serializers.ListField(child=serializers.IntegerField())