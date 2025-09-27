import graphene
from graphene_django import DjangoObjectType
from products.models import Category, Product, Review
from graphql_jwt.decorators import login_required
from django.db.models import Avg, Q


# --- Types ---
class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description', 'parent', 'children',
            'created_at', 'updated_at'
        )


class ProductType(DjangoObjectType):
    average_rating = graphene.Float()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'description', 'price', 'stock_quantity',
            'image', 'is_available', 'created_at', 'updated_at',
            'category', 'owner', 'sku', 'brand', 'weight', 'dimensions'
        )

    def resolve_average_rating(self, info):
        if hasattr(self, 'average_rating'):
            return self.average_rating
        return self.reviews.aggregate(Avg('rating'))['rating__avg']


class ReviewType(DjangoObjectType):
    class Meta:
        model = Review
        fields = (
            'id', 'user', 'product', 'rating', 'comment', 'created_at', 'updated_at'
        )


# --- Input Types ---
class CategoryInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    slug = graphene.String(required=True)
    description = graphene.String()
    parent_id = graphene.UUID()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    slug = graphene.String(required=True)
    description = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock_quantity = graphene.Int(required=True)
    image = graphene.String()
    is_available = graphene.Boolean(default_value=True)
    category_id = graphene.UUID(required=True)
    sku = graphene.String()
    brand = graphene.String()
    weight = graphene.Decimal()
    dimensions = graphene.String()


class ReviewInput(graphene.InputObjectType):
    product_id = graphene.UUID(required=True)
    rating = graphene.Int(required=True)
    comment = graphene.String()


# --- Queries ---
class Query(graphene.ObjectType):
    all_categories = graphene.List(CategoryType, name=graphene.String(), slug=graphene.String())
    category_by_slug = graphene.Field(CategoryType, slug=graphene.String(required=True))

    all_products = graphene.List(
        ProductType,
        name=graphene.String(),
        category_slug=graphene.String(),
        min_price=graphene.Decimal(),
        max_price=graphene.Decimal(),
        is_available=graphene.Boolean(),
        search=graphene.String(),
        owner_id=graphene.UUID(),
        ordering=graphene.String(),
    )
    product_by_slug = graphene.Field(ProductType, slug=graphene.String(required=True))

    all_reviews = graphene.List(ReviewType, product_slug=graphene.String(), user_id=graphene.UUID())
    review_by_id = graphene.Field(ReviewType, id=graphene.UUID(required=True))

    def resolve_all_categories(self, info, name=None, slug=None):
        queryset = Category.objects.all()
        if name:
            queryset = queryset.filter(name__icontains=name)
        if slug:
            queryset = queryset.filter(slug=slug)
        return queryset

    def resolve_category_by_slug(self, info, slug):
        try:
            return Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            return None

    def resolve_all_products(self, info, name=None, category_slug=None, min_price=None, max_price=None,
                             is_available=None, search=None, owner_id=None, ordering=None):
        queryset = Product.objects.annotate(average_rating=Avg('reviews__rating')).all()

        if name:
            queryset = queryset.filter(name__icontains=name)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available)
        if owner_id:
            queryset = queryset.filter(owner__id=owner_id)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__icontains=search) |
                Q(sku__icontains=search)
            )
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def resolve_product_by_slug(self, info, slug):
        try:
            return Product.objects.annotate(average_rating=Avg('reviews__rating')).get(slug=slug)
        except Product.DoesNotExist:
            return None

    def resolve_all_reviews(self, info, product_slug=None, user_id=None):
        queryset = Review.objects.all()
        if product_slug:
            queryset = queryset.filter(product__slug=product_slug)
        if user_id:
            queryset = queryset.filter(user__id=user_id)
        return queryset

    def resolve_review_by_id(self, info, id):
        try:
            return Review.objects.get(pk=id)
        except Review.DoesNotExist:
            return None


# --- Mutations ---
class CreateCategory(graphene.Mutation):
    class Arguments:
        input = CategoryInput(required=True)

    category = graphene.Field(CategoryType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, input):
        if not info.context.user.is_staff and not info.context.user.is_superuser:
            return CreateCategory(
                success=False,
                message="Only staff/superusers can create categories."
            )

        try:
            parent = None
            if input.parent_id:
                try:
                    parent = Category.objects.get(pk=input.parent_id)
                except Category.DoesNotExist:
                    return CreateCategory(
                        success=False,
                        message="Parent category not found."
                    )

            # Check if slug already exists
            if Category.objects.filter(slug=input.slug).exists():
                return CreateCategory(
                    success=False,
                    message="Category with this slug already exists."
                )

            category = Category.objects.create(
                name=input.name,
                slug=input.slug,
                description=input.description,
                parent=parent
            )

            return CreateCategory(
                category=category,
                success=True,
                message="Category created successfully."
            )
        except Exception as e:
            return CreateCategory(
                success=False,
                message=str(e)
            )


class UpdateCategory(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        input = CategoryInput(required=True)

    category = graphene.Field(CategoryType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id, input):
        if not info.context.user.is_staff and not info.context.user.is_superuser:
            return UpdateCategory(
                success=False,
                message="Only staff/superusers can update categories."
            )

        try:
            category = Category.objects.get(pk=id)
        except Category.DoesNotExist:
            return UpdateCategory(
                success=False,
                message="Category not found."
            )

        try:
            # Check if slug is being changed and if it already exists
            if input.slug != category.slug and Category.objects.filter(slug=input.slug).exists():
                return UpdateCategory(
                    success=False,
                    message="Category with this slug already exists."
                )

            parent = None
            if input.parent_id:
                try:
                    parent = Category.objects.get(pk=input.parent_id)
                    # Prevent circular parent relationships
                    if parent == category:
                        return UpdateCategory(
                            success=False,
                            message="Category cannot be its own parent."
                        )
                except Category.DoesNotExist:
                    return UpdateCategory(
                        success=False,
                        message="Parent category not found."
                    )

            category.name = input.name
            category.slug = input.slug
            category.description = input.description
            category.parent = parent
            category.save()

            return UpdateCategory(
                category=category,
                success=True,
                message="Category updated successfully."
            )
        except Exception as e:
            return UpdateCategory(
                success=False,
                message=str(e)
            )


class DeleteCategory(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id):
        if not info.context.user.is_staff and not info.context.user.is_superuser:
            return DeleteCategory(
                success=False,
                message="Only staff/superusers can delete categories."
            )

        try:
            category = Category.objects.get(pk=id)

            # Check if category has products
            if category.products.exists():
                return DeleteCategory(
                    success=False,
                    message="Cannot delete category that has products. Move or delete the products first."
                )

            # Check if category has children
            if category.children.exists():
                return DeleteCategory(
                    success=False,
                    message="Cannot delete category that has subcategories. Delete the subcategories first."
                )

            category.delete()
            return DeleteCategory(
                success=True,
                message="Category deleted successfully."
            )
        except Category.DoesNotExist:
            return DeleteCategory(
                success=False,
                message="Category not found."
            )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, input):
        if info.context.user.user_type != 'seller':
            return CreateProduct(
                success=False,
                message="Only sellers can create products."
            )

        try:
            try:
                category = Category.objects.get(pk=input.category_id)
            except Category.DoesNotExist:
                return CreateProduct(
                    success=False,
                    message="Category not found."
                )

            # Check if slug already exists
            if Product.objects.filter(slug=input.slug).exists():
                return CreateProduct(
                    success=False,
                    message="Product with this slug already exists."
                )

            # Check if SKU already exists
            if input.sku and Product.objects.filter(sku=input.sku).exists():
                return CreateProduct(
                    success=False,
                    message="Product with this SKU already exists."
                )

            product = Product.objects.create(
                owner=info.context.user,
                category=category,
                name=input.name,
                slug=input.slug,
                description=input.description,
                price=input.price,
                stock_quantity=input.stock_quantity,
                image=input.image,
                is_available=input.is_available,
                sku=input.sku,
                brand=input.brand,
                weight=input.weight,
                dimensions=input.dimensions
            )

            return CreateProduct(
                product=product,
                success=True,
                message="Product created successfully."
            )
        except Exception as e:
            return CreateProduct(
                success=False,
                message=str(e)
            )


class UpdateProduct(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id, input):
        try:
            product = Product.objects.get(pk=id, owner=info.context.user)
        except Product.DoesNotExist:
            return UpdateProduct(
                success=False,
                message="Product not found or unauthorized."
            )

        try:
            # Check if category is being changed
            if input.category_id != str(product.category.id):
                try:
                    category = Category.objects.get(pk=input.category_id)
                    product.category = category
                except Category.DoesNotExist:
                    return UpdateProduct(
                        success=False,
                        message="Category not found."
                    )

            # Check if slug is being changed and if it already exists
            if input.slug != product.slug and Product.objects.filter(slug=input.slug).exists():
                return UpdateProduct(
                    success=False,
                    message="Product with this slug already exists."
                )

            # Check if SKU is being changed and if it already exists
            if input.sku and input.sku != product.sku and Product.objects.filter(sku=input.sku).exists():
                return UpdateProduct(
                    success=False,
                    message="Product with this SKU already exists."
                )

            # Update product fields
            product.name = input.name
            product.slug = input.slug
            product.description = input.description
            product.price = input.price
            product.stock_quantity = input.stock_quantity
            product.image = input.image
            product.is_available = input.is_available
            product.sku = input.sku
            product.brand = input.brand
            product.weight = input.weight
            product.dimensions = input.dimensions

            product.save()

            return UpdateProduct(
                product=product,
                success=True,
                message="Product updated successfully."
            )
        except Exception as e:
            return UpdateProduct(
                success=False,
                message=str(e)
            )


class DeleteProduct(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id):
        try:
            product = Product.objects.get(pk=id, owner=info.context.user)

            # Check if product has orders
            if product.order_items.exists():
                return DeleteProduct(
                    success=False,
                    message="Cannot delete product that has been ordered. Archive it instead."
                )

            product.delete()
            return DeleteProduct(
                success=True,
                message="Product deleted successfully."
            )
        except Product.DoesNotExist:
            return DeleteProduct(
                success=False,
                message="Product not found or unauthorized."
            )


class CreateReview(graphene.Mutation):
    class Arguments:
        input = ReviewInput(required=True)

    review = graphene.Field(ReviewType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, input):
        if Review.objects.filter(user=info.context.user, product_id=input.product_id).exists():
            return CreateReview(
                success=False,
                message="You have already reviewed this product."
            )

        try:
            product = Product.objects.get(pk=input.product_id)
        except Product.DoesNotExist:
            return CreateReview(
                success=False,
                message="Product not found."
            )

        try:
            # Validate rating
            if input.rating < 1 or input.rating > 5:
                return CreateReview(
                    success=False,
                    message="Rating must be between 1 and 5."
                )

            review = Review.objects.create(
                user=info.context.user,
                product=product,
                rating=input.rating,
                comment=input.comment
            )

            return CreateReview(
                review=review,
                success=True,
                message="Review created successfully."
            )
        except Exception as e:
            return CreateReview(
                success=False,
                message=str(e)
            )


class UpdateReview(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        input = ReviewInput(required=True)

    review = graphene.Field(ReviewType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id, input):
        try:
            review = Review.objects.get(pk=id, user=info.context.user)
        except Review.DoesNotExist:
            return UpdateReview(
                success=False,
                message="Review not found or unauthorized."
            )

        try:
            # Validate rating
            if input.rating < 1 or input.rating > 5:
                return UpdateReview(
                    success=False,
                    message="Rating must be between 1 and 5."
                )

            # Check if product is being changed
            if input.product_id != str(review.product.id):
                try:
                    product = Product.objects.get(pk=input.product_id)
                    review.product = product
                except Product.DoesNotExist:
                    return UpdateReview(
                        success=False,
                        message="Product not found."
                    )

            review.rating = input.rating
            review.comment = input.comment
            review.save()

            return UpdateReview(
                review=review,
                success=True,
                message="Review updated successfully."
            )
        except Exception as e:
            return UpdateReview(
                success=False,
                message=str(e)
            )


class DeleteReview(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id):
        try:
            review = Review.objects.get(pk=id, user=info.context.user)
            review.delete()
            return DeleteReview(
                success=True,
                message="Review deleted successfully."
            )
        except Review.DoesNotExist:
            return DeleteReview(
                success=False,
                message="Review not found or unauthorized."
            )


class Mutation(graphene.ObjectType):
    create_category = CreateCategory.Field()
    update_category = UpdateCategory.Field()
    delete_category = DeleteCategory.Field()

    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()
    delete_product = DeleteProduct.Field()

    create_review = CreateReview.Field()
    update_review = UpdateReview.Field()
    delete_review = DeleteReview.Field()