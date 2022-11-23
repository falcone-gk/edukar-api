from django.shortcuts import render
from rest_framework import status, viewsets, mixins
from rest_framework.permissions import IsAuthenticated

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
    viewsets.GenericViewSet):

    serializer_class = NotificationSenderSerializer
    permission_classes = (IsAuthenticated, isOwnNotification)
    pagination_class = PostCoursePagination

    def get_queryset(self):

        current_user = self.request.user
        return Notification.objects.filter(user=current_user).order_by('-date')