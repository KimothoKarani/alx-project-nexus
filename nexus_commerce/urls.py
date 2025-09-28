"""
URL configuration for nexus_commerce project.
"""

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# For swagger/OpenAPI Documentation
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from graphene_django.views import GraphQLView
from nexus_commerce.schema import schema
from .health import health_check


# Swagger/OpenAPI Schema View configuration with JWT
schema_view = get_schema_view(
    openapi.Info(
        title="Nexus Commerce API",
        default_version='v1',
        description="""
A comprehensive, production-ready e-commerce backend API built with Django REST Framework and GraphQL.

## Authentication

This API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

### Authentication Flow:
1. **Register a new user**: `POST /api/v1/users/register/`
2. **Obtain JWT tokens**: `POST /api/token/` with email and password
3. **Authorize requests**: Include `Authorization: Bearer <your_access_token>` header

## API Features

### REST API Endpoints:
- **User Management**: Registration, profiles, addresses
- **Product Catalog**: Products, categories, reviews with advanced filtering
- **Shopping Cart**: Persistent cart with session management
- **Order Processing**: Complete order lifecycle with payments

### GraphQL Endpoint:
- **Single endpoint**: `/graphql/`
- **Flexible queries**: Request exactly the data you need

## Quick Start

1. Register a user
2. Get JWT tokens from `/api/token/`
3. Explore endpoints with proper authentication
4. Use GraphQL for complex data relationships

## Documentation Links
- **REST API**: This Swagger documentation
- **GraphQL**: Interactive playground at `/graphql/`
        """,
        terms_of_service="https://www.nexuscommerce.com/terms/",
        contact=openapi.Contact(
            name="Nexus Commerce Support",
            email="support@nexuscommerce.com",
            url="https://github.com/KimothoKarani/alx-project-nexus"
        ),
        license=openapi.License(
            name="BSD License",
            url="https://opensource.org/licenses/BSD-3-Clause"
        ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Authentication Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # GraphQL Endpoint
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),

    # Health check endpoint for Render/K8s/etc.
    path("healthz", health_check),

    # API Endpoints for the application
    path('api/v1/users/', include('users.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/carts/', include('carts.urls')),
    path('api/v1/orders/', include('orders.urls')),

    # 👇 Redirect root to Swagger (maintains your existing URL structure)
    path("", lambda request: HttpResponseRedirect("/swagger/")),

    # Swagger UI and RedDoc Documentation URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/',
         schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]