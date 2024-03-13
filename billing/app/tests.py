from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from .models import Product, Order, OrderItem, Payment
from rest_framework.test import APITestCase


class ModelTests(TestCase):

    def setUp(self):
        # Создаем тестовый продукт
        self.product = Product.objects.create(
            name='Test Product',
            content='Test Content',
            cost='9.99'
        )

        # Создаем тестовый заказ
        self.order = Order.objects.create(
            status='created',
            creation_time=timezone.now()
        )

        # Создаем тестовый платеж
        self.payment = Payment.objects.create(
            order=self.order,
            amount='9.99',
            status='Оплачен',
            payment_type='card'
        )

    def test_order_total_sum(self):
        """Тестирование вычисления итоговой суммы заказа."""
        OrderItem.objects.create(order=self.order, product=self.product, quantity=2)
        self.assertEqual(float(self.order.total_sum), 19.98)

    def test_payment_association(self):
        """Тестирование связи платежа с заказом."""
        self.assertEqual(self.payment.order, self.order)


class ProductAPITests(APITestCase):

    def setUp(self):
        # Создаем тестовый продукт
        Product.objects.create(
            name='Test Product',
            content='Test Content',
            cost='9.99'
        )

    def test_get_product_list(self):
        """Тестирование получения списка продуктов."""
        response = self.client.get('/products/')  # Укажите здесь правильный URL
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Product')


class OrderAndPaymentAPITests(APITestCase):

    def setUp(self):
        # Создание продуктов для тестирования
        self.product1 = Product.objects.create(
            name='Test Product 1',
            content='Test Content 1',
            cost=Decimal('10.00')
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            content='Test Content 2',
            cost=Decimal('20.00')
        )

    def test_create_order(self):
        """Тестирование создания нового заказа."""
        url = reverse('order-create')  # Убедитесь, что имя URL соответствует определенному в urls.py
        data = {
            "items": [
                {"product": self.product1.id, "quantity": 2},
                {"product": self.product2.id, "quantity": 1}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.total_sum, Decimal('40.00'))  # 2 * 10.00 + 1 * 20.00

    def test_create_payment_for_order(self):
        """Тестирование создания платежа для заказа."""
        # Сначала создаем заказ
        order = Order.objects.create(status='created')
        # URL для создания платежа
        url = reverse('payment-create')  # Убедитесь, что имя URL соответствует определенному в urls.py
        data = {
            "order": order.id,
            "status": "Оплачен",
            "payment_type": "card"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(order.payments.count(), 1)
        payment = order.payments.first()
        self.assertEqual(payment.status, "Оплачен")
        self.assertEqual(payment.amount, order.total_sum)  # Проверяем, что сумма платежа равна сумме заказа


class AdminTest(TestCase):
    def setUp(self):
        # Создаем пользователя администратора
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.client.login(username='admin', password='password123')

        # Создаем тестовые объекты
        self.product = Product.objects.create(
            name='Test Product',
            content='Test Content',
            cost='9.99'
        )
        self.order = Order.objects.create()

    def test_order_confirm_action(self):
        """Тест выполнения действия подтверждения заказа."""
        # Добавление оплаченного платежа к заказу для возможности подтверждения
        Payment.objects.create(order=self.order, amount='9.99', status='Оплачен', payment_type='card')

        # URL для действия подтверждения заказа
        confirm_url = reverse('admin:order-confirm', args=[self.order.pk])
        response = self.client.get(confirm_url)
        # Перенаправление обратно на список заказов после подтверждения
        self.assertRedirects(response, reverse('admin:app_order_changelist'))

        # Проверка изменения статуса заказа
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'confirmed')