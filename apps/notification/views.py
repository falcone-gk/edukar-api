from rest_framework.views import APIView
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist

from forum.paginators import PostCoursePagination
from notification.models import Notification
from notification.serializers import (
    NotificationReceiverSerializer,
    NotificationSenderSerializer,
    ArrayOfIdsSerializer
)
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

    @action(
        detail=False, methods=['post'],
        url_path='set-read', url_name='set_read'
    )
    def mark_as_read(self, request, pk=None):

        serializer = ArrayOfIdsSerializer(data=request.data)
        if serializer.is_valid():

            notif_arr = Notification.objects.filter(
                pk__in=serializer.data['selected_notifications'],
                user=request.user
            )

            if not notif_arr.exists():
                return Response({'status': 'Ninguna de las notificaciones te pertenece.'})

            # Iterate over all notif selected to mark as read.
            for notif in notif_arr:
                notif.is_read = True
                notif.save()

            return Response({'has_notification': request.user.notif.filter(is_read=False).exists()})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

class CheckNotificationAPIView(APIView):

    def post(self, request, format=None):

        try:
            user = Token.objects.get(key=request.data['key']).user
            has_notification = Notification.objects.filter(user=user, is_read=False).exists()
            return Response({'has_notification': has_notification}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'token_error': 'El token no existe'}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return Response({'key': 'Este campo es requerido'}, status=status.HTTP_400_BAD_REQUEST)