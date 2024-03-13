from django.contrib import admin
from .models import Product, Order, Payment


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_sum', 'status', 'creation_time', 'confirmation_time')
    list_filter = ('status', 'creation_time')
    search_fields = ('id',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'status', 'payment_type')
    list_filter = ('status', 'payment_type')
    search_fields = ('order__id',)
