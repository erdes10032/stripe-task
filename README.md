# Stripe Task (Django + Stripe)

Готовый к деплою backend-проект для оплаты товаров через Stripe Checkout и PaymentIntent.

## Что реализовано

- `GET /item/{id}/` — HTML-страница товара с кнопкой оплаты.
- `GET /buy/{id}/` — создание Checkout Session для одного `Item`.
- `GET /order/{id}/buy/` — создание Checkout Session для `Order` (несколько `Item`, поддержка скидки и налога).
- `GET /intent/{id}/` — создание Stripe PaymentIntent для `Item`.
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
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Откройте:
- `http://127.0.0.1:8000/admin/`
- `http://127.0.0.1:8000/item/1/`

## Запуск в Docker

```bash
docker compose up --build
```

`docker-compose` автоматически применяет миграции перед запуском `gunicorn`.

## Как проверить функционал

1. В админке создайте `Item` (например `12.50`, `usd`).
2. Для проверки скидок/налогов создайте:
   - `Discount` (например `10%`);
   - `Tax` (например `20%`);
   - `Order` с несколькими `Item` одной валюты и привяжите `Discount`/`Tax`.
3. Проверка Checkout:
   - для item: `http://127.0.0.1:8000/item/<id>/`
   - для order: `http://127.0.0.1:8000/order/<id>/buy/`
4. Проверка JSON-режима:
   - `http://127.0.0.1:8000/buy/<id>/?format=json`
   - `http://127.0.0.1:8000/order/<id>/buy/?format=json`
5. Проверка PaymentIntent:
   - `http://127.0.0.1:8000/intent/<id>/`

## Перед деплоем

- Установите `DJANGO_DEBUG=False`.
- Пропишите домен в `DJANGO_ALLOWED_HOSTS`.
- Пропишите HTTPS домен в `DJANGO_CSRF_TRUSTED_ORIGINS`.
- Установите `APP_BASE_URL=https://your-domain`.
- Используйте production БД (PostgreSQL) и секреты из менеджера секретов.
