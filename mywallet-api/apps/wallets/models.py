from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.wallets.utils import generate_wallet_code

RECORD_CHOICES = (
    ("debit", "debit"),
    ("credit", "credit"),
    ("deposit", "deposit"),
)


class Wallet(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(editable=False, max_length=16, unique=True, default=generate_wallet_code)


class Year(models.Model):
    name = models.CharField(max_length=255)
    wallet = models.ForeignKey(Wallet, related_name="years", on_delete=models.CASCADE)


class Month(models.Model):
    month = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.ForeignKey(Year, related_name="months", on_delete=models.CASCADE)


class Record(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    comments = models.CharField(max_length=500, blank=True)

    value = models.FloatField()

    payer_or_receiver = models.CharField(max_length=400)

    code = models.CharField(editable=False, max_length=16, unique=True)
    group_code = models.CharField(editable=False, max_length=16)

    installment = models.PositiveIntegerField(default=1)
    quantity_of_installments = models.PositiveIntegerField(default=1)

    record_type = models.CharField(max_length=64, choices=RECORD_CHOICES)

    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name="records")
