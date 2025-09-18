from rest_framework import permissions

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
    '''
    Custom permission to only allow authenticated users to view/edit their own objects.
    Assumes the object has a 'user' attribute (e.g., Address, Cart, Order, Review).
    or directly refers to the request.user (e.g., UserProfile)
    '''
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(obj, permissions.get_user_model()):
            return obj == request.user

        if hasattr(obj, 'user'):
            return obj.user == request.user

        if hasattr(obj, 'owner'):
            return obj.owner == request.user

        return False
