from rest_framework import serializers
from notification.models import Notification

class NotificationSerializer(serializers.ModelSerializer):

    sender = serializers.CharField(source='sender.username')
    # title = serializers.CharField(source='source_id.title')
    # title_slug = serializers.CharField(source='source_id.slug')
    # description = serializers.CharField(source='notif_type.desc_receiver')
    # date = serializers.DateTimeField(format="%d de %B del %Y, a las %H:%M", read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'sender', 'date',
            'title', 'description', 'is_read',
            'source_path', 'full_source_path', 'time_difference'
        )

# class NotificationSenderSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Notification
#         fields = ('notification_sender', 'date')

class ArrayOfIdsSerializer(serializers.Serializer):

    # id_ = serializers.IntegerField(required=False)
    selected_notifications = serializers.ListField(child=serializers.IntegerField())
