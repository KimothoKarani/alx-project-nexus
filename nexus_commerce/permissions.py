from rest_framework import permissions
from django.contrib.auth import get_user_model


class IsOwnerOrReadOnly(permissions.BasePermission):
    '''
    Custom permission to only allow owners of an object to edit it.
    Assumes the object has an 'owner' attribute.
    '''
    def has_object_permission(self, request, view, obj):
        # 1. SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
        if request.method in permissions.SAFE_METHODS:
            return True # allow anyone to read

        # 2. For write methods (POST, PUT, PATCH, DELETE),
        # only allow if the object's owner is the current user
        return obj.owner == request.user

class IsAuthenticatedAndOwner(permissions.BasePermission):
    """
    Custom permission:
    - User must be authenticated
    - User must own the object
    Supports models with:
      - `user` field (e.g. Cart, Address, Review)
      - `owner` field (e.g. Product)
      - `cart.user` relationship (e.g. CartItem)
      - direct user objects
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # Direct user model
        if isinstance(obj, get_user_model()):
            return obj == request.user

        # Models with `user`
        if hasattr(obj, "user"):
            return obj.user == request.user

        # Models with `owner`
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        # CartItem → check the related cart.user
        if hasattr(obj, "cart") and hasattr(obj.cart, "user"):
            return obj.cart.user == request.user

        return False
