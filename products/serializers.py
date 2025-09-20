from rest_framework import serializers
from .models import Category, Product, Review

class CategorySerializer(serializers.ModelSerializer):
    # Optionally, display children categories recursively or by their IDs
    children = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'children',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'children', 'created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    owner_email = serializers.ReadOnlyField(source='owner.email')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'price', 'stock_quantity',
            'image', 'is_available', 'created_at', 'updated_at',
            'category', 'category_name', 'owner', 'owner_email', 'sku', 'brand',
            'weight', 'dimensions'
        ]
        read_only_fields = [
            'id', 'slug', 'created_at', 'updated_at',
            'category_name', 'owner', 'owner_email'
        ]

class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'user_email', 'product', 'product_name', 'rating',
            'comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_email', 'product', 'product_name', 'created_at', 'updated_at']


    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5 stars")
        return value

