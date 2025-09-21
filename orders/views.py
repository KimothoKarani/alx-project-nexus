from django.db import transaction
from django.db.models import F, Sum
from django_filters import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Order, OrderItem, Payment
from users.models import Address
from products.models import Product
from carts.models import Cart, CartItem
from .serializers import OrderSerializer, OrderItemSerializer, PaymentSerializer
from nexus_commerce.permissions import IsAuthenticatedAndOwner
from rest_framework import serializers
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Orders:
    - Users can only access their own orders
    - Admin/staff can access all orders
    - Supports filtering and ordering
    - Provides a custom endpoint to create orders from the user's cart
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedAndOwner]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'created_at']
    ordering_fields = ['created_at', 'total_amount']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, "user_type", None) == "admin":
            return self.queryset.select_related("user", "shipping_address", "billing_address").prefetch_related("items__product")
        return (
            self.queryset.filter(user=user)
            .select_related("user", "shipping_address", "billing_address")
            .prefetch_related("items__product")
        )

    @transaction.atomic
    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def create_from_cart(self, request):
        """
        Create an order from the authenticated user's active cart.
        - Validates stock and addresses
        - Moves cart items to order items
        - Deactivates cart
        """
        user = request.user
        user_cart = Cart.objects.filter(user=user, is_active=True).prefetch_related("items__product").first()

        if not user_cart or not user_cart.items.exists():
            return Response(
                {"detail": "Your cart is empty or not found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        billing_address_id = request.data.get("billing_address")
        shipping_address_id = request.data.get("shipping_address")

        if not billing_address_id:
            return Response(
                {"detail": "Billing address is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            billing_address = Address.objects.get(id=billing_address_id, user=user)
            shipping_address = (
                Address.objects.get(id=shipping_address_id, user=user)
                if shipping_address_id
                else billing_address
            )
        except Address.DoesNotExist:
            return Response(
                {"detail": "Provided address(es) not found or do not belong to user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate stock
        insufficient = [
            f"{item.product.name} (Available: {item.product.stock_quantity})"
            for item in user_cart.items.all()
            if item.quantity > item.product.stock_quantity
        ]
        if insufficient:
            return Response(
                {"detail": f"Insufficient stock for: {', '.join(insufficient)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Compute total using DB-side aggregation
        total_amount = sum(
            item.quantity * (item.price_at_time or item.product.price)
            for item in user_cart.items.all()
        )

        # Create order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            total_amount=total_amount,
            status=Order.OrderStatus.PENDING,
            payment_status=Order.PaymentStatus.PENDING,
        )

        # Create order items and decrement stock
        order_items = []
        for cart_item in user_cart.items.all():
            order_items.append(OrderItem(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.price_at_time or cart_item.product.price,
            ))
            cart_item.product.stock_quantity = F("stock_quantity") - cart_item.quantity
            cart_item.product.save(update_fields=["stock_quantity"])

        OrderItem.objects.bulk_create(order_items)

        # Clear and deactivate cart
        user_cart.is_active = False
        user_cart.save(update_fields=["is_active"])
        user_cart.items.all().delete()

        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)


class OrderItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for OrderItems.
    Users see only their own order items, staff/admin see all.
    """
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedAndOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, "user_type", None) == "admin":
            return self.queryset.select_related("order", "product")
        return self.queryset.filter(order__user=user).select_related("order", "product")


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Payments:
    - Users can only create payments for their own pending orders
    - Admin/staff can manage all payments
    - Integrate with external payment gateway in the future
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedAndOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or getattr(user, "user_type", None) == "admin":
            return self.queryset.select_related("order", "order__user")
        return self.queryset.filter(order__user=user).select_related("order", "order__user")

    @transaction.atomic
    def perform_create(self, serializer):
        order = serializer.validated_data["order"]

        if order.user != self.request.user:
            self.permission_denied(self.request, message="You can only pay for your own orders.")

        if order.payment_status != Order.PaymentStatus.PENDING:
            raise serializers.ValidationError({"detail": "This order is not eligible for payment."})

        # TODO: integrate payment gateway (Stripe, PayPal, Mpesa, etc.)
        payment = serializer.save(status=Payment.PaymentStatus.SUCCEEDED)

        # Update order status
        order.payment_status = Order.PaymentStatus.PAID
        order.status = Order.OrderStatus.PROCESSING
        order.save(update_fields=["payment_status", "status", "updated_at"])

        # TODO: trigger background tasks (Celery) for:
        # - sending order confirmation email
        # - notifying sellers/warehouse
        return payment
