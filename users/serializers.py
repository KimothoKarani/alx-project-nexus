from rest_framework import serializers
from .models import User, Address


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "phone_number", "profile_image",
            "user_type", "is_active", "is_staff", "date_joined", "password",
        ]
        read_only_fields = ["id", "is_active", "is_staff", "date_joined"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
            instance.save(update_fields=["password"])
        return super().update(instance, validated_data)


class AddressSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Address
        fields = [
            "id", "user", "user_email", "street_address", "apartment_suite",
            "city", "state", "zip_code", "country", "is_default",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user_email", "created_at", "updated_at"]
        extra_kwargs = {"user": {"write_only": True}}
