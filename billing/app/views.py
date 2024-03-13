from rest_framework import generics
from .models import Product, Order, Payment
from .serializers import ProductSerializer, OrderSerializer, PaymentSerializer


class ProductListAPIView(generics.ListAPIView):
    """
    Представление для получения списка всех продуктов.
    Доступно всем пользователям для просмотра списка продуктов.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class OrderCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания нового заказа.
    Позволяет пользователям создавать заказы, указывая список продуктов и их количество.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class PaymentCreateAPIView(generics.CreateAPIView):
    """
    Представление для создания нового платежа по заказу.
    При создании платежа автоматически устанавливает сумму платежа, равную итоговой сумме заказа.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        """
        Переопределяет метод создания для установки суммы платежа.
        Сумма платежа автоматически устанавливается равной итоговой сумме связанного заказа.
        """
        order_id = self.request.data.get('order')
        order = Order.objects.get(id=order_id)
        serializer.save(amount=order.total_sum)
