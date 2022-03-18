from django.urls import path

from forum import views

app_name = 'forum'
urlpatterns = [
    path('posts/create', views.CreatePostAPIView.as_view(), name='create_post'),
]