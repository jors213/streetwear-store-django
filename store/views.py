from operator import index
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Stock, Order, OrderItem
from .templates import store
from rest_framework import viewsets
from .serializers import ProductSerializer, OrderSerializer
from django.db import transaction
from django.contrib import messages
from decimal import Decimal

def store_home(request):
    products = Product.objects.all()
    return render(request, 'store/store_home.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        selected_size = request.POST.get('size')
        cart = request.session.get('cart', [])
        item = {
            'product_id': product.id,
            'name': product.name,
            'price': float(product.price),
            'size': selected_size,
            'image_url': product.image.url
        }

        cart.append(item)
        request.session['cart'] = cart

        print(f"Carrito actual: {cart}")
        print(f"Talla seleccionada: {selected_size}")
        return redirect('store_home')
    return render(request, 'store/product_detail.html', {'product': product})

def view_cart(request):
    cart = request.session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render(request, 'store/cart.html',
                  {'cart': cart,
                    'total': total
                })

def remove_from_cart(request, index):
    cart = request.session.get('cart', [])

    if 0 <= index < len(cart):
        del cart[index]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('view_cart')

@transaction.atomic # <--- El "escudo" atómico: O todo sale bien, o nada se guarda.
def checkout(request):
    cart = request.session.get('cart', [])
    if not cart:
        return redirect('store_home')

    # Calculamos total asegurando que sea Decimal (para evitar errores con float)
    total = sum(Decimal(str(item['price'])) for item in cart)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')

        # 1. Crear la Orden (Aún no está confirmada hasta que termine el bloque atomic)
        order = Order.objects.create(
            name=name,
            email=email,
            address=address,
            city=city,
            total_price=total
        )

        try:
            for item in cart:
                # 2. BLOQUEO DE BASE DE DATOS (Lo más importante)
                # select_for_update() dice: "Base de datos, dame este stock y NO DEJES que nadie más lo toque hasta que yo termine".
                stock_item = Stock.objects.select_for_update().get(
                    product_id=item['product_id'], 
                    size=item['size']
                )

                # 3. Verificación de Stock en Tiempo Real
                if stock_item.quantity < 1:
                    # Si alguien nos ganó el click milisegundos antes, esto salta.
                    raise ValueError(f"Lo sentimos, el producto {item['name']} (Talla {item['size']}) se acaba de agotar.")

                # 4. Crear Item de Orden
                OrderItem.objects.create(
                    order=order,
                    product_name=item['name'],
                    size=item['size'],
                    price=Decimal(str(item['price'])),
                    quantity=1
                )

                # 5. Restar Stock
                stock_item.quantity -= 1
                stock_item.save()

        except ValueError as e:
            # Si algo falla (falta stock), el @transaction.atomic deshace TODO (borra la orden creada arriba)
            messages.error(request, str(e))
            return redirect('view_cart')

        # Si llegamos aquí, todo salió perfecto. Limpiamos carrito.
        del request.session['cart']
        return redirect('order_success', pk=order.id)

    return render(request, 'store/checkout.html', {'cart': cart, 'total': total})

def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'store/success.html', {'order': order})

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['post']