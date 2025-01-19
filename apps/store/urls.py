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
        "cart/check-product",
        views.CheckProductPurchaseView.as_view(),
        name="cart-check-product",
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
    path("payment", views.UserProductBulkCreateView.as_view(), name="payment"),
    path(
        "document/download/<slug:slug>",
        views.DownloadProductDocumentView.as_view(),
        name="download-document",
    ),
    path(
        "lreclamaciones", views.ClaimCreateView.as_view(), name="lreclamaciones"
    ),
]
