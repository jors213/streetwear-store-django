from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'products', views.ProductViewSet, )
router.register(r'orders', views.OrderViewSet, )

urlpatterns = [
    path('api/', include(router.urls)),

    path('api/payment/validate/', views.validate_payment, name='api_payment_validate'),

    path('', views.store_home, name='store_home'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/remove/<int:index>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('webpay/callback/', views.webpay_callback, name='webpay_callback'),

    path('success/<int:pk>/', views.order_success, name='order_success'),

    path('track-orders/', views.track_orders, name='track_orders'),

    path('order/<int:pk>/', views.order_detail, name='order_detail'),
]