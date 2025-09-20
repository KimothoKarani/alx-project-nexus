from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework import status
from carts.models import Cart, CartItem
from products.models import Product
from users.tests.factories import UserFactory


@pytest.mark.django_db
def test_my_cart_get_or_create(authenticated_user_client, user):
    url = reverse('cart-my-cart')
    response = authenticated_user_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['user_email'] == user.email
    assert Cart.objects.filter(user=user, is_active=True).exists()

    # Ensure it doesn't create a new cart if one already exists
    response = authenticated_user_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert Cart.objects.filter(user=user, is_active=True).count() == 1


@pytest.mark.django_db
def test_my_cart_unauthenticated(api_client):
    url = reverse('cart-my-cart')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_add_item_to_cart(authenticated_user_client, user, product):
    url = reverse('cart_item-list')
    data = {
        'product': product.id,
        'quantity': 1
    }

    initial_stock = product.stock_quantity

    response = authenticated_user_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert CartItem.objects.filter(cart__user=user, product=product, quantity=1).exists()
    assert Cart.objects.filter(user=user, is_active=True).exists()

    cart_item = CartItem.objects.get(cart__user=user, product=product)
    assert cart_item.price_at_time == product.price
    assert product.stock_quantity == initial_stock  # Stock not modified at this layer


@pytest.mark.django_db
def test_add_item_to_cart_existing_product_updates_quantity(authenticated_user_client, user, product):
    cart = Cart.objects.create(user=user, is_active=True)
    CartItem.objects.create(cart=cart, product=product, quantity=1, price_at_time=product.price)

    url = reverse('cart_item-list')
    data = {
        'product': product.id,
        'quantity': 2
    }

    response = authenticated_user_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert CartItem.objects.filter(cart__user=user, product=product).count() == 1

    cart_item = CartItem.objects.get(cart__user=user, product=product)
    assert cart_item.quantity == 3  # 1 + 2


@pytest.mark.django_db
def test_add_item_to_cart_not_enough_stock(authenticated_user_client, user, product):
    product.stock_quantity = 5
    product.save()

    url = reverse('cart_item-list')
    data = {
        'product': product.id,
        'quantity': 10
    }

    response = authenticated_user_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only" in response.data["quantity"][0]
    assert not CartItem.objects.filter(cart__user=user, product=product).exists()


@pytest.mark.django_db
def test_update_cart_item_quantity(authenticated_user_client, cart_item):
    url = reverse('cart_item-detail', kwargs={'pk': cart_item.id})
    updated_quantity = 3
    data = {'quantity': updated_quantity}
    response = authenticated_user_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK

    cart_item.refresh_from_db()
    assert cart_item.quantity == updated_quantity
    assert cart_item.price_at_time == cart_item.product.price


@pytest.mark.django_db
def test_update_cart_item_quantity_not_enough_stock(authenticated_user_client, cart_item):
    cart_item.product.stock_quantity = 5
    cart_item.product.save()

    url = reverse('cart_item-detail', kwargs={'pk': cart_item.id})
    data = {'quantity': 10}
    response = authenticated_user_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only" in response.data["quantity"][0]

    cart_item.refresh_from_db()
    assert cart_item.quantity != 10


@pytest.mark.django_db
def test_delete_cart_item(authenticated_user_client, cart_item):
    url = reverse('cart_item-detail', kwargs={'pk': cart_item.id})
    response = authenticated_user_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not CartItem.objects.filter(id=cart_item.id).exists()


@pytest.mark.django_db
def test_cart_item_access_other_users_cart(authenticated_user_client, product):
    other_user = UserFactory(email='other@test.com')
    other_cart = Cart.objects.create(user=other_user, is_active=True)
    other_cart_item = CartItem.objects.create(
        cart=other_cart, product=product, quantity=1, price_at_time=product.price
    )

    url = reverse('cart_item-detail', kwargs={'pk': other_cart_item.id})
    response = authenticated_user_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_cart_access_other_users_cart(authenticated_user_client):
    other_user = UserFactory(email='other@test.com')
    other_cart = Cart.objects.create(user=other_user, is_active=True)

    url = reverse('cart-detail', kwargs={'pk': other_cart.id})
    response = authenticated_user_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_cart_total_calculation(authenticated_user_client, user, product, category):
    cart = Cart.objects.create(user=user, is_active=True)
    product1 = product
    product2 = Product.objects.create(
        name="Product B", slug="product-b", description="Desc",
        price=Decimal("15.00"), stock_quantity=10,
        category=category, owner=user,
    )

    CartItem.objects.create(cart=cart, product=product1, quantity=2, price_at_time=product1.price)
    CartItem.objects.create(cart=cart, product=product2, quantity=1, price_at_time=product2.price)

    expected_total = (2 * product1.price) + (1 * product2.price)
    url = reverse('cart-my-cart')
    response = authenticated_user_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert float(response.data['cart_total']) == float(expected_total)
