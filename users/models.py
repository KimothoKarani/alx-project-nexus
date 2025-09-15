from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid
from phonenumber_field.modelfields import PhoneNumberField

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not password:
            raise ValueError('Superuser must have a password')
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True) # Superusers should be active by default

        if extra_fields.get("is_staff") is not True:
            raise ValueError('Superuser must have is_staff=True')

        if extra_fields.get("is_superuser") is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images', blank=True, null=True)
    user_type = models.CharField(
        max_length=20,
        choices=[("customer", "Customer"), ("seller", "Seller"), ("admin", "Admin")],
        default="customer",
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name.split(" ")[0]

    def __str__(self):
        return self.email

class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    street_address = models.CharField(max_length=255, null=False, blank=False)
    apartment_suite = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, null=False, blank=False)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, null=False, blank=False)
    country = models.CharField(max_length=255, null=False, blank=False)
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Addresses"
        unique_together = ("user", "street_address", "city", "zip_code", "country") # Prevent exact duplicate addresses for a user
        ordering = ['user', '-is_default', 'city']

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.country} ({self.user.email})"












