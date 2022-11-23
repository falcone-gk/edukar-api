from django.urls import path
from rest_framework.routers import DefaultRouter

from notification import views

router = DefaultRouter()
router.register(r'notification-user', views.NotificationReceivedAPIView, basename='notification-user')

app_name = 'notification'
urlpatterns = [
]

urlpatterns += router.urls