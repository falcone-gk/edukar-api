from django.urls import path
from rest_framework.routers import DefaultRouter

from forum import views

router = DefaultRouter()
router.register(r'posts', views.CreateUpdatePostAPIView, basename='posts')

app_name = 'forum'
urlpatterns = [
    path('sections/', views.ForumHomeAPIView.as_view(), name='sections-list'),
]

urlpatterns += router.urls
