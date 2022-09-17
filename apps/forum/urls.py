from django.urls import path
from rest_framework.routers import DefaultRouter

from forum import views

router = DefaultRouter()
router.register(r'posts', views.CreateUpdatePostAPIView, basename='posts')
router.register(r'comments', views.CreateUpdateCommentAPIView, basename='comments')
router.register(r'replies', views.CreateUpdateReplyAPIView, basename='replies')

app_name = 'forum'
urlpatterns = [
    path('sections/', views.ForumHomeAPIView.as_view(), name='sections-list'),
    path('subsection-list/', views.SubsectionAPIView.as_view(), name='subsections-list'),
]

urlpatterns += router.urls
