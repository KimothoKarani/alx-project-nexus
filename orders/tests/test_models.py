"""
Tests for Order models using Factory Boy factories
"""

import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from orders.models import Order, OrderItem, Payment
from orders.tests.factories import OrderFactory, OrderItemFactory, PaymentFactory

pytestmark = pytest.mark.django_db


class TestOrderModel:
    """Test Order model functionality using factories"""

    def test_create_order(self, user, address):
        """Test basic order creation using factory"""
        order = OrderFactory(user=user, shipping_address=address, billing_address=address)

        assert order is not None
        assert order.user == user
        assert order.status == Order.OrderStatus.PENDING
        assert order.payment_status == Order.PaymentStatus.PENDING
        assert order.total_amount == Decimal('100.00')
        assert str(order).startswith("Order #")

    def test_order_factory_variations(self):
        """Test different order factory variations"""
        pending_order = OrderFactory.create_pending()
        processing_order = OrderFactory.create_processing()
        paid_order = OrderFactory.create_paid()

        assert pending_order.status == Order.OrderStatus.PENDING
        assert processing_order.status == Order.OrderStatus.PROCESSING
        assert paid_order.payment_status == Order.PaymentStatus.PAID

    def test_order_status_choices(self):
        """Test that order status choices are valid"""
        valid_statuses = [status[0] for status in Order.OrderStatus.choices]
        expected_statuses = ['pending', 'processing', 'shipped', 'delivered', 'canceled']

        for status in expected_statuses:
            assert status in valid_statuses

    def test_order_payment_status_choices(self):
        """Test that payment status choices are valid"""
        valid_statuses = [status[0] for status in Order.PaymentStatus.choices]
        expected_statuses = ['pending', 'paid', 'failed', 'refunded']

        for status in expected_statuses:
            assert status in valid_statuses


class TestOrderItemModel:
    """Test OrderItem model functionality using factories"""

    def test_create_order_item(self):
        """Test basic order item creation using factory"""
        order_item = OrderItemFactory()

        assert order_item is not None
        assert order_item.order is not None
        assert order_item.product is not None
        assert order_item.quantity == 2
        assert order_item.price == Decimal('50.00')

    def test_order_item_factory_variations(self):
        """Test different order item factory variations"""
        single_item = OrderItemFactory.create_single()
        multiple_items = OrderItemFactory.create_multiple()
        expensive_item = OrderItemFactory.create_expensive()

        assert single_item.quantity == 1
        assert multiple_items.quantity == 5
        assert expensive_item.price == Decimal('200.00')

    def test_order_item_string_representation(self):
        """Test order item string representation"""
        order_item = OrderItemFactory()

        assert str(order_item.order.id) in str(order_item)
        assert str(order_item.product.name) in str(order_item)
        assert str(order_item.quantity) in str(order_item)

    def test_order_item_min_quantity_validation(self):
        """Test that quantity cannot be less than 1"""
        order_item = OrderItemFactory.build(quantity=0)  # Build but don't save

        with pytest.raises(ValidationError):
            order_item.full_clean()

    def test_unique_constraint_order_product(self):
        """Test that the same product can't be added twice to the same order"""
        order = OrderFactory()
        product = OrderItemFactory().product

        # Create first order item
        OrderItemFactory(order=order, product=product)

        # Try to create second order item with same product
        with pytest.raises(IntegrityError):
            OrderItemFactory(order=order, product=product)


class TestPaymentModel:
    """Test Payment model functionality using factories"""

    def test_create_payment(self):
        """Test basic payment creation using factory"""
        payment = PaymentFactory()

        assert payment is not None
        assert payment.order is not None
        assert payment.amount == Decimal('100.00')
        assert payment.currency == 'USD'
        assert payment.method == Payment.PaymentMethod.CREDIT_CARD
        assert payment.status == Payment.PaymentStatus.PENDING

    def test_payment_factory_variations(self):
        """Test different payment factory variations"""
        succeeded_payment = PaymentFactory.create_succeeded()
        failed_payment = PaymentFactory.create_failed()
        paypal_payment = PaymentFactory.create_paypal()

        assert succeeded_payment.status == Payment.PaymentStatus.SUCCEEDED
        assert failed_payment.status == Payment.PaymentStatus.FAILED
        assert paypal_payment.method == Payment.PaymentMethod.PAYPAL

    def test_payment_method_choices(self):
        """Test that payment method choices are valid"""
        valid_methods = [method[0] for method in Payment.PaymentMethod.choices]
        expected_methods = ['credit_card', 'paypal', 'mpesa', 'bank_transfer']

        for method in expected_methods:
            assert method in valid_methods

    def test_payment_status_choices(self):
        """Test that payment status choices are valid"""
        valid_statuses = [status[0] for status in Payment.PaymentStatus.choices]
        expected_statuses = ['pending', 'succeeded', 'failed', 'refunded', 'processing', 'canceled']

        for status in expected_statuses:
            assert status in valid_statuses

    def test_payment_string_representation(self):
        """Test payment string representation"""
        payment = PaymentFactory.create_succeeded()

        assert str(payment.order.id) in str(payment)
        assert 'Succeeded' in str(payment)
        assert str(payment.amount) in str(payment)

    def test_transaction_id_uniqueness(self):
        """Test that transaction IDs must be unique"""
        transaction_id = 'unique_transaction_123'
        PaymentFactory(transaction_id=transaction_id)

        # Try to create another payment with same transaction ID
        with pytest.raises(IntegrityError):
            PaymentFactory(transaction_id=transaction_id)