import pytest
from rest_framework.test import APIClient
from users.tests.factories import UserFactory, SellerUserFactory, AdminUserFactory, AddressFactory
from products.tests.factories import CategoryFactory, ProductFactory, ReviewFactory
from carts.tests.factories import CartFactory, CartItemFactory



# -------------------------
# Fixtures for users and addresses
# -------------------------
@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def seller_user():
    return SellerUserFactory()

@pytest.fixture
def admin_user():
    return AdminUserFactory()

@pytest.fixture
def address(user):
    return AddressFactory(user=user)


# -------------------------
# Fixtures for products
# -------------------------
@pytest.fixture
def category():
    return CategoryFactory()

@pytest.fixture
def product(seller_user, category):
    return ProductFactory(owner=seller_user, category=category)

@pytest.fixture
def review(user, product):
    return ReviewFactory(user=user, product=product)

@pytest.fixture
def product_with_reviews(seller_user, category, user):
    product = ProductFactory(owner=seller_user, category=category)
    ReviewFactory(user=user, product=product, rating=5)
    ReviewFactory(user=UserFactory(), product=product, rating=3)
    return product


# -------------------------
# Fixtures for API clients
# -------------------------
@pytest.fixture
def api_client():
    """Anonymous client (no authentication)"""
    return APIClient()

@pytest.fixture
def authenticated_user_client(user):
    """Client with a normal authenticated user"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def seller_user_client(seller_user):
    """Client with an authenticated seller"""
    client = APIClient()
    client.force_authenticate(user=seller_user)
    return client

@pytest.fixture
def admin_user_client(admin_user):
    """Client with an authenticated admin/superuser"""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client

# Fixtures for carts
@pytest.fixture
def cart(user):
    return CartFactory(user=user)

@pytest.fixture
def active_cart(user):
    return CartFactory(user=user, is_active=True)

@pytest.fixture
def inactive_cart(user):
    return CartFactory(user=user, is_active=False)

@pytest.fixture
def cart_item(cart, product):
    return CartItemFactory(cart=cart, product=product, price_at_time=product.price)