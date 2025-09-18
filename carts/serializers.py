from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'cart', 'product', 'product_detail', 'quantity',
            'price_at_time', 'updated_at'
        ]
        read_only_fields = ['id', 'product_detail', 'price_at_time', 'updated_at']
        extra_kwargs = {
            'cart': {'write_only': True},
            'product': {'write_only': True},  # only IDs for product input
        }

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def validate(self, attrs):
        product = attrs.get("product")
        quantity = attrs.get("quantity")

        if product and quantity and quantity > product.stock_quantity:
            raise serializers.ValidationError(
                {"quantity": f"Only {product.stock_quantity} units of {product.name} are available."}
            )
        return attrs

    def create(self, validated_data):
        product = validated_data.get("product")
        if product:
            validated_data["price_at_time"] = product.price
        return super().create(validated_data)

    def update(self, instance, validated_data):
        product = validated_data.get("product", instance.product)
        if product:
            validated_data["price_at_time"] = product.price
        return super().update(instance, validated_data)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user_email = serializers.ReadOnlyField(source="user.email")
    cart_total = serializers.SerializerMethodField()
    cart_count = serializers.SerializerMethodField()  # new

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'user_email', 'is_active', 'items',
            'cart_total', 'cart_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_email', 'is_active', 'created_at',
            'updated_at', 'cart_total', 'cart_count'
        ]
        extra_kwargs = {
            'user': {'write_only': True}
        }

    def get_cart_total(self, obj):
        return sum(item.quantity * (item.price_at_time or item.product.price)
                   for item in obj.items.all())

    def get_cart_count(self, obj):
        return sum(item.quantity for item in obj.items.all())
