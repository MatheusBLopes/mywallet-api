from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.wallets.models import Wallet
from apps.wallets.serializers import (
    CreditRecordsSerializer,
    DebitRecordsSerializer,
    DepositRecordsSerializer,
    WalletSerializer,
)


class WalletViewSet(viewsets.ModelViewSet):
    lookup_field = "code"
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class CreditRecordsViewSet(APIView):
    def post(self, request, wallet_code):
        serializer = CreditRecordsSerializer(data={**request.data, "wallet_code": wallet_code})
        serializer.validate(request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DebitRecordsViewSet(APIView):
    def post(self, request, wallet_code):
        serializer = DebitRecordsSerializer(data={**request.data, "wallet_code": wallet_code})
        serializer.validate(request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DepositRecordsViewSet(APIView):
    def post(self, request, wallet_code):
        serializer = DepositRecordsSerializer(data={**request.data, "wallet_code": wallet_code})
        serializer.validate(request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
