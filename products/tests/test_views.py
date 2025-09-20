import pytest
from django.urls import reverse
from rest_framework import status
import json

from products.models import Category, Product, Review


# Assuming api_client, authenticated_user_client, seller_user_client, admin_user_client fixtures from conftest.py
# Assuming category, product, review, product_with_reviews fixtures from conftest.py
# Assuming User, Category, Product, Review models are available

@pytest.mark.django_db
def test_category_list_unauthenticated(api_client, category):
    url = reverse('category-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == category.name

@pytest.mark.django_db
def test_category_create_unauthorized(authenticated_user_client):
    url = reverse('category-list')
    data = {'name': 'New Category', 'slug': 'new-category'}
    response = authenticated_user_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN # Only admins can create

@pytest.mark.django_db
def test_category_create_admin(admin_user_client):
    url = reverse('category-list')
    data = {'name': 'Admin Category', 'slug': 'admin-category'}
    response = admin_user_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert Category.objects.filter(name='Admin Category').exists()

@pytest.mark.django_db
def test_product_list_unauthenticated(api_client, product):
    url = reverse('product-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == product.name

@pytest.mark.django_db
def test_product_create_customer_unauthorized(authenticated_user_client, category):
    url = reverse('product-list')
    data = {
        'name': 'Customer Product', 'slug': 'customer-product',
        'description': 'Desc', 'price': 10.00, 'stock_quantity': 5,
        'category': str(category.id)
    }
    response = authenticated_user_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN # Not a seller

@pytest.mark.django_db
def test_product_create_seller(seller_user_client, seller_user, category):
    url = reverse('product-list')
    data = {
        'name': 'Seller Product',
        'slug': 'seller-product',
        'description': 'Description of seller product',
        'price': 25.50,
        'stock_quantity': 20,
        'category': str(category.id)
    }
    response = seller_user_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    new_product = Product.objects.get(name='Seller Product')
    assert new_product.owner == seller_user

@pytest.mark.django_db
def test_product_update_owner(seller_user_client, product):
    url = reverse('product-detail', kwargs={'slug': product.slug})
    updated_name = 'Updated Product Name'
    data = {'name': updated_name}
    response = seller_user_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    product.refresh_from_db()
    assert product.name == updated_name

@pytest.mark.django_db
def test_product_update_non_owner_unauthorized(authenticated_user_client, product):
    url = reverse('product-detail', kwargs={'slug': product.slug})
    data = {'name': 'Attempted Update'}
    response = authenticated_user_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN # Not the owner

@pytest.mark.django_db
def test_product_filter_by_category(api_client, category, product, seller_user):
    # Create another category and product
    category2 = Category.objects.create(name='Electronics', slug='electronics')
    Product.objects.create(
        name='Laptop', slug='laptop', description='A laptop', price=1000.00,
        stock_quantity=10, category=category2, owner=seller_user
    )

    url = reverse('product-list') + f'?category__slug={category.slug}'
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert data["results"][0]["category_name"] == category.name

@pytest.mark.django_db
def test_product_search(api_client, product, seller_user, category):
    Product.objects.create(
        name='Wireless Mouse', slug='wireless-mouse', description='Comfortable mouse', price=25.00,
        stock_quantity=50, category=category, owner=seller_user
    )
    url = reverse('product-list') + '?search=mouse'
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert data["count"] == 1
    assert len(data["results"]) == 1
    assert "mouse" in data["results"][0]["name"].lower() or "mouse" in data["results"][0]["description"].lower()


@pytest.mark.django_db
def test_product_ordering_by_price(api_client, seller_user, category):
    Product.objects.create(name='Product A', slug='product-a', description='A', price=50.00, stock_quantity=10, category=category, owner=seller_user)
    Product.objects.create(name='Product B', slug='product-b', description='B', price=10.00, stock_quantity=10, category=category, owner=seller_user)
    Product.objects.create(name='Product C', slug='product-c', description='C', price=100.00, stock_quantity=10, category=category, owner=seller_user)

    url = reverse('product-list') + '?ordering=price'
    response = api_client.get(url)
    data = json.loads(response.content)
    assert response.status_code == status.HTTP_200_OK
    assert data["results"][0]['name'] == 'Product B'
    assert data["results"][1]['name'] == 'Product A'
    assert data["results"][2]['name'] == 'Product C'

@pytest.mark.django_db
def test_product_reviews_list(api_client, product_with_reviews):
    url = reverse('product_reviews_list', kwargs={'product_slug': product_with_reviews.slug})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.content)
    assert len(data) == 2
    assert 'product_name' in data[0]

@pytest.mark.django_db
@pytest.mark.django_db
def test_review_create_authenticated(authenticated_user_client, product, user):
    url = reverse('product_reviews_list', kwargs={'product_slug': product.slug})
    data = {'rating': 5, 'comment': 'Great product!'}
    response = authenticated_user_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert Review.objects.filter(user=user, product=product).exists()


@pytest.mark.django_db
def test_review_create_unauthenticated(api_client, product):
    url = reverse('product_reviews_list', kwargs={'product_slug': product.slug})
    data = {'product': str(product.id), 'rating': 5, 'comment': 'Great product!'}
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED # Requires authentication

@pytest.mark.django_db
def test_review_update_owner(authenticated_user_client, product, user):
    review = Review.objects.create(user=user, product=product, rating=3, comment='Okay')
    url = reverse('product_review_detail', kwargs={'product_slug': product.slug, 'pk': review.id})
    data = {'rating': 5, 'comment': 'Excellent!'}
    response = authenticated_user_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    review.refresh_from_db()
    assert review.rating == 5
    assert review.comment == 'Excellent!'

@pytest.mark.django_db
def test_review_update_non_owner_unauthorized(admin_user_client, product, user):
    review = Review.objects.create(user=user, product=product, rating=3, comment='Okay')
    # Admin is not the owner of this review
    url = reverse('product_review_detail', kwargs={'product_slug': product.slug, 'pk': review.id})
    data = {'rating': 1}
    response = admin_user_client.patch(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN # Not the owner