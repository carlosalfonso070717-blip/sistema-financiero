"""Punto de entrada: FastAPI con el router de GraphQL montado en /graphql."""
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app.database import Base, engine
from app.graphql_api.context import get_context
from app.graphql_api.schema import schema
from app.models import Company  # noqa: F401  (registra las tablas)

# En un proyecto en produccion esto lo haria Alembic con migraciones.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema Financiero - API GraphQL")
app.include_router(GraphQLRouter(schema, context_getter=get_context), prefix="/graphql")


@app.get("/")
def health():
    return {"status": "ok", "graphql": "/graphql"}
