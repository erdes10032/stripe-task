from django.urls import path
from . import views

urlpatterns = [
    path('item/<int:id>/', views.item_page),
    path('buy/<int:id>/', views.buy_item),
    path('order/<int:id>/buy/', views.buy_order),
    path('intent/<int:id>/', views.payment_intent),
    path('success/', views.checkout_success),
    path('cancel/', views.checkout_cancel),
]