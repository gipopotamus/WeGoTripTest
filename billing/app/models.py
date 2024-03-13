from django.db import models
from django.utils import timezone


class Product(models.Model):
    """
    Модель продукта, содержащая информацию о товарах.
    """
    name = models.CharField(max_length=255, verbose_name="Название")
    image = models.ImageField(upload_to='products/', verbose_name="Картинка", blank=True, null=True)
    content = models.TextField(verbose_name="Контент")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")

    def __str__(self):
        """Возвращает название продукта."""
        return self.name


class Order(models.Model):
    """
    Модель заказа, отражающая информацию о заказах пользователей.
    """
    STATUS_CHOICES = (
        ('created', 'Создан'),
        ('confirmed', 'Подтвержден'),
        ('completed', 'Завершен'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='created', verbose_name="Статус")
    creation_time = models.DateTimeField(default=timezone.now, verbose_name="Время создания")
    confirmation_time = models.DateTimeField(null=True, blank=True, verbose_name="Время подтверждения")

    def __str__(self):
        """Возвращает идентификатор и статус заказа."""
        return f"Order {self.id} - {self.status}"

    @property
    def total_sum(self):
        """
        Вычисляет итоговую сумму заказа на основе стоимости всех товаров в заказе.
        """
        return sum(item.product.cost * item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """
    Модель элемента заказа, связывает продукты с заказами и содержит количество каждого продукта.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Заказ")
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        """Возвращает строковое представление элемента заказа."""
        return f'{self.quantity} of {self.product.name}'

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"


class Payment(models.Model):
    """
    Модель платежа, содержит информацию о платежах, связанных с заказами.
    """
    PAYMENT_TYPE_CHOICES = (
        ('card', 'Карта'),
        ('bank_transfer', 'Банковский перевод'),
        ('paypal', 'PayPal'),
    )
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', verbose_name="Заказ")
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Сумма")
    status = models.CharField(max_length=255, verbose_name="Статус")
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='card', verbose_name="Тип оплаты")

    def __str__(self):
        """Возвращает идентификатор и статус платежа."""
        return f"Payment {self.id} - {self.status}"

    def save(self, *args, **kwargs):
        """
        Переопределяет метод сохранения, чтобы автоматически установить сумму платежа,
        равную итоговой сумме заказа, если она не была задана.
        """
        if not self.amount:
            self.amount = self.order.total_sum
        super().save(*args, **kwargs)
