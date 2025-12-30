from django.contrib import admin
from .models import Product, Stock, Order, OrderItem

# 1. Configuración para ver los productos DENTRO del pedido
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # No muestra filas vacías extra
    readonly_fields = ('product_name', 'size', 'price', 'quantity') # Para que nadie modifique lo que ya se vendió

# 2. Configuración del Pedido principal
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'city', 'total_price', 'created_at') # Columnas que verás en la lista
    inlines = [OrderItemInline] # Aquí conectamos la tabla de productos

# 3. Registro de modelos
admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(Order, OrderAdmin)
# No registramos OrderItem por separado porque ya se ve dentro de Order