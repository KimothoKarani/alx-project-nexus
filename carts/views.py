from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from nexus_commerce.permissions import IsAuthenticatedAndOwner


class CartViewSet(viewsets.ModelViewSet):
    """
    Manage user's shopping cart.
    A user can only have one active cart.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedAndOwner]

    def get_queryset(self):
        # Only return the authenticated user's active carts
        return self.queryset.filter(user=self.request.user, is_active=True).prefetch_related(
            "items__product"
        )

    def perform_create(self, serializer):
        # Ensure a user only has one active cart
        if self.get_queryset().exists():
            raise ValueError("You already have an active cart.")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def my_cart(self, request):
        # Get or create an active cart for the user
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        cart = Cart.objects.filter(id=cart.id).prefetch_related("items__product").first()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    Manage items inside the user's cart.
    Stock validation and price snapshot are handled by the serializer.
    """
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedAndOwner]

    def get_queryset(self):
        # Limit to user's active cart
        user_cart = Cart.objects.filter(user=self.request.user, is_active=True).first()
        if user_cart:
            return self.queryset.filter(cart=user_cart).select_related("product")
        return self.queryset.none()

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Create or update a cart item.
        If the product already exists in the cart, increment quantity.
        """
        user_cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        cart_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=product,
            defaults={"quantity": quantity, "price_at_time": product.price},
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.price_at_time = product.price
            cart_item.save()
            serializer.instance = cart_item  # so serializer returns the updated item
        else:
            serializer.save(cart=user_cart)

    def perform_update(self, serializer):
        """
        Update a cart item (quantity or product).
        The serializer handles stock validation and price snapshot refresh.
        """
        serializer.save()
