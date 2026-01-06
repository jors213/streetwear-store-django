from django.contrib import admin
from .models import Product, Stock, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 
    readonly_fields = ('product_name', 'size', 'price', 'quantity')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'city', 'total_price', 'created_at') 
    inlines = [OrderItemInline] 

admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Order, OrderAdmin)