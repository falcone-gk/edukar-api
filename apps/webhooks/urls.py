from django.urls import path

from .views import culqi

urlpatterns = [
    # Chat Inbound
    path(
        "culqi/charge-order/",
        culqi.ChangeOrderWebhook.as_view(),
        name="charge-order",
    ),
]
