from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')  # /api/v1/products/categories/
router.register(r'', ProductViewSet, basename='product')  # /api/v1/products/

urlpatterns = [
    path('', include(router.urls)),

    # Nested reviews under product
    path('<slug:product_slug>/reviews/',
         ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='product_reviews_list'),
    path('<slug:product_slug>/reviews/<uuid:pk>/',
         ReviewViewSet.as_view({'get': 'retrieve', 'put': 'update',
                                'patch': 'partial_update', 'delete': 'destroy'}),
         name='product_review_detail'),
]
