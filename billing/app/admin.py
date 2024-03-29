import time
import requests
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.timezone import now

from .models import Product, Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    """
    Инлайн-класс для отображения элементов заказа непосредственно в форме заказа.
    """
    model = OrderItem
    extra = 1  # Предоставляет одну дополнительную строку для нового элемента заказа


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Административный класс для модели Order.
    """
    list_display = ('id', 'status', 'creation_time', 'confirmation_time', 'display_total_sum', 'confirm_order_link')
    inlines = [OrderItemInline]

    def get_urls(self):
        """
        Добавляет пользовательский URL для подтверждения заказов.
        """
        urls = super().get_urls()
        custom_urls = [
            path('<path:object_id>/confirm/', self.admin_site.admin_view(self.confirm_order), name='order-confirm'),
        ]
        return custom_urls + urls

    def display_total_sum(self, obj):
        """
        Отображает итоговую сумму заказа.
        """
        return obj.total_sum

    display_total_sum.short_description = "Итоговая сумма"

    def confirm_order_link(self, obj):
        """
        Возвращает HTML-ссылку для подтверждения заказа, если это возможно.
        """
        if obj.status == 'confirmed':
            return "Заказ подтвержден"
        elif obj.payments.filter(status="Оплачен").exists():
            return format_html('<a href="{}">Подтвердить заказ</a>',
                               reverse('admin:order-confirm', args=[obj.pk]))
        return "Платеж не подтвержден"

    confirm_order_link.short_description = 'Подтверждение заказа'
    confirm_order_link.allow_tags = True

    def confirm_order(self, request, object_id, *args, **kwargs):
        """
        Обрабатывает подтверждение заказа, изменяет его статус и отправляет POST-запрос на внешний сервис.
        """
        order = Order.objects.get(pk=object_id)
        if not order.payments.filter(status="Оплачен").exists():
            self.message_user(request, 'Заказ не может быть подтвержден без оплаченного платежа.', messages.ERROR)
            return HttpResponseRedirect('.')

        order.status = 'confirmed'
        order.confirmation_time = now()
        order.save()

        # Симуляция подготовки заказа
        time.sleep(2)

        # Отправка POST-запроса
        data = {
            "id": order.id,
            "amount": str(order.total_sum),
            "date": order.confirmation_time.isoformat()
        }
        requests.post('https://webhook.site/36693e00-8f59-4f7b-9a85-1d1e7ddde4d4', json=data)

        self.message_user(request, 'Заказ подтвержден.', messages.SUCCESS)
        return HttpResponseRedirect(reverse('admin:app_order_changelist'))


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Административный класс для модели Product.
    """
    list_display = ['name', 'cost', 'content']
    search_fields = ['name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Административный класс для модели Payment.
    """
    list_display = ['id', 'order', 'display_amount', 'status', 'payment_type']

    def display_amount(self, obj):
        """
        Отображает сумму платежа.
        """
        return obj.amount

    display_amount.short_description = "Сумма"
