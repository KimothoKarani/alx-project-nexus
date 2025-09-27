import graphene
import graphql_jwt

import users.schema
import products.schema

class Query(
    users.schema.Query,
    products.schema.Query,
    # carts.schema.Query,
    # orders.schema.Query,
    graphene.ObjectType
):
    pass

class Mutation(
    users.schema.Mutation,  # User mutations (without JWT)
    products.schema.Mutation,  # Product mutations
    # carts.schema.Mutation,
    # orders.schema.Mutation,
    graphene.ObjectType
):
    # Define JWT mutations ONLY in the main schema to avoid conflicts
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)