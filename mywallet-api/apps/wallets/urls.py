from django.urls import include, path
from rest_framework import routers

from apps.wallets.views import RecordsView, WalletViewSet

app_name = "wallets"

router = routers.DefaultRouter()
router.register("wallets", WalletViewSet, basename="Wallets")


urlpatterns = [
    path("", include(router.urls)),
    path("records/", RecordsView.as_view(), name="records"),
    path("records/<str:record_code>", RecordsView.as_view(), name="delete_records"),
]
