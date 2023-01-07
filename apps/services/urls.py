from django.urls import path

from services import views

app_name = 'services'
urlpatterns = [
    path('exams-list/', views.ExamsAPIView.as_view(), name='exams-list'),
]