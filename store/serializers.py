import uuid
from rest_framework import serializers
from .models import Order, Product, Stock, OrderItem
from .webpay import WebpayService

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
    # Campos calculados (no van a la BD) para guiar al frontend
    payment_url = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'items', 'name', 'email', 'address', 'city', 'total_price', 'status', 'payment_url', 'token']
        read_only_fields = ['total_price', 'status', 'payment_url', 'token']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # 1. Crear la orden (PENDING por defecto)
        order = Order.objects.create(total_price=0, status='PENDING', **validated_data)

        total_accumulated = 0

        # 2. Lógica de Negocio: Gestión de Stock y Cálculo de Precios
        for item_data in items_data:
            try:
                stock = Stock.objects.get(
                    product_id=item_data['product_id'], 
                    size=item_data['size']
                )
            except Stock.DoesNotExist:
                raise serializers.ValidationError(f"Stock no encontrado: ID {item_data['product_id']} Talla {item_data['size']}")

            # Bloqueo optimista: Verificamos antes de restar
            if stock.quantity < item_data['quantity']:
                raise serializers.ValidationError(f"Sin stock suficiente para {stock.product.name} ({stock.size})")

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

        # 3. Integración con Pasarela de Pago (Webpay)
        try:
            service = WebpayService()
            session_id = str(uuid.uuid4())
            buy_order = str(order.id)
            amount = float(order.total_price)
            
            # URL de retorno: Donde Webpay devolverá al usuario (Endpoint de nuestra API)
            # En producción, esto debería venir de una variable de entorno (settings.API_URL)
            return_url = "http://127.0.0.1:8000/api/payment/validate/"

            response = service.create_transaction(
                buy_order=buy_order,
                session_id=session_id,
                amount=amount,
                return_url=return_url
            )

            # Persistencia del Token para futura validación
            order.webpay_token = response['token']
            order.save()

            # Inyectamos los datos en la respuesta (sin guardar en BD)
            order.payment_url = response['url'] + '?token_ws=' + response['token']
            order.token = response['token']

        except Exception as e:
            # Senior Move: Si falla el pago, deberíamos considerar rollback del stock aquí.
            # Por ahora lanzamos error para que el cliente lo sepa.
            raise serializers.ValidationError(f"Error al iniciar Webpay: {str(e)}")

        return order