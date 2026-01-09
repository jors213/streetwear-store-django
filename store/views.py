import uuid
from operator import index
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Stock, Order, OrderItem
from .templates import store
from rest_framework import viewsets
from .serializers import ProductSerializer, OrderSerializer
from django.db import transaction
from django.contrib import messages
from decimal import Decimal
from .webpay import WebpayService
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.urls import reverse

def store_home(request):
    products = Product.objects.all().order_by('-id') 
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

@transaction.atomic
def checkout(request):
    cart = request.session.get('cart', [])
    if not cart:
        return redirect('store_home')

    total = sum(Decimal(str(item['price'])) for item in cart)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')

        # 1. Crear la Orden como PENDIENTE
        order = Order.objects.create(
            name=name,
            email=email,
            address=address,
            city=city,
            total_price=total,
            status='PENDING' # Importante: Nace pendiente
        )

        try:
            # 2. Lógica de Stock (Bloqueo Pesimista)
            for item in cart:
                stock_item = Stock.objects.select_for_update().get(
                    product_id=item['product_id'], 
                    size=item['size']
                )

                if stock_item.quantity < 1:
                    raise ValueError(f"Lo sentimos, el producto {item['name']} (Talla {item['size']}) se acaba de agotar.")

                # Crear Item
                OrderItem.objects.create(
                    order=order,
                    product_name=item['name'],
                    size=item['size'],
                    price=Decimal(str(item['price'])),
                    quantity=1
                )

                # Restar Stock (Reserva temporal)
                stock_item.quantity -= 1
                stock_item.save()

            # --- AQUÍ CAMBIA: INTEGRACIÓN WEBPAY ---
            
            # Inicializamos el servicio
            service = WebpayService()
            session_id = str(uuid.uuid4())
            return_url = request.build_absolute_uri(reverse('webpay_callback'))
            
            # Llamamos a Transbank
            response = service.create_transaction(
                buy_order=str(order.id),
                session_id=session_id,
                amount=float(total),
                return_url=return_url
            )
            
            # Guardamos el token para validar después
            order.webpay_token = response['token']
            order.save()
            
            # Redirigimos al banco (NO borramos el carrito todavía)
            return redirect(response['url'] + '?token_ws=' + response['token'])

        except ValueError as e:
            messages.error(request, str(e))
            return redirect('view_cart')
        except Exception as e:
            messages.error(request, f"Error al iniciar pago: {str(e)}")
            return redirect('view_cart')

    return render(request, 'store/checkout.html', {'cart': cart, 'total': total})

def webpay_callback(request):
    token = request.GET.get('token_ws')
    
    if not token:
        # Caso: Usuario cancela en el formulario de Webpay (TBK_TOKEN)
        messages.error(request, "La transacción fue anulada por el usuario.")
        return redirect('view_cart')

    try:
        service = WebpayService()
        response = service.commit_transaction(token) # Preguntamos a Transbank: "¿Pagó?"
        
        # Buscamos la orden
        order = get_object_or_404(Order, webpay_token=token)
        
        if response['status'] == 'AUTHORIZED' and response['response_code'] == 0:
            # --- CASO ÉXITO ---
            order.status = 'PAID'
            order.save()
            
            # Ahora sí borramos el carrito
            if 'cart' in request.session:
                del request.session['cart']
            
            messages.success(request, "¡Pago exitoso! Tu pedido está en camino.")
            return redirect('order_success', pk=order.id)
            
        else:
            # --- CASO FALLO/RECHAZO ---
            order.status = 'REJECTED'
            order.save()
            
            # CRÍTICO: Devolver el Stock (Rollback manual)
            for item in order.items.all():
                # Buscamos el stock exacto
                try:
                    # Ojo: Aquí asumimos que el producto y talla existen en tu lógica de stock
                    # Debes adaptar esto si tu modelo Stock usa IDs diferentes, pero basado en tu código:
                    product = Product.objects.get(name=item.product_name) # Ojo con esto si cambias nombres
                    # Mejor sería haber guardado product_id en OrderItem, pero por ahora:
                    stock_item = Stock.objects.filter(product=product, size=item.size).first()
                    if stock_item:
                        stock_item.quantity += 1
                        stock_item.save()
                except Exception as e:
                    print(f"Error devolviendo stock: {e}")

            messages.error(request, "El pago fue rechazado por el banco. Hemos liberado el stock.")
            return redirect('view_cart')

    except Exception as e:
        print(f"Error técnico en callback: {e}")
        messages.error(request, "Ocurrió un error al procesar el pago.")
        return redirect('view_cart')

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

@api_view(['GET', 'POST', 'PUT']) # Webpay a veces retorna por POST, a veces GET
def validate_payment(request):
    """
    Endpoint de Callback: Transbank redirige aquí después del pago.
    """
    token = request.GET.get('token_ws') or request.data.get('token_ws')

    if not token:
        # Caso: Usuario aborta la compra en el formulario Webpay
        return Response({'status': 'ABORTED', 'message': 'Compra anulada por usuario'}, status=400)

    try:
        service = WebpayService()
        # Confirmamos la transacción con Transbank (Commit)
        response = service.commit_transaction(token)
        
        # Recuperamos la orden local
        order = Order.objects.get(webpay_token=token)

        if response['status'] == 'AUTHORIZED' and response['response_code'] == 0:
            # --- ÉXITO ---
            order.status = 'PAID'
            order.save()
            return Response({
                'message': 'Pago exitoso',
                'order_id': order.id,
                'status': 'PAID',
                'amount': order.total_price,
                'details': response
            })
        else:
            # --- RECHAZO (Senior Logic: Rollback de Stock) ---
            order.status = 'REJECTED'
            order.save()
            
            # Devolvemos los productos al inventario
            for item in order.items.all():
                # Nota: Esto asume que el producto y talla siguen existiendo
                # En un sistema real, usaríamos product_id guardado en OrderItem
                try:
                    product = Product.objects.get(name=item.product_name)
                    stock_item = Stock.objects.filter(product=product, size=item.size).first()
                    if stock_item:
                        stock_item.quantity += item.quantity
                        stock_item.save()
                except Exception as e:
                    print(f"Error crítico devolviendo stock: {e}")

            return Response({
                'message': 'Pago rechazado o anulado. Stock liberado.',
                'status': 'REJECTED',
                'details': response
            }, status=400)

    except Order.DoesNotExist:
        return Response({'error': 'Orden no encontrada para este token'}, status=404)
    except Exception as e:
        return Response({'error': f'Error técnico: {str(e)}'}, status=500)

def track_orders(request):
    orders = None
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Buscamos todas las órdenes de ese correo, ordenadas por fecha (más reciente primero)
            orders = Order.objects.filter(email=email).order_by('-created_at')
    
    return render(request, 'store/track_orders.html', {'orders': orders})

def order_detail(request, pk):
    # Buscamos el pedido o devolvemos error 404 si no existe
    order = get_object_or_404(Order, pk=pk)
    
    # Renderizamos la plantilla con la información del pedido
    return render(request, 'store/order_detail.html', {'order': order})