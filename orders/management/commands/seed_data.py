import random
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User, Address
from products.models import Category, Product, Review
from carts.models import Cart, CartItem
from orders.models import Order, OrderItem, Payment


class Command(BaseCommand):
    help = "Seed database with test data (users, products, orders, etc.)"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # --- Clean old data (optional) ---
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        Review.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Address.objects.all().delete()
        User.objects.all().delete()

        # --- Helpers ---
        def random_price(low=10, high=2000):
            return Decimal(str(random.randint(low, high))) + Decimal("0.99")

        cities = [
            ("New York", "NY", "10001"),
            ("Los Angeles", "CA", "90001"),
            ("Chicago", "IL", "60601"),
            ("Houston", "TX", "77001"),
            ("Phoenix", "AZ", "85001"),
        ]

        # --- Users ---
        sellers = []
        for i in range(1, 6):
            sellers.append(
                User.objects.create_user(
                    email=f"seller{i}@example.com",
                    password="password123",
                    full_name=f"Seller {i}",
                    user_type="seller"
                )
            )

        customers = []
        for i in range(1, 11):
            customers.append(
                User.objects.create_user(
                    email=f"customer{i}@example.com",
                    password="password123",
                    full_name=f"Customer {i}",
                    user_type="customer"
                )
            )

        # --- Addresses ---
        for cust in customers:
            city, state, zip_code = random.choice(cities)
            Address.objects.create(
                user=cust,
                street_address=f"{random.randint(100, 999)} Main St",
                city=city,
                state=state,
                zip_code=zip_code,
                country="USA",
                is_default=True
            )

        # --- Categories ---
        categories = []
        for name in [
            "Electronics", "Clothing", "Books", "Home",
            "Sports", "Beauty", "Toys", "Automotive", "Food", "Music"
        ]:
            categories.append(
                Category.objects.create(
                    name=name,
                    slug=name.lower(),
                    description=f"{name} category",
                )
            )

        # --- Products ---
        products = []
        for i in range(1, 21):
            cat = random.choice(categories)
            owner = random.choice(sellers)
            products.append(
                Product.objects.create(
                    name=f"Product {i}",
                    slug=f"product-{i}",
                    description=f"Description for product {i}",
                    price=random_price(),
                    stock_quantity=random.randint(5, 100),
                    category=cat,
                    owner=owner,
                    is_available=True
                )
            )

        # --- Carts + CartItems ---
        for cust in customers[:10]:
            cart = Cart.objects.create(user=cust)
            for _ in range(random.randint(1, 3)):
                prod = random.choice(products)
                CartItem.objects.create(
                    cart=cart,
                    product=prod,
                    quantity=random.randint(1, 3),
                    price_at_time=prod.price
                )

        # --- Orders + Items + Payments ---
        for cust in customers[:5]:
            addr = cust.addresses.first()
            order = Order.objects.create(
                user=cust,
                shipping_address=addr,
                billing_address=addr,
                status=random.choice([Order.OrderStatus.PENDING, Order.OrderStatus.PROCESSING]),
                total_amount=Decimal("0.00"),
                payment_status=Order.PaymentStatus.PENDING,
            )
            total = Decimal("0.00")
            for _ in range(random.randint(1, 3)):
                prod = random.choice(products)
                qty = random.randint(1, 2)
                OrderItem.objects.create(
                    order=order,
                    product=prod,
                    quantity=qty,
                    price=prod.price
                )
                total += prod.price * qty
            order.total_amount = total
            order.save()

            Payment.objects.create(
                order=order,
                amount=total,
                method=random.choice(["credit_card", "paypal", "mpesa"]),
                transaction_id=str(uuid.uuid4()),
                status=random.choice(["succeeded", "pending", "failed"])
            )

        # --- Reviews ---
        for _ in range(20):
            cust = random.choice(customers)
            prod = random.choice(products)
            Review.objects.get_or_create(
                user=cust,
                product=prod,
                defaults={
                    "rating": random.randint(1, 5),
                    "comment": f"Review by {cust.full_name} on {prod.name}"
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Database seeded with test data!"))
