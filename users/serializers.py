from rest_framework import serializers
from .models import User, Address

class UserSerializer(serializers.ModelSerializer):
    # Passwords should not be read directly. For creating/updating, we handle it separately
    password = serializers.CharField(write_only=True, required=False) # Password is optional for updates

    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone_number', 'profile_image',
            'user_type', 'is_active', 'is_staff', 'date_joined', 'password'
        ]
        read_only_fields = ['id', 'is_active', 'is_staff', 'date_joined'] # These fields are not set by user

        def create(self, validated_data):
            # Extract password and create user
            password = validated_data.pop('password', None)
            user = User.objects.create_user(**validated_data)
            if password:
                user.set_password(password)
                user.save()
            return user

        def update(self, instance, validated_data):
            # We will handle password update separately if provided
            password = validated_data.pop('password', None)
            if password:
                instance.set_password(password)

            # Update the other fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance

class AddressSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Address
        fields = [
            'id', 'user', 'user_email', 'street_address', 'apartment_suite',
            'city', 'state', 'zip_code', 'country', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_email', 'created_at', 'updated_at']
        extra_kwargs = {
            'user': {'write_only': True}, # User should be set by view based on authenticated user
        }