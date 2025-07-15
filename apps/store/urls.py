from django.urls import include, path
from rest_framework.routers import DefaultRouter
from store import views

app_name = "store"

router = DefaultRouter()
router.register(r"products", views.ProductViewSet, basename="product")
router.register(r"sells", views.StartSellView, basename="sell")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "cart/check-product",
        views.CheckProductPurchaseView.as_view(),
        name="cart-check-product",
    ),
    path(
        "category/filters",
        views.CategoryFiltersAPIView.as_view(),
        name="category-filters",
    ),
    # path("payment", views.UserProductBulkCreateView.as_view(), name="payment"),
    path(
        "invoice/send/<int:sell_id>/",
        views.InvoiceSendAPIView.as_view(),
        name="send_invoice_email",
    ),
    path(
        "document/download/<slug:slug>",
        views.DownloadProductDocumentView.as_view(),
        name="download-document",
    ),
    path(
        "lreclamaciones", views.ClaimCreateView.as_view(), name="lreclamaciones"
    ),
    path("invoice/<int:sell_id>/", views.view_invoice, name="view_invoice"),
]
