from rest_framework import serializers
from notification.models import Notification

class NotificationReceiverSerializer(serializers.ModelSerializer):

    author = serializers.CharField(source='sender.username')
    title = serializers.CharField(source='source_id.title')
    title_slug = serializers.CharField(source='source_id.slug')
    description = serializers.CharField(source='notif_type.desc_receiver')
    date = serializers.DateTimeField(format="%d de %B del %Y, a las %H:%M", read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'author', 'date', 'description', 'title', 'title_slug', 'is_read')

class NotificationSenderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('notification_sender', 'date')

class ArrayOfIdsSerializer(serializers.Serializer):

    id_ = serializers.IntegerField(required=False)
    selected_notifications = serializers.ListField(child=serializers.IntegerField())