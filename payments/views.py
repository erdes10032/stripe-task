from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET

from .models import Item, Order
from .services import (
    create_checkout_session_with_base_url,
    create_order_session_with_base_url,
    create_payment_intent,
    get_public_key,
)


@require_GET
def item_page(request, id):
    item = get_object_or_404(Item, id=id)
    return render(
        request,
        "item.html",
        {
            "item": item,
            "stripe_public_key": get_public_key(item.currency),
        },
    )


@require_GET
def buy_item(request, id):
    item = get_object_or_404(Item, id=id)
    base_url = request.build_absolute_uri("/").rstrip("/")
    try:
        session = create_checkout_session_with_base_url(item=item, base_url=base_url)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    if "text/html" in request.headers.get("Accept", "") and request.GET.get("format") != "json":
        return redirect(session.url)
    return JsonResponse({"id": session.id})


@require_GET
def buy_order(request, id):
    order = get_object_or_404(Order, id=id)
    base_url = request.build_absolute_uri("/").rstrip("/")
    try:
        session = create_order_session_with_base_url(order=order, base_url=base_url)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    if "text/html" in request.headers.get("Accept", "") and request.GET.get("format") != "json":
        return redirect(session.url)
    return JsonResponse({"id": session.id})


@require_GET
def payment_intent(request, id):
    item = get_object_or_404(Item, id=id)
    try:
        intent = create_payment_intent(item)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"client_secret": intent.client_secret})


@require_GET
def checkout_success(request):
    return JsonResponse({"status": "success"})


@require_GET
def checkout_cancel(request):
    return JsonResponse({"status": "cancelled"})