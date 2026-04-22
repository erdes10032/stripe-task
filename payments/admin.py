from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import Item, Order, Discount, Tax


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "currency")
    list_filter = ("currency",)
    search_fields = ("name", "description")


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        items = cleaned_data.get("items")
        if not items:
            raise ValidationError("Order must contain at least one item.")

        currencies = set(items.values_list("currency", flat=True))
        if len(currencies) > 1:
            raise ValidationError("All items must have the same currency.")
        return cleaned_data


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ("id", "discount", "tax")
    filter_horizontal = ("items",)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "percent_off", "stripe_coupon_id")
    search_fields = ("name", "stripe_coupon_id")


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "percentage", "stripe_tax_id")
    search_fields = ("name", "stripe_tax_id")