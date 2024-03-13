from django.urls import path
from .views import ProductListAPIView, OrderCreateAPIView, PaymentCreateAPIView

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('orders/', OrderCreateAPIView.as_view(), name='order-create'),
    path('payments/', PaymentCreateAPIView.as_view(), name='payment-create'),
]
