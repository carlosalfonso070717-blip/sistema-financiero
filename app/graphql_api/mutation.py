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
from app.schemas.user import (
    AuthPayload,
    AuthUser,
    CompanyUser,
    CreateCompanyAdminInput,
    CreateCompanyUserInput,
    LoginInput,
)
from app.services import account_service, company_service, concept_service, user_service


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
            company_id=str(input.company_id),
            name=input.name,
            email=input.email,
            password=input.password,
        )
        return CompanyUser.from_model(model)

    @strawberry.mutation
    def deactivate_company_user(self, info: Info, id: strawberry.ID) -> CompanyUser:
        model = user_service.deactivate_company_user(info.context.db, str(id))
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
            account_id=str(input.account_id),
            concept_id=str(input.concept_id),
        )
        return AccountConcept.from_model(model)

    @strawberry.mutation
    def remove_concept_from_account(
        self, info: Info, account_id: strawberry.ID, concept_id: strawberry.ID
    ) -> bool:
        return account_service.remove_concept_from_account(
            info.context.db, account_id=str(account_id), concept_id=str(concept_id)
        )
