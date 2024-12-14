from django.urls import include, path
from rest_framework.routers import DefaultRouter
from store import views

app_name = "store"

router = DefaultRouter()
router.register(r"products", views.ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "cart/add-item", views.AddItemCartView.as_view(), name="add-item-cart"
    ),
    path(
        "cart/remove-item",
        views.RemoveItemCartAPIView.as_view(),
        name="remove-item-cart",
    ),
    path(
        "category/filters",
        views.CategoryFiltersAPIView.as_view(),
        name="category-filters",
    ),
]
