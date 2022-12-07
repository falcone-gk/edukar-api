from django.urls import path
from rest_framework.routers import DefaultRouter

from forum import views

router = DefaultRouter()
router.register(r'posts', views.CreatePostAPIView, basename='posts')
router.register(r'comments', views.UnsafeCommentAPIView, basename='comments')
router.register(r'replies', views.UnsafeReplyAPIView, basename='replies')

app_name = 'forum'
urlpatterns = [
    path('sections/', views.ForumHomeAPIView.as_view(), name='sections-list'),
    path('subsection-list/', views.SubsectionAPIView.as_view(), name='subsections-list'),
    path('post-data/<slug:slug>/', views.GetPostAPIView.as_view(), name='post-data')
]

urlpatterns += router.urls
