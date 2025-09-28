import graphene
from graphene_django import DjangoObjectType
from users.models import User, Address
from graphql_jwt.decorators import login_required


# --- Types ---
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name', 'phone_number', 'profile_image',
            'user_type', 'is_active', 'is_staff', 'date_joined', 'addresses'
        )


class AddressType(DjangoObjectType):
    class Meta:
        model = Address
        fields = (
            'id', 'user', 'street_address', 'apartment_suite', 'city',
            'state', 'zip_code', 'country', 'is_default', 'created_at', 'updated_at'
        )


# --- Input Types ---
class UserInput(graphene.InputObjectType):
    email = graphene.String(required=True)
    full_name = graphene.String(required=True)
    password = graphene.String(required=True)
    user_type = graphene.String(default_value="customer")
    phone_number = graphene.String()


class AddressInput(graphene.InputObjectType):
    street_address = graphene.String(required=True)
    apartment_suite = graphene.String()
    city = graphene.String(required=True)
    state = graphene.String()
    zip_code = graphene.String(required=True)
    country = graphene.String(required=True)
    is_default = graphene.Boolean(default_value=False)


# --- Mutations ---
class CreateUser(graphene.Mutation):
    class Arguments:
        input = UserInput(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input):
        try:
            # Check if user already exists
            if User.objects.filter(email=input.email).exists():
                return CreateUser(
                    success=False,
                    message="User with this email already exists."
                )

            user = User.objects.create_user(
                email=input.email,
                full_name=input.full_name,
                password=input.password,
                user_type=input.user_type,
                phone_number=input.phone_number
            )

            return CreateUser(
                user=user,
                success=True,
                message="User created successfully."
            )
        except Exception as e:
            return CreateUser(
                success=False,
                message=str(e)
            )


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        full_name = graphene.String()
        phone_number = graphene.String()
        profile_image = graphene.String()

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id, full_name=None, phone_number=None, profile_image=None):
        try:
            user = info.context.user

            # Ensure user can only update their own profile
            if str(user.id) != str(id):
                return UpdateUser(
                    success=False,
                    message="You are not authorized to update this profile."
                )

            if full_name:
                user.full_name = full_name
            if phone_number:
                user.phone_number = phone_number
            if profile_image:
                user.profile_image = profile_image

            user.save()

            return UpdateUser(
                user=user,
                success=True,
                message="Profile updated successfully."
            )
        except Exception as e:
            return UpdateUser(
                success=False,
                message=str(e)
            )


class CreateAddress(graphene.Mutation):
    class Arguments:
        input = AddressInput(required=True)

    address = graphene.Field(AddressType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, input):
        try:
            user = info.context.user

            # If setting as default, unset other defaults
            if input.is_default:
                Address.objects.filter(user=user, is_default=True).update(is_default=False)

            address = Address.objects.create(
                user=user,
                street_address=input.street_address,
                apartment_suite=input.apartment_suite,
                city=input.city,
                state=input.state,
                zip_code=input.zip_code,
                country=input.country,
                is_default=input.is_default
            )

            return CreateAddress(
                address=address,
                success=True,
                message="Address created successfully."
            )
        except Exception as e:
            return CreateAddress(
                success=False,
                message=str(e)
            )


class UpdateAddress(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)
        input = AddressInput(required=True)

    address = graphene.Field(AddressType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id, input):
        try:
            user = info.context.user

            try:
                address = Address.objects.get(pk=id, user=user)
            except Address.DoesNotExist:
                return UpdateAddress(
                    success=False,
                    message="Address not found or unauthorized."
                )

            # If setting as default, unset other defaults
            if input.is_default:
                Address.objects.filter(user=user, is_default=True).update(is_default=False)

            # Update address fields
            address.street_address = input.street_address
            address.apartment_suite = input.apartment_suite
            address.city = input.city
            address.state = input.state
            address.zip_code = input.zip_code
            address.country = input.country
            address.is_default = input.is_default

            address.save()

            return UpdateAddress(
                address=address,
                success=True,
                message="Address updated successfully."
            )
        except Exception as e:
            return UpdateAddress(
                success=False,
                message=str(e)
            )


class DeleteAddress(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id):
        try:
            user = info.context.user

            try:
                address = Address.objects.get(pk=id, user=user)
                address.delete()
                return DeleteAddress(
                    success=True,
                    message="Address deleted successfully."
                )
            except Address.DoesNotExist:
                return DeleteAddress(
                    success=False,
                    message="Address not found or unauthorized."
                )
        except Exception as e:
            return DeleteAddress(
                success=False,
                message=str(e)
            )


class SetDefaultAddress(graphene.Mutation):
    class Arguments:
        id = graphene.UUID(required=True)

    address = graphene.Field(AddressType)
    success = graphene.Boolean()
    message = graphene.String()

    @login_required
    def mutate(self, info, id):
        try:
            user = info.context.user

            try:
                address = Address.objects.get(pk=id, user=user)
            except Address.DoesNotExist:
                return SetDefaultAddress(
                    success=False,
                    message="Address not found or unauthorized."
                )

            # Unset all other defaults
            Address.objects.filter(user=user, is_default=True).update(is_default=False)

            # Set this address as default
            address.is_default = True
            address.save()

            return SetDefaultAddress(
                address=address,
                success=True,
                message="Default address set successfully."
            )
        except Exception as e:
            return SetDefaultAddress(
                success=False,
                message=str(e)
            )


# --- Queries ---
class Query(graphene.ObjectType):
    all_users = graphene.List(UserType, user_type=graphene.String())
    user_by_id = graphene.Field(UserType, id=graphene.UUID())
    me = graphene.Field(UserType)

    all_addresses = graphene.List(AddressType)
    address_by_id = graphene.Field(AddressType, id=graphene.UUID())

    @login_required
    def resolve_all_users(self, info, user_type=None):
        # Only admin/staff can see all users
        if info.context.user.is_superuser or info.context.user.is_staff:
            if user_type:
                return User.objects.filter(user_type=user_type)
            return User.objects.all()
        return User.objects.none()

    @login_required
    def resolve_user_by_id(self, info, id):
        # User can see their own profile or admin/staff can see any
        if info.context.user.is_superuser or info.context.user.is_staff or str(info.context.user.id) == str(id):
            try:
                return User.objects.get(pk=id)
            except User.DoesNotExist:
                return None
        return None

    @login_required
    def resolve_me(self, info):
        return info.context.user

    @login_required
    def resolve_all_addresses(self, info):
        return Address.objects.filter(user=info.context.user)

    @login_required
    def resolve_address_by_id(self, info, id):
        try:
            return Address.objects.get(pk=id, user=info.context.user)
        except Address.DoesNotExist:
            return None


class Mutation(graphene.ObjectType):
    # Only user-specific mutations - NO JWT mutations here
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    create_address = CreateAddress.Field()
    update_address = UpdateAddress.Field()
    delete_address = DeleteAddress.Field()
    set_default_address = SetDefaultAddress.Field()