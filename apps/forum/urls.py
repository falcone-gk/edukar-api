from django.urls import path
from rest_framework.routers import DefaultRouter

from forum import views

router = DefaultRouter()
router.register(r'posts', views.CreatePostAPIView, basename='posts')
router.register(r'comments', views.CommentAPIView, basename='comments')
router.register(r'replies', views.ReplyAPIView, basename='replies')

app_name = 'forum'
urlpatterns = [
    path('home-forum/', views.ForumHomeAPIView.as_view(), name='home-forum'),
    path('sections/<slug:slug>/', views.SectionPostAPIView.as_view(), name='sections-post'),
    path('section-list/', views.SectionAPIView.as_view(), name='sections-list'),
    path('post-data/<slug:slug>/', views.GetPostAPIView.as_view(), name='post-data')
]

urlpatterns += router.urls
