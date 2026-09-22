"""Queries del schema (Dia 1)."""
import strawberry
from strawberry.types import Info

from app.schemas.company import Company
from app.services import company_service


@strawberry.type
class Query:
    @strawberry.field(description="Lista las empresas registradas.")
    def companies(self, info: Info, active_only: bool | None = None) -> list[Company]:
        db = info.context.db
        return [Company.from_model(c) for c in company_service.list_companies(db, active_only)]

    @strawberry.field(description="Devuelve una empresa o null si no existe.")
    def company(self, info: Info, id: strawberry.ID) -> Company | None:
        model = company_service.get_company(info.context.db, str(id))
        return Company.from_model(model) if model else None
