import pytest
from users.tests.factories import UserFactory, SellerUserFactory, AdminUserFactory, AddressFactory

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