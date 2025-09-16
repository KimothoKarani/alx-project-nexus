from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer  # Import for nested product representation


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(read_only=True)  # Nested serializer to show product details

    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'product_detail', 'quantity',
            'price_at_time', 'updated_at'
        ]
        read_only_fields = ['id', 'product_detail', 'price_at_time', 'updated_at']
        extra_kwargs = {
            'cart': {'write_only': True}  # Cart should be set by the view
        }

    # Custom validation/logic can go here if needed, e.g., checking product stock
    def create(self, validated_data):
        # fetch the current product price
        product = validated_data.get('product')
        if product:
            validated_data['price_at_time'] = product.price
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Update price_at_time if product changes or stock logic warrants
        return super().update(instance, validated_data)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)  # Nested serializer for cart items
    user_email = serializers.ReadOnlyField(source='user.email')

    # Optional: calculate cart total
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'user_email', 'is_active', 'items',
            'cart_total', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_email', 'is_active', 'created_at', 'updated_at', 'cart_total']
        extra_kwargs = {
            'user': {'write_only': True}  # User should be set by the view
        }

    def get_cart_total(self, obj):
        return sum(item.quantity * (item.price_at_time or item.product.price) for item in obj.items.all())