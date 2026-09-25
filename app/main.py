from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.database import Base, engine
from app.graphql_api.context import get_context
from app.graphql_api.schema import schema
from app.models import (  # noqa: F401
    Account,
    AccountConcept,
    Company,
    CompanyUser,
    Concept,
    Transaction,
    User,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema Financiero - API GraphQL")
app.include_router(GraphQLRouter(schema, context_getter=get_context), prefix="/graphql")


@app.get("/")
def health():
    return {"status": "ok", "graphql": "/graphql"}
