from django.contrib import admin
from .models import Costumer, Product, Cart, Order

@admin.register(Costumer)
class CostumerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'locality', 'city', 'zipcode', 'state','mobile']
    search_fields = ['name', 'city', 'state']
    list_filter = ['state']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'selling_price', 'discounted_price', 'brand', 'category']
    search_fields = ['title', 'brand']
    list_filter = ['category']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'quantity']
    search_fields = ['user__username', 'product__title']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'costumer', 'product', 'quantity', 'order_date', 'order_status']
    list_filter = ['order_status', 'order_date']
    search_fields = ['user__username', 'product__title']
