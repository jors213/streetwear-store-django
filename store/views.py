from operator import index
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Stock, Order, OrderItem
from .templates import store

# Create your views here.

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
        # Aquí podrías manejar la lógica de agregar al carrito, etc.
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

def checkout(request):
    cart = request.session.get('cart', [])
    if not cart:
        return redirect('store_home')

    total = sum(item['price'] for item in cart)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')

        order = Order.objects.create(
            name=name,
            email=email,
            address=address,
            city=city,
            total_price=total
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product_name=item['name'],
                size=item['size'],
                price=item['price'],
                quantity=1
            )
            stock_item = Stock.objects.get(product_id=item['product_id'], size=item['size'])
            stock_item.quantity -= 1
            stock_item.save()

            print(f"Stock actualizado: {item['name']} talla {item['size']} Nueva cantidad: {stock_item.quantity} unidades.")
        del request.session['cart']
        return redirect('order_success', pk=order.id)
    return render(request, 'store/checkout.html', {'cart': cart, 'total': total})

def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'store/success.html', {'order': order})