from django.db import models

# store/models.py

from django.db import models

class Product(models.Model):
    # Definimos las categorías fijas para mantener orden
    CATEGORY_CHOICES = [
        ('poleras', 'Poleras'),
        ('polerones', 'Polerones'),
        ('pantalones', 'Pantalones'),
        ('accesorios', 'Accesorios'),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Recuerda que cambiamos a Decimal
    image = models.ImageField(upload_to='products/')
    
    # NUEVOS CAMPOS
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='poleras')
    is_new_arrival = models.BooleanField(default=False, verbose_name="¿Es Nueva Colección?")
    description = models.TextField(blank=True, null=True) # Para los detalles

    def __str__(self):
        return self.name

class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=4)
    quantity = models.PositiveIntegerField()

class Order(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Pedido #{self.id} - {self.name}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100)
    size = models.CharField(max_length=10)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"