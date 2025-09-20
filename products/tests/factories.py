import factory
from products.models import Category, Product, Review
from users.tests.factories import UserFactory, SellerUserFactory # Import User factories
from django.utils.text import slugify

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        # django_get_or_create = ('name',) # Ensures unique categories

    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    description = factory.Faker('text')
    parent = None # Can be overridden if nested category is needed

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
        # django_get_or_create = ('name',) # Ensures unique product names (or slug)

    name = factory.Sequence(lambda n: f'Product {n}')
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
    description = factory.Faker('paragraph')
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    stock_quantity = factory.Faker('random_int', min=10, max=100)
    is_available = True
    category = factory.SubFactory(CategoryFactory)
    owner = factory.SubFactory(SellerUserFactory) # Products are owned by sellers
    sku = factory.Sequence(lambda n: f'SKU{n:05d}')
    brand = factory.Faker('company')
    weight = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    dimensions = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)

class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review
        # django_get_or_create = ('user', 'product') # Not strictly needed with unique constraint

    user = factory.SubFactory(UserFactory)
    product = factory.SubFactory(ProductFactory)
    rating = factory.Faker('random_int', min=1, max=5)
    comment = factory.Faker('sentence')