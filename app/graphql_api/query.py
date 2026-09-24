import strawberry
from strawberry.types import Info

from app.schemas.account import Account, AccountConcept, AccountType, Concept, ConceptType
from app.schemas.company import Company
from app.schemas.user import CompanyUser
from app.services import account_service, company_service, concept_service, user_service


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

    @strawberry.field
    def accounts(
        self,
        info: Info,
        company_id: strawberry.ID,
        account_type: AccountType | None = None,
        active_only: bool | None = None,
    ) -> list[Account]:
        rows = account_service.list_accounts(
            info.context.db,
            company_id=str(company_id),
            account_type=account_type,
            active_only=active_only,
        )
        return [Account.from_model(a) for a in rows]

    @strawberry.field
    def concepts(
        self,
        info: Info,
        company_id: strawberry.ID,
        concept_type: ConceptType | None = None,
        active_only: bool | None = None,
    ) -> list[Concept]:
        rows = concept_service.list_concepts(
            info.context.db,
            company_id=str(company_id),
            concept_type=concept_type,
            active_only=active_only,
        )
        return [Concept.from_model(c) for c in rows]

    @strawberry.field
    def account_concepts(self, info: Info, account_id: strawberry.ID) -> list[AccountConcept]:
        rows = account_service.list_account_concepts(info.context.db, str(account_id))
        return [AccountConcept.from_model(r) for r in rows]
