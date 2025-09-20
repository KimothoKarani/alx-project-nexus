from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer
from nexus_commerce.permissions import IsOwnerOrReadOnly, IsAuthenticatedAndOwner


# ------------------------------
# Category ViewSet
# ------------------------------
class CategoryViewSet(viewsets.ModelViewSet):
    """
    Manage product categories.
    - Anyone can read.
    - Only admins/staff can create/update/delete.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"  # Use slug for SEO-friendly URLs
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        # Admin-only for unsafe methods
        if self.request.method not in permissions.SAFE_METHODS:
            return [permissions.IsAdminUser()]
        return super().get_permissions()


# ------------------------------
# Product ViewSet
# ------------------------------
class ProductViewSet(viewsets.ModelViewSet):
    """
    Manage products.
    - Anyone can view products.
    - Only authenticated sellers can create.
    - Only owner or staff can update/delete.
    """
    serializer_class = ProductSerializer
    lookup_field = "slug"

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__slug", "is_available", "brand", "owner__id"]
    search_fields = ["name", "description", "brand", "sku"]
    ordering_fields = ["name", "price", "created_at", "average_rating"]

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        return (
            Product.objects
            .annotate(average_rating=Avg("reviews__rating"))
            .select_related("category", "owner")
            .prefetch_related("reviews")
            .all()
        )

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or user.user_type != "seller":
            self.permission_denied(
                self.request,
                message="Only authenticated sellers can create products."
            )
        serializer.save(owner=user)

    def perform_update(self, serializer):
        user = self.request.user
        if not (user == serializer.instance.owner or user.is_staff or user.is_superuser):
            self.permission_denied(
                self.request,
                message="You do not have permission to edit this product."
            )
        serializer.save()

    @action(detail=True, methods=["get", "post"], url_path="reviews",
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def reviews(self, request, slug=None):
        product = self.get_object()

        if request.method == "GET":
            reviews = product.reviews.all().select_related("user")
            serializer = ReviewSerializer(reviews, many=True, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

            serializer = ReviewSerializer(
                data=request.data,
                context={"request": request, "product": product}  # pass product here
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# ------------------------------
# Review ViewSet
# ------------------------------
class ReviewViewSet(viewsets.ModelViewSet):
    """
    Manage reviews for products.
    - Anyone can read reviews.
    - Authenticated users can create.
    - Only the review owner (or staff) can edit/delete.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthenticatedAndOwner]

    def get_queryset(self):
        product_slug = self.kwargs.get("product_slug")
        if product_slug:
            return self.queryset.filter(product__slug=product_slug).select_related("user", "product")
        return self.queryset.select_related("user", "product")

    def perform_create(self, serializer):
        product_id = self.request.data.get("product")
        if Review.objects.filter(user=self.request.user, product_id=product_id).exists():
            return Response(
                {"detail": "You have already reviewed this product."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save(user=self.request.user)
