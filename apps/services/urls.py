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
        "exams/upload",
        views.UploadExamAPIView.as_view(),
        name="exam-upload",
    ),
    path(
        "exams-filters/",
        views.GetExamsFilterAPIView.as_view(),
        name="exams-filters",
    ),
    path(
        "cart/add-item",
        views.AddItemCartView.as_view(),
        name="add-item-cart",
    ),
    path(
        "cart/remove-item",
        views.RemoveItemCartAPIView.as_view(),
        name="remove-item-cart",
    ),
    path(
        "user-products/",
        views.UserProductBulkCreateView.as_view(),
        name="user-products-bulk-create",
    ),
    path("courses/", views.CoursesAPIView.as_view(), name="courses-list"),
]
