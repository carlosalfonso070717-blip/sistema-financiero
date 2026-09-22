"""Ensamblado del schema de Strawberry."""
import strawberry

from app.graphql_api.mutation import Mutation
from app.graphql_api.query import Query

schema = strawberry.Schema(query=Query, mutation=Mutation)
