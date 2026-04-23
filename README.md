# Stripe Task (Django + Stripe)

Готовый к деплою backend-проект для оплаты товаров через Stripe Checkout и PaymentIntent.

## Что реализовано

- `GET /item/{id}/` — HTML-страница товара с кнопкой оплаты.
- `GET /buy/{id}/` — создание Checkout Session для одного `Item`.
- `GET /order/{id}/buy/` — создание Checkout Session для `Order` (несколько `Item`, поддержка скидки и налога).
- `GET /intent/{id}/` — создание Stripe PaymentIntent для `Item`.
- На странице `GET /item/{id}/` есть два рабочих сценария оплаты:
  - `Pay with Checkout` (редирект в Stripe Checkout),
  - `Pay with PaymentIntent` (создание intent + подтверждение картой через Stripe.js `confirmCardPayment`).
- `GET /success/`, `GET /cancel/` — служебные URL после оплаты.

## Модели

- `Item(name, description, price, currency)` — цена в долларах/евро (`Decimal`), не в центах.
- `Order(items, discount, tax)`
- `Discount(name, percent_off, stripe_coupon_id)`
- `Tax(name, percentage, stripe_tax_id)`

Все модели доступны в Django Admin.

## Локальный запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

Откройте:
- `http://127.0.0.1:8000/admin/`
- `http://127.0.0.1:8000/item/1/`

## Запуск в Docker

```bash
docker compose up --build
```


## Как проверить функционал

1. Проверка Checkout:
   - для item: `https://stripe-task-2.onrender.com/item/1/` и нажмите на кнопку `Pay with Checkout`
   - для order: `https://stripe-task-2.onrender.com/order/1/buy/`
   В открывшемся окне введите тестовую карту Stripe (например `4242 4242 4242 4242`, любая будущая дата, любой CVC, любая почта, любое имя пользователя и страна). Нажмите `Оплатить` и откроется страница со статусом платежа
2. Проверка JSON-режима:
   - `https://stripe-task-2.onrender.com/buy/1/?format=json`
   - `https://stripe-task-2.onrender.com/order/1/buy/?format=json`
3. Проверка PaymentIntent:
   - откройте `https://stripe-task-2.onrender.com/item/1/`
   - нажмите `Pay with PaymentIntent`
   - введите тестовую карту Stripe (например `4242 4242 4242 4242`, любая будущая дата, любой CVC, любой индекс)
   - нажмите `Confirm PaymentIntent` и проверьте статус `Payment succeeded.`
4. При желании также можно самостоятельно создать товары по адресу `https://stripe-task-2.onrender.com/admin/` (логин и пароль `admin`)

