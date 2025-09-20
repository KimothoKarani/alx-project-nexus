# This file will test the API endpoints for user registration, profile, and addresses.
from http.client import responses

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User, Address
import json

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def authenticated_user_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.fixture
def seller_user_client(api_client, seller_user):
    refresh = RefreshToken.for_user(seller_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.fixture
def admin_user_client(api_client, admin_user):
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.mark.django_db
def test_user_registration(api_client):
    url = reverse('user_register')
    data = {
        'email': 'newuser@example.com',
        'full_name': 'New User',
        'password': 'password123',
        'user_type': 'customer',
    }
    response = api_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email='newuser@example.com').exists()

@pytest.mark.django_db
def test_user_profile_update(authenticated_user_client, user):
    url = reverse('user_profile_detail', kwargs={'id': user.id})
    update_name = 'Updated Full Name'
    data = {'full_name': update_name}
    response = authenticated_user_client.patch(url, data=data, format='json')
    assert response.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.full_name == update_name

@pytest.mark.django_db
def test_address_list_create(authenticated_user_client, user):
    url = reverse('address-list') # This is from DefaultRouter
    data = {
        'street_address': '456 Test Ave',
        'city': 'Sampleton',
        'zip_code': '54321',
        'country': 'Testland',
        'user': str(user.id), # Included user ID if serializer doesn't auto-assign
    }
    response = authenticated_user_client.post(url, data=data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert Address.objects.filter(user=user, street_address='456 Test Ave').exists()

    # Test listing addresses
    response = authenticated_user_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert data['count'] == 1
    assert len(data['results']) == 1
    assert data['results'][0]['street_address'] == '456 Test Ave'


@pytest.mark.django_db
def test_address_set_default(authenticated_user_client, user):
    #Create a few addresses for the user
    address1 = Address.objects.create(user=user, street_address='Addr 1', city='City A', zip_code='111', country='C1', is_default=True)
    address2 = Address.objects.create(user=user, street_address='Addr 2', city='City B', zip_code='222', country='C2')
    address3 = Address.objects.create(user=user, street_address='Addr 3', city='City C', zip_code='333', country='C3')

    url = reverse('address-set-default', kwargs={'pk': address3.id})
    data = {'address_id': str(address3.id)}
    response = authenticated_user_client.post(url, data=data, format='json')

    assert response.status_code == status.HTTP_200_OK
    address1.refresh_from_db()
    address2.refresh_from_db()
    address3.refresh_from_db()

    assert not address1.is_default
    assert not address2.is_default
    assert address3.is_default




