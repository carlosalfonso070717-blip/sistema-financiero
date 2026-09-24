from datetime import datetime

import strawberry

from app.models.account import AccountType as AccountTypeEnum
from app.models.concept import ConceptType as ConceptTypeEnum
from app.schemas.company import Company

AccountType = strawberry.enum(AccountTypeEnum)
ConceptType = strawberry.enum(ConceptTypeEnum)


@strawberry.type
class Account:
    id: strawberry.ID
    company_id: strawberry.ID
    account_type: AccountType
    name: str
    bank_name: str | None
    account_number: str | None
    clabe: str | None
    card_last_digits: str | None
    short_description: str | None
    long_description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    company: Company

    @classmethod
    def from_model(cls, model) -> "Account":
        return cls(
            id=strawberry.ID(model.id),
            company_id=strawberry.ID(model.company_id),
            account_type=model.account_type,
            name=model.name,
            bank_name=model.bank_name,
            account_number=model.account_number,
            clabe=model.clabe,
            card_last_digits=model.card_last_digits,
            short_description=model.short_description,
            long_description=model.long_description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            company=Company.from_model(model.company),
        )


@strawberry.type
class Concept:
    id: strawberry.ID
    company_id: strawberry.ID
    concept_type: ConceptType
    name: str
    short_description: str | None
    long_description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, model) -> "Concept":
        return cls(
            id=strawberry.ID(model.id),
            company_id=strawberry.ID(model.company_id),
            concept_type=model.concept_type,
            name=model.name,
            short_description=model.short_description,
            long_description=model.long_description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


@strawberry.type
class AccountConcept:
    id: strawberry.ID
    account_id: strawberry.ID
    concept_id: strawberry.ID
    is_active: bool
    created_at: datetime
    account: Account
    concept: Concept

    @classmethod
    def from_model(cls, model) -> "AccountConcept":
        return cls(
            id=strawberry.ID(model.id),
            account_id=strawberry.ID(model.account_id),
            concept_id=strawberry.ID(model.concept_id),
            is_active=model.is_active,
            created_at=model.created_at,
            account=Account.from_model(model.account),
            concept=Concept.from_model(model.concept),
        )


@strawberry.input
class CreateAccountInput:
    company_id: strawberry.ID
    account_type: AccountType
    name: str
    bank_name: str | None = None
    account_number: str | None = None
    clabe: str | None = None
    card_last_digits: str | None = None
    short_description: str | None = None
    long_description: str | None = None


@strawberry.input
class CreateConceptInput:
    company_id: strawberry.ID
    concept_type: ConceptType
    name: str
    short_description: str | None = None
    long_description: str | None = None


@strawberry.input
class AssignConceptToAccountInput:
    account_id: strawberry.ID
    concept_id: strawberry.ID
