import pytest
from rest_framework.test import APIClient
from users.tests.factories import UserFactory, SellerUserFactory, AdminUserFactory, AddressFactory
from products.tests.factories import CategoryFactory, ProductFactory, ReviewFactory
from carts.tests.factories import CartFactory, CartItemFactory
from orders.tests.factories import (
    OrderFactory, OrderItemFactory, PaymentFactory,
    OrderWithItemsFactory, PaidOrderFactory
)



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

@pytest.fixture
def active_cart_with_items(user, product):
    """Create an active cart with items for order creation testing"""
    cart = CartFactory(user=user, is_active=True)
    CartItemFactory(
        cart=cart,
        product=product,
        quantity=2,
        price_at_time=product.price
    )
    return cart


# -------------------------
# Order Fixtures
# -------------------------

@pytest.fixture
def order(user, address):
    """Create a basic order for testing using Factory"""
    return OrderFactory(user=user, shipping_address=address, billing_address=address)

@pytest.fixture
def order_with_items(user, address):
    """Create an order with items using Factory - avoid unique constraint issues"""
    order = OrderWithItemsFactory(user=user, shipping_address=address, billing_address=address)
    return order

@pytest.fixture
def paid_order(user, address):
    """Create a paid order with items using specialized Factory"""
    return PaidOrderFactory(user=user, shipping_address=address, billing_address=address)

@pytest.fixture
def processing_order(user, address):
    """Create an order in processing status"""
    return OrderFactory.create_processing(user=user, shipping_address=address, billing_address=address)

@pytest.fixture
def delivered_order(user, address):
    """Create a delivered order"""
    return OrderFactory.create_delivered(user=user, shipping_address=address, billing_address=address)

@pytest.fixture
def canceled_order(user, address):
    """Create a canceled order"""
    return OrderFactory.create_canceled(user=user, shipping_address=address, billing_address=address)

@pytest.fixture
def payment(order):
    """Create a payment for an order using Factory"""
    return PaymentFactory(order=order, amount=order.total_amount)

@pytest.fixture
def successful_payment(order):
    """Create a successful payment"""
    return PaymentFactory.create_succeeded(order=order, amount=order.total_amount)

@pytest.fixture
def failed_payment(order):
    """Create a failed payment"""
    return PaymentFactory.create_failed(order=order, amount=order.total_amount)
