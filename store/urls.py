from django.urls import path
from . import views

urlpatterns = [
    path('', views.store_home, name='store_home'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/remove/<int:index>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:pk>/', views.order_success, name='order_success'),
]