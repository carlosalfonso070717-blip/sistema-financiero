from datetime import datetime
from decimal import Decimal

import strawberry

from app.models.transaction import TransactionType as TransactionTypeEnum
from app.schemas.account import Account, Concept
from app.schemas.user import User

TransactionType = strawberry.enum(TransactionTypeEnum)


@strawberry.type
class Transaction:
    id: strawberry.ID
    account_id: strawberry.ID
    concept_id: strawberry.ID
    transaction_type: TransactionType
    amount: Decimal
    transaction_date: datetime
    captured_at: datetime
    captured_by: strawberry.ID
    short_description: str | None
    long_description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    account: Account
    concept: Concept
    captured_by_user: User

    @classmethod
    def from_model(cls, model) -> "Transaction":
        return cls(
            id=strawberry.ID(model.id),
            account_id=strawberry.ID(model.account_id),
            concept_id=strawberry.ID(model.concept_id),
            transaction_type=model.transaction_type,
            amount=model.amount,
            transaction_date=model.transaction_date,
            captured_at=model.captured_at,
            captured_by=strawberry.ID(model.captured_by),
            short_description=model.short_description,
            long_description=model.long_description,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            account=Account.from_model(model.account),
            concept=Concept.from_model(model.concept),
            captured_by_user=User.from_model(model.captured_by_user),
        )


@strawberry.input
class CreateTransactionInput:
    account_id: strawberry.ID
    concept_id: strawberry.ID
    transaction_type: TransactionType
    amount: Decimal
    transaction_date: datetime | None = None
    short_description: str | None = None
    long_description: str | None = None
