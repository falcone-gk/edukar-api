from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from account import views

app_name = 'account'
urlpatterns = [
    path('create', views.CreateUserAPIView.as_view(), name='create_account'),
    path('login', obtain_auth_token, name='login')
]