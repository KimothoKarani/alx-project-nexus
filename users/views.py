from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import User, Address
from .serializers import UserSerializer, AddressSerializer
from nexus_commerce.permissions import IsAuthenticatedAndOwner


# User Registration
class UserRegistrationView(generics.CreateAPIView):
    """
    Public endpoint for user registration.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


# User Profile (Retrieve, Update)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Authenticated users can view and update their own profile.
    Supports `/api/v1/users/me/` as a shortcut.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedAndOwner]
    lookup_field = "id"

    def get_object(self):
        if self.kwargs.get(self.lookup_field) == "me":
            return self.request.user
        return super().get_object()


class AddressViewSet(viewsets.ModelViewSet):
    """
    Manage user's addresses.
    Users can only manage their own addresses.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthenticatedAndOwner]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def set_default(self, request, pk=None):
        """
        Set a specific address as the default.
        Clears default flag from all other addresses.
        """
        try:
            address_to_set = self.get_queryset().get(pk=pk)
        except Address.DoesNotExist:
            return Response(
                {"detail": "Address not found or not yours"},
                status=status.HTTP_404_NOT_FOUND,
            )

        self.get_queryset().update(is_default=False)
        address_to_set.is_default = True
        address_to_set.save(update_fields=["is_default"])

        serializer = self.get_serializer(address_to_set)
        return Response(serializer.data, status=status.HTTP_200_OK)
