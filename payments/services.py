import stripe
from django.conf import settings

from .models import Item, Order


def _get_secret_key(currency: str) -> str:
    keypair = settings.STRIPE_KEYS_BY_CURRENCY.get(currency.lower())
    if not keypair or not keypair.get("secret"):
        raise ValueError(f"Stripe secret key is not configured for currency '{currency}'.")
    return keypair["secret"]


def get_public_key(currency: str) -> str:
    keypair = settings.STRIPE_KEYS_BY_CURRENCY.get(currency.lower())
    if not keypair or not keypair.get("public"):
        raise ValueError(f"Stripe public key is not configured for currency '{currency}'.")
    return keypair["public"]


def create_coupon(secret_key: str, discount):
    if discount.stripe_coupon_id:
        return discount.stripe_coupon_id

    coupon = stripe.Coupon.create(
        percent_off=discount.percent_off,
        duration="once",
        api_key=secret_key,
    )
    discount.stripe_coupon_id = coupon.id
    discount.save(update_fields=["stripe_coupon_id"])
    return coupon.id


def create_tax_rate(secret_key: str, tax):
    if tax.stripe_tax_id:
        return tax.stripe_tax_id

    tax_rate = stripe.TaxRate.create(
        display_name=tax.name,
        percentage=tax.percentage,
        inclusive=False,
        api_key=secret_key,
    )
    tax.stripe_tax_id = tax_rate.id
    tax.save(update_fields=["stripe_tax_id"])
    return tax_rate.id


def create_checkout_session(item: Item):
    return create_checkout_session_with_base_url(item=item, base_url=settings.APP_BASE_URL)


def create_checkout_session_with_base_url(item: Item, base_url: str):
    secret_key = _get_secret_key(item.currency)
    success_url = f"{base_url}/success/"
    cancel_url = f"{base_url}/cancel/"
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": item.currency,
                "product_data": {
                    "name": item.name,
                    "description": item.description,
                },
                "unit_amount": item.price_minor_units(),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        api_key=secret_key,
    )


def create_order_session(order: Order):
    return create_order_session_with_base_url(order=order, base_url=settings.APP_BASE_URL)


def create_order_session_with_base_url(order: Order, base_url: str):
    currencies = set(order.items.values_list("currency", flat=True))
    if len(currencies) > 1:
        raise ValueError("All items in Order must have same currency")
    if not currencies:
        raise ValueError("Order must contain at least one item")

    currency = order.currency()
    secret_key = _get_secret_key(currency)

    tax_rates = []
    if order.tax:
        tax_rates.append(create_tax_rate(secret_key, order.tax))

    line_items = []
    for item in order.items.all():
        line_item = {
            "price_data": {
                "currency": currency,
                "product_data": {"name": item.name, "description": item.description},
                "unit_amount": item.price_minor_units(),
            },
            "quantity": 1,
        }
        if tax_rates:
            line_item["tax_rates"] = tax_rates
        line_items.append(line_item)

    discounts = None
    if order.discount:
        discounts = [{"coupon": create_coupon(secret_key, order.discount)}]

    success_url = f"{base_url}/success/"
    cancel_url = f"{base_url}/cancel/"
    return stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        discounts=discounts,
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        api_key=secret_key,
    )


def create_payment_intent(item: Item):
    secret_key = _get_secret_key(item.currency)
    return stripe.PaymentIntent.create(
        amount=item.price_minor_units(),
        currency=item.currency,
        automatic_payment_methods={"enabled": True},
        api_key=secret_key,
    )