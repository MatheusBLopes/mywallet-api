from django.urls import include, path
from rest_framework import routers

from apps.wallets.views import (
    DebitRecordsViewSet,
    WalletViewSet,
    CreditRecordsViewSet

)

app_name = "wallets"

router = routers.DefaultRouter()
router.register("wallets", WalletViewSet, basename="Wallets")


urlpatterns = [
    path("", include(router.urls)),
    path("wallets/<str:wallet_code>/credit-record", CreditRecordsViewSet.as_view(), name="wallet_credit_record"),
    path("wallets/<str:wallet_code>/debit-record", DebitRecordsViewSet.as_view(), name="wallet_debit_record")
]
