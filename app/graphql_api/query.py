import strawberry
from strawberry.types import Info

from app.schemas.company import Company
from app.schemas.user import CompanyUser
from app.services import company_service, user_service


@strawberry.type
class Query:
    @strawberry.field
    def companies(self, info: Info, active_only: bool | None = None) -> list[Company]:
        rows = company_service.list_companies(info.context.db, active_only)
        return [Company.from_model(c) for c in rows]

    @strawberry.field
    def company(self, info: Info, id: strawberry.ID) -> Company | None:
        model = company_service.get_company(info.context.db, str(id))
        return Company.from_model(model) if model else None

    @strawberry.field
    def company_users(self, info: Info, company_id: strawberry.ID) -> list[CompanyUser]:
        rows = user_service.list_company_users(info.context.db, str(company_id))
        return [CompanyUser.from_model(r) for r in rows]
