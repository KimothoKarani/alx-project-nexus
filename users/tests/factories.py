import factory
from django.contrib.auth import get_user_model
from users.models import Address

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('email',)

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    full_name = factory.Faker('name')
    password = factory.PostGenerationMethodCall('set_password', 'test-password')
    user_type = 'customer'
    is_active = True

class SellerUserFactory(UserFactory):
    user_type = 'seller'

class AdminUserFactory(UserFactory):
    email = factory.Sequence(lambda n: f'admin{n}@example.com')
    user_type = 'admin'
    is_staff = True
    is_superuser = True

class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    user = factory.SubFactory(UserFactory)
    street_address = factory.Faker('street_address')
    apartment_suite = factory.Faker('secondary_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    zip_code = factory.Faker('postcode')
    country = factory.Faker('country')
    is_default = False