import strawberry
from strawberry.types import Info

from app.schemas.account import (
    Account,
    AccountConcept,
    AssignConceptToAccountInput,
    Concept,
    CreateAccountInput,
    CreateConceptInput,
)
from app.schemas.company import Company, CreateCompanyInput, UpdateCompanyInput
from app.schemas.role import (
    AssignPermissionToRoleInput,
    CreatePermissionInput,
    CreateRoleInput,
    Permission,
    Role,
    RolePermission,
)
from app.schemas.transaction import CreateTransactionInput, Transaction
from app.schemas.user import (
    AuthPayload,
    AssignRoleInput,
    AuthUser,
    CompanyUser,
    CompanyUserRole,
    CreateCompanyAdminInput,
    CreateCompanyUserInput,
    LoginInput,
)
from app.services import (
    account_service,
    company_service,
    concept_service,
    role_service,
    transaction_service,
    user_service,
)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_company(self, info: Info, input: CreateCompanyInput) -> Company:
        model = company_service.create_company(
            info.context.db,
            name=input.name,
            legal_name=input.legal_name,
            tax_id=input.tax_id,
            email=input.email,
            phone=input.phone,
        )
        return Company.from_model(model)

    @strawberry.mutation
    def update_company(self, info: Info, input: UpdateCompanyInput) -> Company:
        model = company_service.update_company(
            info.context.db,
            company_id=str(input.id),
            name=input.name,
            legal_name=input.legal_name,
            tax_id=input.tax_id,
            email=input.email,
            phone=input.phone,
            is_active=input.is_active,
        )
        return Company.from_model(model)

    @strawberry.mutation
    def deactivate_company(self, info: Info, id: strawberry.ID) -> Company:
        model = company_service.deactivate_company(info.context.db, str(id))
        return Company.from_model(model)

    @strawberry.mutation
    def create_company_admin(self, info: Info, input: CreateCompanyAdminInput) -> CompanyUser:
        model = user_service.create_company_admin(
            info.context.db,
            company_id=str(input.company_id),
            name=input.name,
            email=input.email,
            password=input.password,
        )
        return CompanyUser.from_model(model)

    @strawberry.mutation
    def create_company_user(self, info: Info, input: CreateCompanyUserInput) -> CompanyUser:
        model = user_service.create_company_user(
            info.context.db,
            actor_company_user_id=str(input.actor_company_user_id),
            company_id=str(input.company_id),
            name=input.name,
            email=input.email,
            password=input.password,
        )
        return CompanyUser.from_model(model)

    @strawberry.mutation
    def deactivate_company_user(
        self, info: Info, id: strawberry.ID, actor_company_user_id: strawberry.ID
    ) -> CompanyUser:
        model = user_service.deactivate_company_user(
            info.context.db,
            actor_company_user_id=str(actor_company_user_id),
            membership_id=str(id),
        )
        return CompanyUser.from_model(model)

    @strawberry.mutation
    def login(self, info: Info, input: LoginInput) -> AuthPayload:
        token, user = user_service.login(
            info.context.db, email=input.email, password=input.password
        )
        return AuthPayload(
            token=token,
            token_type="Bearer",
            user=AuthUser(id=strawberry.ID(user.id), name=user.name, email=user.email),
        )

    @strawberry.mutation
    def create_account(self, info: Info, input: CreateAccountInput) -> Account:
        model = account_service.create_account(
            info.context.db,
            actor_company_user_id=str(input.actor_company_user_id),
            company_id=str(input.company_id),
            account_type=input.account_type,
            name=input.name,
            bank_name=input.bank_name,
            account_number=input.account_number,
            clabe=input.clabe,
            card_last_digits=input.card_last_digits,
            short_description=input.short_description,
            long_description=input.long_description,
        )
        return Account.from_model(model)

    @strawberry.mutation
    def create_concept(self, info: Info, input: CreateConceptInput) -> Concept:
        model = concept_service.create_concept(
            info.context.db,
            actor_company_user_id=str(input.actor_company_user_id),
            company_id=str(input.company_id),
            concept_type=input.concept_type,
            name=input.name,
            short_description=input.short_description,
            long_description=input.long_description,
        )
        return Concept.from_model(model)

    @strawberry.mutation
    def assign_concept_to_account(
        self, info: Info, input: AssignConceptToAccountInput
    ) -> AccountConcept:
        model = account_service.assign_concept_to_account(
            info.context.db,
            actor_company_user_id=str(input.actor_company_user_id),
            account_id=str(input.account_id),
            concept_id=str(input.concept_id),
        )
        return AccountConcept.from_model(model)

    @strawberry.mutation
    def remove_concept_from_account(
        self,
        info: Info,
        account_id: strawberry.ID,
        concept_id: strawberry.ID,
        actor_company_user_id: strawberry.ID,
    ) -> bool:
        return account_service.remove_concept_from_account(
            info.context.db,
            actor_company_user_id=str(actor_company_user_id),
            account_id=str(account_id),
            concept_id=str(concept_id),
        )

    @strawberry.mutation
    def create_transaction(self, info: Info, input: CreateTransactionInput) -> Transaction:
        model = transaction_service.create_transaction(
            info.context.db,
            actor_company_user_id=str(input.actor_company_user_id),
            current_user=info.context.user,
            account_id=str(input.account_id),
            concept_id=str(input.concept_id),
            transaction_type=input.transaction_type,
            amount=input.amount,
            transaction_date=input.transaction_date,
            short_description=input.short_description,
            long_description=input.long_description,
        )
        return Transaction.from_model(model)

    @strawberry.mutation
    def delete_transaction(
        self, info: Info, id: strawberry.ID, actor_company_user_id: strawberry.ID
    ) -> Transaction:
        model = transaction_service.delete_transaction(
            info.context.db,
            actor_company_user_id=str(actor_company_user_id),
            transaction_id=str(id),
        )
        return Transaction.from_model(model)

    @strawberry.mutation
    def create_role(self, info: Info, input: CreateRoleInput) -> Role:
        model = role_service.create_role(
            info.context.db, code=input.code, name=input.name, description=input.description
        )
        return Role.from_model(model)

    @strawberry.mutation
    def deactivate_role(self, info: Info, id: strawberry.ID) -> Role:
        model = role_service.deactivate_role(info.context.db, str(id))
        return Role.from_model(model)

    @strawberry.mutation
    def create_permission(self, info: Info, input: CreatePermissionInput) -> Permission:
        model = role_service.create_permission(
            info.context.db, code=input.code, name=input.name, description=input.description
        )
        return Permission.from_model(model)

    @strawberry.mutation
    def assign_permission_to_role(
        self, info: Info, input: AssignPermissionToRoleInput
    ) -> RolePermission:
        model = role_service.assign_permission_to_role(
            info.context.db,
            actor_company_user_id=str(input.actor_company_user_id),
            role_id=str(input.role_id),
            permission_id=str(input.permission_id),
        )
        return RolePermission.from_model(model)

    @strawberry.mutation
    def remove_permission_from_role(
        self,
        info: Info,
        role_id: strawberry.ID,
        permission_id: strawberry.ID,
        actor_company_user_id: strawberry.ID,
    ) -> bool:
        return role_service.remove_permission_from_role(
            info.context.db,
            actor_company_user_id=str(actor_company_user_id),
            role_id=str(role_id),
            permission_id=str(permission_id),
        )

    @strawberry.mutation
    def assign_role(self, info: Info, input: AssignRoleInput) -> CompanyUserRole:
        model = role_service.assign_role(
            info.context.db,
            actor_company_user_id=str(input.actor_company_user_id),
            company_user_id=str(input.company_user_id),
            role_id=str(input.role_id),
        )
        return CompanyUserRole.from_model(model)
