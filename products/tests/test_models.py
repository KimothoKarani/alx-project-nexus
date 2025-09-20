import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from products.models import Category, Product, Review
from users.models import User


@pytest.mark.django_db
def test_category_creation(category):
    assert category.name is not None
    assert category.slug is not None
    assert Category.objects.count() == 1


@pytest.mark.django_db
def test_category_unique_name():
    Category.objects.create(name='Unique Category', slug='unique-category')
    with pytest.raises(IntegrityError):
        Category.objects.create(name='Unique Category', slug='another-slug')


@pytest.mark.django_db
def test_category_unique_slug():
    Category.objects.create(name='Category One', slug='category-one')
    with pytest.raises(IntegrityError):
        Category.objects.create(name='Category Two', slug='category-one')


@pytest.mark.django_db
def test_nested_category(category):
    child_category = Category.objects.create(name='Child Category', slug='child-category', parent=category)
    assert child_category.parent == category
    assert category.children.count() == 1
    assert category.children.first() == child_category


@pytest.mark.django_db
def test_product_creation(product, seller_user, category):
    assert product.name is not None
    assert product.price >= 0
    assert product.stock_quantity >= 0
    assert product.category == category
    assert product.owner == seller_user
    assert Product.objects.count() == 1


@pytest.mark.django_db
def test_product_unique_name():
    Category.objects.create(name='Test Category', slug='test-category')
    User.objects.create_user(email='seller@test.com', full_name='Seller', password='pw', user_type='seller')

    Product.objects.create(
        name='Unique Product',
        slug='unique-product',
        description='Desc',
        price=10.00,
        stock_quantity=5,
        category=Category.objects.first(),
        owner=User.objects.first()
    )
    with pytest.raises(IntegrityError):
        Product.objects.create(
            name='Unique Product',  # Same name
            slug='unique-product-2',  # Different slug
            description='Desc 2',
            price=20.00,
            stock_quantity=10,
            category=Category.objects.first(),
            owner=User.objects.first()
        )


@pytest.mark.django_db
def test_product_stock_quantity_validator():
    category = Category.objects.create(name='Test Category', slug='test-category')
    owner = User.objects.create_user(email='seller@test.com', full_name='Seller', password='pw', user_type='seller')

    with pytest.raises(ValidationError):
        product = Product(
            name='Invalid Stock Product',
            slug='invalid-stock',
            description='Desc',
            price=10.00,
            stock_quantity=-1,  # Invalid
            category=category,
            owner=owner
        )
        product.full_clean()  # Triggers model validators


@pytest.mark.django_db
def test_review_creation(review, user, product):
    assert review.user == user
    assert review.product == product
    assert 1 <= review.rating <= 5
    assert Review.objects.count() == 1


@pytest.mark.django_db
def test_review_unique_user_product_constraint(user, product):
    Review.objects.create(user=user, product=product, rating=4)
    with pytest.raises(IntegrityError):  # Due to UniqueConstraint
        Review.objects.create(user=user, product=product, rating=3)


@pytest.mark.django_db
def test_review_rating_validators(user, product):
    with pytest.raises(ValidationError):
        review = Review(user=user, product=product, rating=0)
        review.full_clean()  # Rating too low

    with pytest.raises(ValidationError):
        review = Review(user=user, product=product, rating=6)
        review.full_clean()  # Rating too high