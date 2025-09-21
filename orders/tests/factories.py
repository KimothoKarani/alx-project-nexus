"""
Factory Boy factories for creating test data for orders, order items, and payments.
"""

import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from django.utils import timezone

from orders.models import Order, OrderItem, Payment
from users.tests.factories import UserFactory, AddressFactory
from products.tests.factories import ProductFactory

class OrderFactory(DjangoModelFactory):
    """Factory for creating Order instances"""

    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    shipping_address = factory.SubFactory(AddressFactory)
    billing_address = factory.SubFactory(AddressFactory)
    total_amount = Decimal('100.00')
    status = Order.OrderStatus.PENDING
    payment_status = Order.PaymentStatus.PENDING
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

    # Use class variables instead of Params for simple cases
    @classmethod
    def create_pending(cls, **kwargs):
        return cls.create(status=Order.OrderStatus.PENDING, payment_status=Order.PaymentStatus.PENDING, **kwargs)

    @classmethod
    def create_processing(cls, **kwargs):
        return cls.create(status=Order.OrderStatus.PROCESSING, payment_status=Order.PaymentStatus.PAID, **kwargs)

    @classmethod
    def create_shipped(cls, **kwargs):
        return cls.create(status=Order.OrderStatus.SHIPPED, payment_status=Order.PaymentStatus.PAID, **kwargs)

    @classmethod
    def create_delivered(cls, **kwargs):
        return cls.create(status=Order.OrderStatus.DELIVERED, payment_status=Order.PaymentStatus.PAID, **kwargs)

    @classmethod
    def create_canceled(cls, **kwargs):
        return cls.create(status=Order.OrderStatus.CANCELED, payment_status=Order.PaymentStatus.REFUNDED, **kwargs)

    @classmethod
    def create_paid(cls, **kwargs):
        return cls.create(payment_status=Order.PaymentStatus.PAID, **kwargs)


class OrderItemFactory(DjangoModelFactory):
    """Factory for creating OrderItem instances"""

    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 2
    price = Decimal('50.00')

    @classmethod
    def create_single(cls, **kwargs):
        return cls.create(quantity=1, **kwargs)

    @classmethod
    def create_multiple(cls, **kwargs):
        return cls.create(quantity=5, **kwargs)

    @classmethod
    def create_expensive(cls, **kwargs):
        return cls.create(price=Decimal('200.00'), **kwargs)

    @classmethod
    def create_cheap(cls, **kwargs):
        return cls.create(price=Decimal('10.00'), **kwargs)


class PaymentFactory(DjangoModelFactory):
    """Factory for creating Payment instances"""

    class Meta:
        model = Payment

    order = factory.SubFactory(OrderFactory)
    amount = Decimal('100.00')
    currency = 'USD'
    method = Payment.PaymentMethod.CREDIT_CARD
    transaction_id = factory.Sequence(lambda n: f'transaction_{n:08d}')
    reference = factory.Sequence(lambda n: f'ref_{n:06d}')
    status = Payment.PaymentStatus.PENDING
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)

    @classmethod
    def create_pending(cls, **kwargs):
        return cls.create(status=Payment.PaymentStatus.PENDING, **kwargs)

    @classmethod
    def create_succeeded(cls, **kwargs):
        return cls.create(status=Payment.PaymentStatus.SUCCEEDED, **kwargs)

    @classmethod
    def create_failed(cls, **kwargs):
        return cls.create(status=Payment.PaymentStatus.FAILED, **kwargs)

    @classmethod
    def create_refunded(cls, **kwargs):
        return cls.create(status=Payment.PaymentStatus.REFUNDED, **kwargs)

    @classmethod
    def create_processing(cls, **kwargs):
        return cls.create(status=Payment.PaymentStatus.PROCESSING, **kwargs)

    @classmethod
    def create_canceled(cls, **kwargs):
        return cls.create(status=Payment.PaymentStatus.CANCELED, **kwargs)

    @classmethod
    def create_paypal(cls, **kwargs):
        return cls.create(method=Payment.PaymentMethod.PAYPAL, **kwargs)

    @classmethod
    def create_mpesa(cls, **kwargs):
        return cls.create(method=Payment.PaymentMethod.MPESA, **kwargs)

    @classmethod
    def create_bank_transfer(cls, **kwargs):
        return cls.create(method=Payment.PaymentMethod.BANK_TRANSFER, **kwargs)


# Composite factories for common scenarios
class OrderWithItemsFactory(OrderFactory):
    """Factory that creates an order with items"""

    @factory.post_generation
    def items(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # If items are passed in, use them
            for item in extracted:
                item.order = self
                item.save()
        else:
            # Create default items with different products to avoid unique constraint
            product1 = ProductFactory()
            product2 = ProductFactory()
            OrderItemFactory.create(order=self, product=product1, quantity=1, price=Decimal('50.00'))
            OrderItemFactory.create(order=self, product=product2, quantity=1, price=Decimal('50.00'))

            # Recalculate total amount based on items
            total = sum(item.price * item.quantity for item in self.items.all())
            self.total_amount = total
            self.save()


class PaidOrderFactory(OrderWithItemsFactory):
    """Factory for creating a paid order with items"""

    status = Order.OrderStatus.PROCESSING
    payment_status = Order.PaymentStatus.PAID

    @factory.post_generation
    def payment(self, create, extracted, **kwargs):
        if not create:
            return

        # Create a successful payment for the order
        PaymentFactory.create(
            order=self,
            amount=self.total_amount,
            status=Payment.PaymentStatus.SUCCEEDED
        )