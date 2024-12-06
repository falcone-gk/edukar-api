from dashboard import views
from django.urls import path

app_name = "dashboard"
urlpatterns = [
    path("", views.DashboardAPIView.as_view(), name="dashboard-info"),
]
