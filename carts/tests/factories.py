import factory
from carts.models import Cart, CartItem
from users.tests.factories import UserFactory
from products.tests.factories import ProductFactory


class CartFactory(factory.django.DjangoModelFactory):
    """Factory for Cart model"""

    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)
    is_active = True
    # created_at and updated_at are usually auto-managed by Django (auto_now_add/auto_now),
    # so no need to set them here unless we want custom values in specific tests.


class CartItemFactory(factory.django.DjangoModelFactory):
    """Factory for CartItem model"""

    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.Faker('random_int', min=1, max=5)

    @factory.lazy_attribute
    def price_at_time(self):
        # Default to the product's current price at the time of creation
        return self.product.price
