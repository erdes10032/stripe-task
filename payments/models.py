from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal, ROUND_HALF_UP


class Item(models.Model):
    CURRENCY_CHOICES = [
        ("usd", "USD"),
        ("eur", "EUR"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Price in major currency units (e.g. dollars/euros).",
    )
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="usd")

    def __str__(self):
        return f"{self.name} ({self.currency})"

    def price_minor_units(self) -> int:
        return int((self.price * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class Discount(models.Model):
    name = models.CharField(max_length=100)
    percent_off = models.FloatField(validators=[MinValueValidator(0.01), MaxValueValidator(100.0)])
    stripe_coupon_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Tax(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    stripe_tax_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    items = models.ManyToManyField(Item)
    discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)
    tax = models.ForeignKey(Tax, null=True, blank=True, on_delete=models.SET_NULL)

    def clean(self):
        if not self.pk:
            # During admin create flow object has no PK yet; M2M relation is unavailable.
            return
        currencies = set(self.items.values_list("currency", flat=True))
        if len(currencies) > 1:
            raise ValidationError("All items must have the same currency")
        if not currencies:
            raise ValidationError("Order must contain at least one item.")

    def currency(self):
        return self.items.first().currency if self.items.exists() else "usd"

    def __str__(self):
        return f"Order #{self.id}"