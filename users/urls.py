from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, UserProfileView, AddressViewSet

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')  # /api/v1/users/addresses/

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('me/', UserProfileView.as_view(), name='user_profile_me'),
    path('<uuid:id>/', UserProfileView.as_view(), name='user_profile_detail'),
    path('', include(router.urls)),
]
