from datetime import datetime, timedelta
from rest_framework import serializers

from apps.wallets.models import CreditRecord, DebitRecord, DepositRecord, Wallet, Year, Month


def get_months_to_create(record, wallet_code, installments):
    dates = []

    months_to_create = []

    purchase_date = record.get("purchase_date", None)

    dates.append(purchase_date)
    for _ in range(1, installments):
        purchase_date = purchase_date + timedelta(days=30)
        dates.append(purchase_date)

    for date in dates:
        year = Year.objects.filter(wallet__code=wallet_code).filter(name=date.year).first()
        month = Month.objects.filter(year_id=year.id).filter(month=date.month).first()

        months_to_create.append(month)

    return months_to_create


class CreditRecordsSerializer(serializers.ModelSerializer):
    wallet_code = serializers.CharField(write_only=True)

    class Meta:
        model = CreditRecord
        fields = [
            "id",
            "name",
            "purchase_date",
            "receiver",
            "comments",
            "total_price",
            "wallet_code",
            "number_of_installments",
            "installment",
            "installment_value",
        ]
        extra_kwargs = {"installment_value": {"read_only": True}}

    def create(self, validated_data):
        number_of_installments = validated_data.get("number_of_installments", None)

        months_to_create = get_months_to_create(
            validated_data, validated_data.pop("wallet_code"), number_of_installments
        )

        installment_price = validated_data["total_price"] / number_of_installments

        validated_data["installment_value"] = installment_price

        validated_data["installment"] = 1

        for month in months_to_create:
            new_credit_record = CreditRecord.objects.create(month=month, **validated_data)
            validated_data["installment"] += 1

        return new_credit_record


class DebitRecordsSerializer(serializers.ModelSerializer):
    wallet_code = serializers.CharField(write_only=True)

    class Meta:
        model = DebitRecord
        fields = [
            "id",
            "name",
            "purchase_date",
            "receiver",
            "comments",
            "price",
            "wallet_code",
            "recurrences",
        ]

    def create(self, validated_data):
        months_to_create = get_months_to_create(
            validated_data, validated_data.pop("wallet_code"), validated_data.get("recurrences", None)
        )

        for month in months_to_create:
            new_credit_record = DebitRecord.objects.create(month=month, **validated_data)

        return new_credit_record


class DepositRecordsSerializer(serializers.ModelSerializer):
    wallet_code = serializers.CharField(write_only=True)

    class Meta:
        model = DepositRecord
        fields = [
            "id",
            "name",
            "receipt_date",
            "payer",
            "comments",
            "value",
            "wallet_code",
            "recurrences",
        ]

    def create(self, validated_data):
        months_to_create = get_months_to_create(
            validated_data, validated_data.pop("wallet_code"), validated_data.get("recurrences", None)
        )

        for month in months_to_create:
            new_credit_record = DepositRecord.objects.create(month=month, **validated_data)

        return new_credit_record


class MonthSerializer(serializers.ModelSerializer):
    credit_records = CreditRecordsSerializer(many=True, required=False)
    debit_records = DebitRecordsSerializer(many=True, required=False)

    class Meta:
        model = Month
        fields = ["id", "month", "credit_records", "debit_records"]


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
