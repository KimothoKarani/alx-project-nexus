import pytest
import uuid
from django.contrib.auth import get_user_model
from users.models import Address

User = get_user_model()

@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create_user(
        email='test@example.com',
        full_name='Test User',
        password='jb2J£9ZS)O8^'
    )

    assert user.email == 'test@example.com'
    assert user.full_name == 'Test User'
    assert user.check_password('jb2J£9ZS)O8^')
    assert not user.is_staff
    assert not user.is_superuser
    assert user.is_active

@pytest.mark.django_db
def test_superuser_creation():
    admin_user = User.objects.create_superuser(
        email='admin@example.com',
        full_name='Admin User',
        password='Admin_jb2J£9ZS)O8^'
    )

    assert admin_user.email == 'admin@example.com'
    assert admin_user.full_name == 'Admin User'
    assert admin_user.is_staff
    assert admin_user.is_superuser
    assert admin_user.is_active

@pytest.mark.django_db
def test_address_creation(user):
    # 1. Create an address for the test user
    address = Address.objects.create(
        user=user,
        street_address='123 Test St',
        city='Testville',
        zip_code='12345',
        country='Testland',
    )

    # 2. Try to create a *duplicate* address for the same user
    with pytest.raises(Exception):  # expect an error here. The Address model has a uniqueness constraint
        Address.objects.create(
            user=user,
            street_address='123 Test St',
            apartment_suite='Apt 1',
            city='Testville',
            zip_code='12345',
            country='Testland',
        )
