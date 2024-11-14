from django.urls import path

from services import views

app_name = "services"
urlpatterns = [
    path("exams/", views.ExamsAPIView.as_view(), name="exams-list"),
    path(
        "exams/<slug:slug>/",
        views.RetrieveExamsAPIView.as_view(),
        name="exam-retrieve",
    ),
    path(
        "exams/download/<slug:slug>/",
        views.DownloadExamAPIView.as_view(),
        name="exam-download",
    ),
    path(
        "exams-filters/",
        views.GetExamsFilterAPIView.as_view(),
        name="exams-filters",
    ),
    path("courses/", views.CoursesAPIView.as_view(), name="courses-list"),
]
