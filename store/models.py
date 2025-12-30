from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')

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
    total_price = models.FloatField()

    def __str__(self):
        return f"Pedido #{self.id} - {self.name}"
    
class OrderItem(models.Model):
    # Conexión con el Pedido principal
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    
    # Guardamos los datos "congelados" (por si el producto cambia de precio mañana)
    product_name = models.CharField(max_length=100)
    size = models.CharField(max_length=10)
    price = models.FloatField()
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name}"