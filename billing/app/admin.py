from django.contrib import admin
from .models import Product, Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Предоставляет одну дополнительную строку для нового элемента заказа


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'creation_time', 'confirmation_time', 'display_total_sum']
    inlines = [OrderItemInline]

    def display_total_sum(self, obj):
        return obj.total_sum
    display_total_sum.short_description = "Итоговая сумма"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'cost', 'content']
    search_fields = ['name']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'display_amount', 'status', 'payment_type']

    def display_amount(self, obj):
        return obj.amount
    display_amount.short_description = "Сумма"
