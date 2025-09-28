from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# API Documentation with drf-spectacular
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from graphene_django.views import GraphQLView
from nexus_commerce.schema import schema
from .health import health_check

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # JWT Authentication Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # GraphQL Endpoint
    path('graphql/', GraphQLView.as_view(graphiql=True, schema=schema)),

    # Health check endpoint
    path('healthz/', health_check, name='health_check'),

    # API Endpoints
    path('api/v1/users/', include('users.urls')),
    path('api/v1/products/', include('products.urls')),
    path('api/v1/carts/', include('carts.urls')),
    path('api/v1/orders/', include('orders.urls')),

    # API Schema and Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Redirect root to Swagger UI
    path('', lambda request: HttpResponseRedirect('/api/schema/swagger-ui/')),
]