import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from carts.models import Cart, CartItem
from products.models import Product  # To interact with product stock


@pytest.mark.django_db
def test_cart_creation(user):
    cart = Cart.objects.create(user=user, is_active=True)
    assert cart.user == user
    assert cart.is_active
    assert Cart.objects.count() == 1


@pytest.mark.django_db
def test_cart_unique_active_cart_per_user_constraint(user):
    Cart.objects.create(user=user, is_active=True)
    with pytest.raises(IntegrityError):
        # Attempt to create another active cart for the same user
        Cart.objects.create(user=user, is_active=True)


@pytest.mark.django_db
def test_cart_multiple_inactive_carts_per_user(user):
    Cart.objects.create(user=user, is_active=False)
    Cart.objects.create(user=user, is_active=False)
    assert Cart.objects.filter(user=user, is_active=False).count() == 2


@pytest.mark.django_db
def test_cart_str_representation(user):
    cart = Cart.objects.create(user=user, is_active=True)
    expected = f"Cart for {user.email} (ID: {cart.id})"
    assert str(cart) == expected


@pytest.mark.django_db
def test_cart_item_creation(active_cart, product):
    initial_product_price = product.price
    cart_item = CartItem.objects.create(
        cart=active_cart,
        product=product,
        quantity=2,
        price_at_time=initial_product_price
    )
    assert cart_item.cart == active_cart
    assert cart_item.product == product
    assert cart_item.quantity == 2
    assert cart_item.price_at_time == initial_product_price
    assert CartItem.objects.count() == 1


@pytest.mark.django_db
def test_cart_item_unique_cart_product_constraint(active_cart, product):
    CartItem.objects.create(
        cart=active_cart,
        product=product,
        quantity=1,
        price_at_time=product.price
    )
    with pytest.raises(IntegrityError):
        # Attempt to add the same product to the same cart again
        CartItem.objects.create(
            cart=active_cart,
            product=product,
            quantity=1,
            price_at_time=product.price
        )


@pytest.mark.django_db
def test_cart_item_quantity_validator(active_cart, product):
    with pytest.raises(ValidationError):
        cart_item = CartItem(cart=active_cart, product=product, quantity=0)
        cart_item.full_clean()  # Quantity too low (PositiveIntegerField + MinValueValidator)

    with pytest.raises(ValidationError):
        cart_item = CartItem(cart=active_cart, product=product, quantity=-1)
        cart_item.full_clean()  # Quantity negative


@pytest.mark.django_db
def test_cart_item_str(active_cart, product):
    cart_item = CartItem.objects.create(
        cart=active_cart,
        product=product,
        quantity=3,
        price_at_time=product.price
    )
    expected = f"3 x {product.name} in cart {active_cart.id}"
    assert str(cart_item) == expected
