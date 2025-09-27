# Nexus Commerce - Production E-commerce Backend

A full-featured, production-ready e-commerce backend API built with Django, featuring comprehensive REST APIs, GraphQL support, real-time processing, and automated CI/CD deployment.

**API Documentation:** https://nexus-commerce.onrender.com/swagger/  
**GraphQL Playground:** https://nexus-commerce.onrender.com/graphql/

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Deployment](#deployment)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)

## Features

### Core E-commerce Functionality

- **User Management:** Registration, JWT authentication, profile management
- **Product Catalog:** Categories, products with reviews and ratings
- **Shopping Cart:** Persistent cart with session management
- **Order Processing:** Complete order lifecycle with payment integration
- **Address Management:** Multiple shipping/billing addresses

### Technical Excellence

- **Dual API Support:** Comprehensive REST API + GraphQL endpoints
- **Real-time Processing:** Celery workers with RabbitMQ for async tasks
- **Advanced Caching:** Redis-based caching with smart invalidation
- **Rate Limiting:** Comprehensive API throttling and security
- **Containerized:** Full Docker support for all environments
- **CI/CD Pipeline:** Automated testing and deployment to Render

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3.8+

### Local Development

```bash
# Clone the repository
git clone https://github.com/KimothoKarani/alx-project-nexus.git
cd alx-project-nexus

# Set up environment
cp .env.example .env

# Edit .env with your configuration

# Start all services
docker-compose up --build

# The application will be available at http://localhost:8000
```

### Production Deployment

The application is automatically deployed to Render on pushes to the main branch. Visit: https://nexus-commerce.onrender.com/swagger/

## API Documentation

### Live API Endpoints

**Base URL:** https://nexus-commerce.onrender.com/api

#### Authentication Endpoints

- `POST /api/token/` - Obtain JWT tokens
- `POST /api/token/refresh/` - Refresh JWT tokens
- `POST /api/token/verify/` - Verify JWT tokens

#### User Management

- `POST /api/v1/users/register/` - User registration
- `GET/PUT /api/v1/users/me/` - Current user profile
- `GET/PUT /api/v1/users/{id}/` - User management (admin)

#### Product Catalog

- `GET /api/v1/products/` - List products (with filtering, sorting, pagination)
- `POST /api/v1/products/` - Create product (seller only)
- `GET /api/v1/products/{slug}/` - Product details
- `GET/POST /api/v1/products/{slug}/reviews/` - Product reviews

#### Shopping Cart

- `GET /api/v1/carts/carts/my-cart/` - Get the user's cart
- `POST /api/v1/carts/cart-items/` - Add item to cart
- `PUT/DELETE /api/v1/carts/cart-items/{id}/` - Update/remove cart items

#### Order Management

- `GET /api/v1/orders/` - List user orders
- `POST /api/v1/orders/create-from-cart/` - Create order from cart
- `GET /api/v1/orders/{id}/` - Order details

#### GraphQL API

- `POST /graphql/` - GraphQL endpoint
- An interactive playground is available at `/graphql/` when `DEBUG=True`

### Example API Usage

#### User Registration

```bash
curl -X POST https://nexus-commerce.onrender.com/api/v1/users/register/ \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword123",
  "user_type": "customer"
}'
```

#### JWT Authentication

```bash
curl -X POST https://nexus-commerce.onrender.com/api/token/ \
-H "Content-Type: application/json" \
-d '{
  "email": "user@example.com",
  "password": "securepassword123"
}'
```

#### GraphQL Query

```graphql
query {
  allProducts(categorySlug: "electronics", minPrice: 100, maxPrice: 1000) {
    id
    name
    price
    averageRating
    category {
      name
      slug
    }
    reviews {
      rating
      comment
      user {
        fullName
      }
    }
  }
}
```

#### Get Specific Product:

```graphql
query {
  productBySlug(slug: "macbook-pro") {
    id
    name
    description
    price
    stockQuantity
    averageRating
    brand
    sku
    category {
      name
    }
    owner {
      fullName
      email
    }
  }
}
```

#### Create Product (Seller Only):

```graphql
mutation {
  createProduct(input: {
    name: "New Product",
    slug: "new-product",
    description: "Product description",
    price: 99.99,
    stockQuantity: 50,
    categoryId: "category-uuid-here",
    sku: "NP001",
    brand: "Example Brand"
  }) {
    success
    message
    product {
      id
      name
      slug
      price
    }
  }
}
```

## Database Schema

The application uses a comprehensive PostgreSQL database schema:

### Core Tables

**Users:** User accounts with authentication
- `id, email, full_name, password, user_type, phone_number, profile_image`

**Addresses:** User address management
- `id, user_id, street_address, city, zip_code, country, is_default`

**Categories:** Product categorization with hierarchy
- `id, name, slug, description, parent_id`

**Products:** Product catalog with inventory
- `id, name, slug, description, price, stock_quantity, category_id, owner_id`

**Carts & CartItems:** Shopping cart functionality
- `carts: id, user_id`
- `cart_items: id, cart_id, product_id, quantity`

**Orders & OrderItems:** Order management
- `orders: id, user_id, total_amount, status, payment_status`
- `order_items: id, order_id, product_id, quantity, price`

**Payments:** Payment processing
- `id, order_id, amount, method, transaction_id, status`

**Reviews:** Product reviews and ratings
- `id, user_id, product_id, rating, comment`

## Deployment

### Current Production Deployment

The application is deployed on Render.com with the following services:

- **Web Service:** Django application with Gunicorn
- **PostgreSQL:** Managed database
- **Redis:** Cache and session storage
- **Celery Workers:** Background task processing

### Auto-Deployment

The CI/CD pipeline automatically deploys to production on pushes to the main branch:

- Tests run on GitHub Actions
- Docker images built and tested
- Auto-deploy to Render.com
- Health checks verify deployment success

### Manual Deployment

```bash
# Build and deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec web_prod python manage.py migrate

# Collect static files
docker-compose exec web_prod python manage.py collectstatic --noinput
```

## Development

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Configure database, Redis, etc.

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Docker Development

```bash
# Start all services
docker-compose up --build

# Run specific services
docker-compose up db redis web

# Run commands in container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Environment Configuration

Create a `.env` file with:

```env
# Database
POSTGRES_DB=nexus_commerce_db
POSTGRES_USER=nexus_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Django
DJANGO_SECRET_KEY=your_very_secure_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@domain.com
EMAIL_HOST_PASSWORD=your_app_password
```

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests with coverage
coverage run manage.py test
coverage report

# Run specific app tests
python manage.py test users
python manage.py test products

# Run tests in Docker
docker-compose exec web python manage.py test

# Run with pytest
pytest
```

### Test Data Generation

The project uses factory-boy for generating realistic test data:

```python
# Example factory
class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
    
    name = factory.Faker('word')
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    stock_quantity = factory.Faker('random_int', min=0, max=100)
```

## Configuration

### Django Settings

The project uses environment-specific settings:

- `nexus_commerce/settings.py` - Base settings
- `nexus_commerce/settings_production.py` - Production overrides

### Key Configuration Areas

- **Caching:** Redis-based with intelligent invalidation
- **Rate Limiting:** Comprehensive API throttling
- **Security:** JWT authentication, CORS, CSRF protection
- **Performance:** Database optimization, query caching
- **Monitoring:** Health checks, structured logging

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Write tests for new functionality
- Follow PEP 8 style guide
- Update documentation for new features
- Use descriptive commit messages
- Ensure all tests pass before submitting PR

## Performance Features

### Optimization Strategies

- **Database Indexing:** Optimized queries with proper indexes
- **Query Optimization:** Strategic use of `select_related()` and `prefetch_related()`
- **Redis Caching:** Multi-level caching for frequently accessed data
- **Background Processing:** Celery for non-blocking operations
- **Static Files:** CDN-ready configuration

### Monitoring

- **Health Endpoint:** `/healthz` for service monitoring
- **Structured Logging:** JSON-formatted logs in production
- **Performance Metrics:** Response time tracking
- **Error Tracking:** Comprehensive error handling

## Troubleshooting

### Common Issues

**Database Connection Issues:**
```bash
# Check if services are running
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up -d
```

**Redis Connection Issues:**
```bash
# Test Redis connection
docker-compose exec redis redis-cli ping
```

**Celery Worker Issues:**
```bash
# Check Celery status
docker-compose exec celery_worker celery -A nexus_commerce status

# View logs
docker-compose logs celery_worker
```

### Getting Help

- Check the API Documentation
- Review the GraphQL Schema
- Examine application logs for detailed error information

## Author

**Kimotho Karani** - [GitHub Profile](https://github.com/KimothoKarani)

## Acknowledgments

- ALX Software Engineering Program for the learning foundation
- Django and Django REST Framework communities
- Render.com for excellent hosting services
- The open-source community for invaluable tools and libraries

---

**If this project helps you, please give it a star!**

[API Docs](https://nexus-commerce.onrender.com/swagger/) · [Report Issues](https://github.com/KimothoKarani/issues) · [Request Features](https://github.com/KimothoKarani/issues)

## Useful Links

- [Live API Documentation](https://nexus-commerce.onrender.com/swagger/)
- [GraphQL Playground](https://nexus-commerce.onrender.com/graphql/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Render Deployment Guide](https://render.com/docs)

---

**Production Status:** Live and actively maintained  
**Last Deployment:** Automatically deployed on main branch commits  
**API Version:** v1 (Stable)  
**Support:** Open issues for questions and support