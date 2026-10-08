import strawberry
from strawberry.types import Info

from app.schemas.account import Account, AccountConcept, AccountType, Concept, ConceptType
from app.schemas.company import Company
from app.schemas.role import Permission, Role, RolePermission
from app.schemas.transaction import Transaction, TransactionType
from app.schemas.user import CompanyUser
from app.services import (
    account_service,
    company_service,
    concept_service,
    role_service,
    transaction_service,
    user_service,
)


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
        actor_company_user_id: strawberry.ID,
        account_type: AccountType | None = None,
        active_only: bool | None = None,
    ) -> list[Account]:
        rows = account_service.list_accounts(
            info.context.db,
            actor_company_user_id=str(actor_company_user_id),
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
        actor_company_user_id: strawberry.ID,
        concept_type: ConceptType | None = None,
        active_only: bool | None = None,
    ) -> list[Concept]:
        rows = concept_service.list_concepts(
            info.context.db,
            actor_company_user_id=str(actor_company_user_id),
            company_id=str(company_id),
            concept_type=concept_type,
            active_only=active_only,
        )
        return [Concept.from_model(c) for c in rows]

    @strawberry.field
    def account_concepts(self, info: Info, account_id: strawberry.ID) -> list[AccountConcept]:
        rows = account_service.list_account_concepts(info.context.db, str(account_id))
        return [AccountConcept.from_model(r) for r in rows]

    @strawberry.field
    def transactions(
        self,
        info: Info,
        actor_company_user_id: strawberry.ID,
        account_id: strawberry.ID | None = None,
        transaction_type: TransactionType | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Transaction]:
        rows = transaction_service.list_transactions(
            info.context.db,
            actor_company_user_id=str(actor_company_user_id),
            account_id=str(account_id) if account_id else None,
            transaction_type=transaction_type,
            limit=limit,
            offset=offset,
        )
        return [Transaction.from_model(t) for t in rows]

    @strawberry.field
    def roles(self, info: Info, active_only: bool | None = None) -> list[Role]:
        return [Role.from_model(r) for r in role_service.list_roles(info.context.db, active_only)]

    @strawberry.field
    def role(self, info: Info, id: strawberry.ID) -> Role | None:
        model = role_service.get_role(info.context.db, str(id))
        return Role.from_model(model) if model else None

    @strawberry.field
    def permissions(self, info: Info, active_only: bool | None = None) -> list[Permission]:
        rows = role_service.list_permissions(info.context.db, active_only)
        return [Permission.from_model(p) for p in rows]

    @strawberry.field
    def role_permissions(self, info: Info, role_id: strawberry.ID) -> list[RolePermission]:
        rows = role_service.list_role_permissions(info.context.db, str(role_id))
        return [RolePermission.from_model(r) for r in rows]
