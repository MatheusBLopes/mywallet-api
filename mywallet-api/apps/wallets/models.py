from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.wallets.utils import generate_wallet_code


class Wallet(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(editable=False, max_length=16, unique=True, default=generate_wallet_code)


class Year(models.Model):
    name = models.CharField(max_length=255)
    wallet = models.ForeignKey(Wallet, related_name="years", on_delete=models.CASCADE)


class Month(models.Model):
    month = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.ForeignKey(Year, related_name="months", on_delete=models.CASCADE)


class DebitRecord(models.Model):
    name = models.CharField(max_length=255)
    purchase_date = models.DateField()
    receiver = models.CharField(max_length=400)
    comments = models.CharField(max_length=500, blank=True)
    price = models.FloatField()

    recurrences = models.PositiveIntegerField(default=1)

    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name="debit_records")


class CreditRecord(models.Model):
    name = models.CharField(max_length=255)
    purchase_date = models.DateField()
    receiver = models.CharField(max_length=400)
    comments = models.CharField(max_length=500, blank=True)
    number_of_installments = models.PositiveIntegerField(default=1)
    installment = models.PositiveIntegerField(default=1)
    total_price = models.FloatField()
    installment_value = models.FloatField(default=0)

    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name="credit_records")


class DepositRecord(models.Model):
    name = models.CharField(max_length=255)
    receipt_date = models.DateField()

    payer = models.CharField(max_length=400)
    comments = models.CharField(max_length=500, blank=True)
    value = models.FloatField()

    recurrences = models.PositiveIntegerField(default=1)

    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name="deposit_records")
