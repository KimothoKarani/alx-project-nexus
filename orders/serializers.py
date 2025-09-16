from rest_framework import serializers
from .models import Order, OrderItem, Payment
from users.serializers import AddressSerializer # for nested address representation
from products.serializers import ProductSerializer # for nested product representation

class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(read_only=True)
    # product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'product_detail', 'quantity', 'price'
        ]
        read_only_fields = ['id', 'product_detail']
        extra_kwargs = {
            'order': {'write_only': True},
            'product': {'write_only': True}
        }

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'status'] # Status handled by payment gateway callback
        extra_kwargs = {
            'order': {'write_only': True} # Order set by the view
        }

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSerializer(read_only=True) # One-to-one relationship
    user_email = serializers.ReadOnlyField(source='user.email')
    shipping_address_detail = AddressSerializer(read_only=True, source='shipping_address')
    billing_address_detail = AddressSerializer(read_only=True, source='billing_address')

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'shipping_address', 'shipping_address_detail',
            'billing_address', 'billing_address_detail', 'status', 'total_amount',
            'payment_status', 'created_at', 'updated_at', 'items', 'payment'
        ]
        read_only_fields = [
            'id', 'user_email', 'status', 'total_amount', 'payment_status',
            'created_at', 'updated_at', 'items', 'payment',
            'shipping_address_detail', 'billing_address_detail'
        ]
        extra_kwargs = {
            'user': {'write_only': True}, # User set by the view
            'shipping_address': {'write_only': True, 'required': False}, # ID for setting address
            'billing_address': {'write_only': True} # ID for setting address
        }

    # override create to handle nested OrderItems and Payment
    # def create(self, validated_data):
    #     items_data = validated_data.pop('items', [])
    #     payment_data = validated_data.pop('payment', None)
    #     order = Order.objects.create(**validated_data)
    #     for item_data in items_data:
    #         OrderItem.objects.create(order=order, **item_data)
    #     if payment_data:
    #         Payment.objects.create(order=order, **payment_data)
    #     return order