from rest_framework import serializers
from .models import Order, Product, Stock, OrderItem

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['size', 'quantity']

class ProductSerializer(serializers.ModelSerializer):
    stock = StockSerializer(source='stock_set', many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image', 'stock']

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'size', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'items', 'name', 'email', 'address', 'city', 'total_price']
        read_only_fields = ['total_price']

    def create(self, validated_data):
            items_data = validated_data.pop('items')

            order = Order.objects.create(total_price=0, **validated_data)

            total_accumulated = 0

            for item_data in items_data:
                

                try:
                    stock = Stock.objects.get(
                        product_id=item_data['product_id'], 
                        size=item_data['size']
                    )
                except Stock.DoesNotExist:
                    raise serializers.ValidationError(f"No encontramos stock para el producto {item_data['product_id']} talla {item_data['size']}")

                if stock.quantity < item_data['quantity']:
                    raise serializers.ValidationError(f"No hay suficiente stock de {stock.product.name} en talla {stock.size}")

                stock.quantity -= item_data['quantity']
                stock.save()
                
                item_price = stock.product.price * item_data['quantity']
                total_accumulated += item_price

                OrderItem.objects.create(
                    order=order,
                    product_name=stock.product.name,
                    size=item_data['size'],
                    price=stock.product.price,
                    quantity=item_data['quantity']
                )
            order.total_price = total_accumulated
            order.save()
            return order