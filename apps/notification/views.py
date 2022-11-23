from django.shortcuts import render
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from forum.paginators import PostCoursePagination
from notification.models import Notification
from notification.serializers import NotificationReceiverSerializer, NotificationSenderSerializer
from notification.permissions import isOwnNotification

# Create your views here.

class NotificationReceivedAPIView(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):

    serializer_class = NotificationReceiverSerializer
    permission_classes = (IsAuthenticated, isOwnNotification)
    pagination_class = PostCoursePagination

    def get_queryset(self):

        current_user = self.request.user
        return Notification.objects.filter(user=current_user).order_by('-date')

class NotificationSentAPIView(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet):

    serializer_class = NotificationSenderSerializer
    permission_classes = (IsAuthenticated, isOwnNotification)
    pagination_class = PostCoursePagination

    def get_queryset(self):

        current_user = self.request.user
        return Notification.objects.filter(user=current_user).order_by('-date')

    @action(detail=True, methods=['post'])
    def set_as_read(self, request, pk=None):

        notif_ids = request.data
        notif_arr = Notification.objects.filter(pk__in=notif_ids)

        for notif in notif_arr:
            notif.is_read = True
            notif.save()
            return Response({'status': 'Notificaciones marcadas como leídas.'})