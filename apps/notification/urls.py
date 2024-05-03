from django.urls import path
from rest_framework.routers import DefaultRouter

from notification import views

router = DefaultRouter()
router.register(r'notification-user', views.NotificationAPIView, basename='notification-user')

app_name = 'notification'
urlpatterns = [
    path('check-notification/', views.CheckNotificationAPIView.as_view(), name='check-notification'),
]

urlpatterns += router.urls
