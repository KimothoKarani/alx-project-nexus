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
    help = "Seed database with realistic e-commerce test data"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding database with realistic e-commerce data...")

        if options['clear']:
            self.stdout.write("🗑️ Clearing existing data...")
            self.clear_data()

        # Seed data
        self.seed_categories()
        self.seed_users_and_addresses()
        self.seed_products()
        self.seed_reviews()
        self.seed_carts()
        self.seed_orders_and_payments()

        self.stdout.write(self.style.SUCCESS("✅ Database successfully seeded with realistic data!"))

    def clear_data(self):
        """Clear existing data in proper order to avoid foreign key constraints"""
        models_to_clear = [
            Payment, OrderItem, Order, CartItem, Cart,
            Review, Product, Category, Address, User
        ]

        for model in models_to_clear:
            model.objects.all().delete()
            self.stdout.write(f"Cleared {model.__name__}")

    def seed_categories(self):
        """Seed realistic product categories with hierarchy"""
        categories_data = [
            # Electronics
            {"name": "Electronics", "slug": "electronics", "description": "Latest gadgets and devices"},
            {"name": "Computers", "slug": "computers", "description": "Laptops, desktops and accessories",
             "parent": "electronics"},
            {"name": "Smartphones", "slug": "smartphones", "description": "Mobile phones and accessories",
             "parent": "electronics"},
            {"name": "Audio", "slug": "audio", "description": "Headphones, speakers, and audio gear",
             "parent": "electronics"},

            # Clothing
            {"name": "Clothing", "slug": "clothing", "description": "Fashion and apparel for everyone"},
            {"name": "Men's Fashion", "slug": "mens-fashion", "description": "Clothing for men", "parent": "clothing"},
            {"name": "Women's Fashion", "slug": "womens-fashion", "description": "Clothing for women",
             "parent": "clothing"},
            {"name": "Kids & Baby", "slug": "kids-baby", "description": "Clothing for children", "parent": "clothing"},

            # Home
            {"name": "Home & Garden", "slug": "home-garden", "description": "Everything for your home"},
            {"name": "Furniture", "slug": "furniture", "description": "Home and office furniture",
             "parent": "home-garden"},
            {"name": "Kitchen", "slug": "kitchen", "description": "Kitchen appliances and utensils",
             "parent": "home-garden"},
            {"name": "Home Decor", "slug": "home-decor", "description": "Decoration items for your home",
             "parent": "home-garden"},

            # Other categories
            {"name": "Books", "slug": "books", "description": "Books across all genres"},
            {"name": "Sports", "slug": "sports", "description": "Sports equipment and apparel"},
            {"name": "Beauty", "slug": "beauty", "description": "Beauty and personal care products"},
            {"name": "Toys & Games", "slug": "toys-games", "description": "Toys and games for all ages"},
        ]

        category_objects = {}

        for cat_data in categories_data:
            parent = None
            if 'parent' in cat_data:
                parent = category_objects[cat_data['parent']]
                del cat_data['parent']

            category = Category.objects.create(**cat_data)
            if parent:
                category.parent = parent
                category.save()

            category_objects[cat_data['slug']] = category

        self.stdout.write(f"✅ Created {len(categories_data)} categories")

    def seed_users_and_addresses(self):
        """Seed realistic users with proper addresses"""
        users_data = [
            # Sellers
            {
                "email": "techworld@example.com",
                "full_name": "Tech World Store",
                "user_type": "seller",
                "phone_number": "+1-555-0202"
            },
            {
                "email": "fashionhub@example.com",
                "full_name": "Fashion Hub",
                "user_type": "seller",
                "phone_number": "+1-555-0303"
            },
            {
                "email": "bookparadise@example.com",
                "full_name": "Book Paradise",
                "user_type": "seller",
                "phone_number": "+1-555-0404"
            },
            # Customers
            {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "user_type": "customer",
                "phone_number": "+1-555-1001"
            },
            {
                "email": "jane.smith@example.com",
                "full_name": "Jane Smith",
                "user_type": "customer",
                "phone_number": "+1-555-1002"
            },
            {
                "email": "mike.wilson@example.com",
                "full_name": "Mike Wilson",
                "user_type": "customer",
                "phone_number": "+1-555-1003"
            },
            {
                "email": "sarah.johnson@example.com",
                "full_name": "Sarah Johnson",
                "user_type": "customer",
                "phone_number": "+1-555-1004"
            },
            {
                "email": "david.brown@example.com",
                "full_name": "David Brown",
                "user_type": "customer",
                "phone_number": "+1-555-1005"
            }
        ]

        addresses_data = [
            # US addresses
            {
                "street_address": "123 Main Street",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "United States"
            },
            {
                "street_address": "456 Oak Avenue",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90001",
                "country": "United States"
            },
            {
                "street_address": "789 Pine Road",
                "city": "Chicago",
                "state": "IL",
                "zip_code": "60601",
                "country": "United States"
            },
            # International addresses
            {
                "street_address": "10 Downing Street",
                "city": "London",
                "state": "",
                "zip_code": "SW1A 2AA",
                "country": "United Kingdom"
            },
            {
                "street_address": "Champs-Élysées 25",
                "city": "Paris",
                "state": "",
                "zip_code": "75008",
                "country": "France"
            }
        ]

        users = {}
        for user_data in users_data:
            email = user_data.pop('email')
            user = User.objects.create_user(
                email=email,
                password="password123",  # Simple password for testing
                **user_data
            )
            users[email] = user

            # Add addresses to customers
            if user_data['user_type'] == 'customer':
                for i, addr_data in enumerate(random.sample(addresses_data, random.randint(1, 2))):
                    Address.objects.create(
                        user=user,
                        is_default=(i == 0),
                        **addr_data
                    )

        self.stdout.write(f"✅ Created {len(users_data)} users with addresses")

    def seed_products(self):
        """Seed realistic products with proper details"""
        categories = Category.objects.all()
        sellers = User.objects.filter(user_type='seller')

        products_data = [
            # Electronics
            {
                "name": "MacBook Pro 16-inch",
                "slug": "macbook-pro-16",
                "description": "Powerful laptop for professionals with M2 chip, 16GB RAM, 1TB SSD",
                "price": Decimal("2399.99"),
                "stock_quantity": 15,
                "category": categories.get(slug="computers"),
                "owner": sellers.get(email="techworld@example.com"),
                "sku": "APP-MBP16-M2",
                "brand": "Apple",
                "weight": Decimal("2.1"),
                "dimensions": "35.57 x 24.81 x 1.68 cm"
            },
            {
                "name": "iPhone 15 Pro",
                "slug": "iphone-15-pro",
                "description": "Latest iPhone with A17 Pro chip, titanium design, and advanced camera",
                "price": Decimal("999.00"),
                "stock_quantity": 25,
                "category": categories.get(slug="smartphones"),
                "owner": sellers.get(email="techworld@example.com"),
                "sku": "APP-IP15-PRO",
                "brand": "Apple",
                "weight": Decimal("0.187"),
                "dimensions": "14.65 x 7.06 x 0.80 cm"
            },
            {
                "name": "Sony WH-1000XM5 Headphones",
                "slug": "sony-wh1000xm5",
                "description": "Industry-leading noise canceling wireless headphones with 30-hour battery",
                "price": Decimal("399.99"),
                "stock_quantity": 30,
                "category": categories.get(slug="audio"),
                "owner": sellers.get(email="techworld@example.com"),
                "sku": "SON-WH1000XM5",
                "brand": "Sony",
                "weight": Decimal("0.25"),
                "dimensions": "20.0 x 26.5 x 18.5 cm"
            },
            # Clothing
            {
                "name": "Men's Casual Shirt",
                "slug": "mens-casual-shirt",
                "description": "Comfortable cotton shirt for casual wear, available in multiple colors",
                "price": Decimal("29.99"),
                "stock_quantity": 50,
                "category": categories.get(slug="mens-fashion"),
                "owner": sellers.get(email="fashionhub@example.com"),
                "sku": "FASH-MS001",
                "brand": "FashionHub",
                "weight": Decimal("0.3"),
                "dimensions": "One Size"
            },
            {
                "name": "Women's Summer Dress",
                "slug": "womens-summer-dress",
                "description": "Lightweight floral print dress perfect for summer occasions",
                "price": Decimal("45.50"),
                "stock_quantity": 35,
                "category": categories.get(slug="womens-fashion"),
                "owner": sellers.get(email="fashionhub@example.com"),
                "sku": "FASH-WD001",
                "brand": "SummerStyle",
                "weight": Decimal("0.4"),
                "dimensions": "S, M, L, XL"
            },
            # Books
            {
                "name": "The Great Gatsby",
                "slug": "great-gatsby-book",
                "description": "Classic novel by F. Scott Fitzgerald, paperback edition",
                "price": Decimal("12.99"),
                "stock_quantity": 100,
                "category": categories.get(slug="books"),
                "owner": sellers.get(email="bookparadise@example.com"),
                "sku": "BOOK-GG001",
                "brand": "Penguin Classics",
                "weight": Decimal("0.2"),
                "dimensions": "19.8 x 12.9 x 1.5 cm"
            },
            # Home
            {
                "name": "Stainless Steel Cookware Set",
                "slug": "cookware-set",
                "description": "10-piece stainless steel cookware set for modern kitchens",
                "price": Decimal("199.99"),
                "stock_quantity": 20,
                "category": categories.get(slug="kitchen"),
                "owner": sellers.get(email="techworld@example.com"),
                "sku": "HOME-CS010",
                "brand": "KitchenPro",
                "weight": Decimal("8.5"),
                "dimensions": "Various sizes"
            },
            # Add more products to reach 50+
            {
                "name": "Wireless Gaming Mouse",
                "slug": "gaming-mouse",
                "description": "High-precision wireless mouse for gaming with RGB lighting",
                "price": Decimal("79.99"),
                "stock_quantity": 40,
                "category": categories.get(slug="computers"),
                "owner": sellers.get(email="techworld@example.com"),
                "sku": "TECH-GM001",
                "brand": "GameTech",
                "weight": Decimal("0.1"),
                "dimensions": "12.5 x 6.8 x 3.9 cm"
            },
            # ... Add more products following the same pattern
        ]

        # Generate additional products to reach 50
        additional_products = 42  # We have 8 above, need 42 more
        product_names = [
            "Bluetooth Speaker", "Yoga Mat", "Desk Lamp", "Phone Case",
            "Running Shoes", "Backpack", "Coffee Maker", "Watch",
            "Sunglasses", "Water Bottle", "Notebook", "Pen Set",
            "Board Game", "Basketball", "Skincare Set", "Perfume",
            "Action Figure", "Lego Set", "Car Accessory", "Tool Kit"
        ]

        for i in range(additional_products):
            name = f"{random.choice(product_names)} {i + 1}"
            products_data.append({
                "name": name,
                "slug": f"{name.lower().replace(' ', '-')}",
                "description": f"High-quality {name} for everyday use",
                "price": Decimal(str(random.randint(10, 200))) + Decimal("0.99"),
                "stock_quantity": random.randint(5, 100),
                "category": random.choice(categories),
                "owner": random.choice(sellers),
                "sku": f"SKU{1000 + i}",
                "brand": random.choice(["Generic", "Premium", "Eco", "Pro", "Smart"]),
                "weight": Decimal(str(round(random.uniform(0.1, 5.0), 2))),
                "dimensions": f"{random.randint(5, 50)}x{random.randint(5, 50)}x{random.randint(5, 50)}cm",
                "is_available": random.choice([True, True, True, False])  # 75% available
            })

        for product_data in products_data:
            Product.objects.create(**product_data)

        self.stdout.write(f"✅ Created {len(products_data)} realistic products")

    def seed_reviews(self):
        """Seed realistic product reviews"""
        products = Product.objects.all()
        customers = User.objects.filter(user_type='customer')

        review_templates = [
            ("Excellent product! Highly recommended.", 5),
            ("Very good quality for the price.", 4),
            ("Good product, meets expectations.", 4),
            ("Average product, could be better.", 3),
            ("Not what I expected, but okay.", 3),
            ("Disappointed with the quality.", 2),
            ("Poor product, would not recommend.", 1),
        ]

        for product in products:
            # Each product gets 2-8 reviews
            num_reviews = random.randint(2, 8)
            reviewers = random.sample(list(customers), min(num_reviews, len(customers)))

            for reviewer in reviewers:
                comment, rating = random.choice(review_templates)
                Review.objects.create(
                    user=reviewer,
                    product=product,
                    rating=rating,
                    comment=f"{comment} - {reviewer.full_name}"
                )

        self.stdout.write("✅ Created realistic product reviews")

    def seed_carts(self):
        """Seed shopping carts with items"""
        customers = User.objects.filter(user_type='customer')
        products = Product.objects.filter(is_available=True)

        for customer in customers:
            # 70% of customers have active carts
            if random.random() < 0.7:
                cart, created = Cart.objects.get_or_create(user=customer)

                # Add 1-5 items to cart
                cart_products = random.sample(list(products), random.randint(1, 5))
                for product in cart_products:
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=random.randint(1, 3),
                        price_at_time=product.price
                    )

        self.stdout.write("✅ Created shopping carts with items")

    def seed_orders_and_payments(self):
        """Seed realistic orders with proper status flow"""
        customers = User.objects.filter(user_type='customer')
        products = Product.objects.all()

        order_status_flow = [
            ('pending', 'pending'),
            ('processing', 'pending'),
            ('shipped', 'paid'),
            ('delivered', 'paid'),
            ('cancelled', 'failed'),
        ]

        for customer in customers[:8]:  # First 8 customers have order history
            # Each customer has 1-4 orders
            for order_num in range(random.randint(1, 4)):
                address = customer.addresses.first()
                status, payment_status = random.choice(order_status_flow)

                order = Order.objects.create(
                    user=customer,
                    shipping_address=address,
                    billing_address=address,
                    status=status,
                    payment_status=payment_status,
                    total_amount=Decimal("0.00"),
                )

                # Add 2-5 items to order
                order_products = random.sample(list(products), random.randint(2, 5))
                total_amount = Decimal("0.00")

                for product in order_products:
                    quantity = random.randint(1, 3)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )
                    total_amount += product.price * quantity

                order.total_amount = total_amount
                order.save()

                # Create payment record
                if payment_status == 'paid':
                    Payment.objects.create(
                        order=order,
                        amount=total_amount,
                        method=random.choice(["credit_card", "paypal", "stripe"]),
                        transaction_id=str(uuid.uuid4()),
                        status="succeeded"
                    )
                elif payment_status == 'failed':
                    Payment.objects.create(
                        order=order,
                        amount=total_amount,
                        method=random.choice(["credit_card", "paypal"]),
                        transaction_id=str(uuid.uuid4()),
                        status="failed"
                    )

        self.stdout.write("✅ Created realistic orders and payments")