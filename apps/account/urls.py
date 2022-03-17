from django.urls import path
from account import views

app_name = 'account'
urlpatterns = [
    path('create', views.CreateUserAPIView.as_view(), name='create_account')
]