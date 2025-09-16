from django.core.validators import MinValueValidator
from django.db import models
import uuid
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_active=True),
                name='unique_active_cart_per_user'
            )
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Cart for {self.user.email if self.user else 'Anonymous User'} (ID: {self.id})"

class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    price_at_time = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Snapshot of product price when item was added to cart"
    )
    updated_at = models.DateTimeField(auto_now=True)



    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product')
        ] # A product can only appear once in a given cart
        ordering = ['product__name']
        indexes = [
            models.Index(fields=['cart', 'product']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart {self.cart.id}"