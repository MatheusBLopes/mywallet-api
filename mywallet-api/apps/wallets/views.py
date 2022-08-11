from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.wallets.models import Record, Wallet
from apps.wallets.serializers import RecordsSerializer, WalletSerializer


class WalletViewSet(viewsets.ModelViewSet):
    lookup_field = "code"
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer


class RecordsView(APIView):
    def post(self, request):
        serializer = RecordsSerializer(data={**request.data})
        serializer.validate(request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, record_code):
        delete_all = request.data.get("delete_all", None)
        delete_one = request.data.get("delete_one", None)
        delete_onwards = request.data.get("delete_onwards", None)

        deletes_list = [delete_all, delete_one, delete_onwards]

        if deletes_list.count(True) > 1:
            return Response(
                data={"details": "Only one delete operation can be performed at a time"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        main_record = get_object_or_404(Record, code=record_code)

        if delete_one:
            main_record.delete()

        if delete_all:
            group_code = main_record.group_code
            records_to_delete = Record.objects.filter(group_code=group_code)
            records_to_delete.delete()

        if delete_onwards:
            group_code = main_record.group_code
            records_to_delete = Record.objects.filter(group_code=group_code)

            for record in records_to_delete:
                if record.installment >= main_record.installment:
                    record.delete()

        return Response(status=status.HTTP_200_OK)
