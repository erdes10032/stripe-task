from django.test import TestCase
from django.test import override_settings
from unittest.mock import patch
from decimal import Decimal

from .models import Discount, Item, Order, Tax
from .services import create_checkout_session_with_base_url


class ItemViewsTests(TestCase):
    def setUp(self):
        self.item = Item.objects.create(
            name="Test item",
            description="Test description",
            price="10.00",
            currency="usd",
        )

    @patch("payments.views.get_public_key", return_value="pk_test_example")
    def test_item_page_returns_html(self, _):
        response = self.client.get(f"/item/{self.item.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.item.name)

    @patch("payments.views.create_checkout_session_with_base_url")
    def test_buy_item_returns_session_id(self, mock_create_checkout_session):
        class Session:
            id = "cs_test_123"

        mock_create_checkout_session.return_value = Session()
        response = self.client.get(f"/buy/{self.item.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"id": "cs_test_123"})


class OrderViewsTests(TestCase):
    def setUp(self):
        self.item_1 = Item.objects.create(
            name="First",
            description="First item",
            price="10.00",
            currency="usd",
        )
        self.item_2 = Item.objects.create(
            name="Second",
            description="Second item",
            price="20.00",
            currency="usd",
        )
        self.discount = Discount.objects.create(name="D10", percent_off=10)
        self.tax = Tax.objects.create(name="VAT", percentage=20)
        self.order = Order.objects.create(discount=self.discount, tax=self.tax)
        self.order.items.add(self.item_1, self.item_2)

    @patch("payments.views.create_order_session_with_base_url")
    def test_buy_order_returns_session_id(self, mock_create_order_session):
        class Session:
            id = "cs_test_order_123"

        mock_create_order_session.return_value = Session()
        response = self.client.get(f"/order/{self.order.id}/buy/?format=json")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"id": "cs_test_order_123"})


class ServicesTests(TestCase):
    @override_settings(
        STRIPE_KEYS_BY_CURRENCY={
            "usd": {"public": "pk_usd", "secret": "sk_usd"},
            "eur": {"public": "pk_eur", "secret": "sk_eur"},
        }
    )
    @patch("payments.services.stripe.checkout.Session.create")
    def test_checkout_uses_currency_specific_secret_key(self, mock_create):
        item = Item.objects.create(
            name="Euro item",
            description="EUR",
            price=Decimal("15.00"),
            currency="eur",
        )
        create_checkout_session_with_base_url(item=item, base_url="http://example.com")
        _, kwargs = mock_create.call_args
        self.assertEqual(kwargs["api_key"], "sk_eur")
