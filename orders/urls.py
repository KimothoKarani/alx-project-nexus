from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')  # /api/v1/orders/
router.register(r'items', OrderItemViewSet, basename='order_item')  # /api/v1/orders/items/
router.register(r'payments', PaymentViewSet, basename='payment')  # /api/v1/orders/payments/

urlpatterns = [
    path('', include(router.urls)),
    path('create-from-cart/', OrderViewSet.as_view({'post': 'create_from_cart'}), name='order_create_from_cart'),
]
