from datetime import datetime, timedelta

from rest_framework import serializers

from apps.wallets.models import Month, Record, Wallet, Year
from apps.wallets.utils import generate_record_code, generate_record_group_code


def get_months_to_create(wallet_code, installments, operation_date):
    dates = []

    months_to_create = []

    dates.append(operation_date)
    for _ in range(1, installments):
        operation_date = operation_date + timedelta(days=30)
        dates.append(operation_date)

    for date in dates:
        year = Year.objects.filter(wallet__code=wallet_code).filter(name=date.year).first()
        month = Month.objects.filter(year_id=year.id).filter(month=date.month).first()

        months_to_create.append(month)

    return months_to_create


class RecordsSerializer(serializers.ModelSerializer):
    wallet_code = serializers.CharField(write_only=True)

    class Meta:
        model = Record
        fields = [
            "id",
            "name",
            "date",
            "comments",
            "value",
            "payer_or_receiver",
            "code",
            "group_code",
            "installment",
            "quantity_of_installments",
            "record_type",
            "wallet_code",
        ]

    def create(self, validated_data):
        record_type = validated_data.get("record_type", None)

        months_to_create = get_months_to_create(
            validated_data.pop("wallet_code"),
            validated_data.get("quantity_of_installments", None),
            validated_data.get("date", None),
        )

        validated_data["code"] = generate_record_code()

        if record_type == "credit_record":
            validated_data["value"] = validated_data["value"] / validated_data["quantity_of_installments"]

        validated_data["installment"] = 1

        if len(months_to_create) > 1:
            validated_data["group_code"] = generate_record_group_code()
        else:
            validated_data["group_code"] = validated_data["code"]

        for month in months_to_create:
            new_record = Record.objects.create(month=month, **validated_data)
            validated_data["installment"] += 1
            validated_data["code"] = generate_record_code()

        return new_record


class MonthSerializer(serializers.ModelSerializer):
    records = RecordsSerializer(many=True, required=False)

    class Meta:
        model = Month
        fields = ["id", "month", "records"]


class YearSerializer(serializers.ModelSerializer):
    months = MonthSerializer(many=True, required=False)

    class Meta:
        model = Year
        fields = ["id", "name", "months", "wallet"]

    def create(self, validated_data):
        new_year = Year.objects.create(name=validated_data["name"], wallet=validated_data["wallet"])

        for month in range(1, 13):
            Month.objects.create(month=month, year=new_year)

        return new_year


class WalletSerializer(serializers.ModelSerializer):
    years = YearSerializer(many=True, required=False)

    class Meta:
        model = Wallet
        fields = ["id", "name", "years", "code"]

    def create(self, validated_data):
        new_wallet = Wallet.objects.create(**validated_data)

        years_to_create = [
            str(int(datetime.now().strftime("%Y")) - 1),
            datetime.now().strftime("%Y"),
            str(int(datetime.now().strftime("%Y")) + 1),
        ]

        for year in years_to_create:
            year_serializer = YearSerializer(data={"name": year, "wallet": new_wallet.id})
            year_serializer.is_valid()
            year_serializer.save()

        return new_wallet
