from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import (
    CompanyMismatch,
    ConceptNotAllowed,
    InvalidAmount,
    TransactionNotFound,
    TransactionTypeMismatch,
    Unauthenticated,
)
from app.models import AccountConcept, CompanyUser, Transaction
from app.models.transaction import TransactionType
from app.services.account_service import get_active_account_or_fail
from app.services.concept_service import get_active_concept_or_fail


def _user_belongs_to_company(db: Session, user_id: str, company_id: str) -> bool:
    membership = db.scalars(
        select(CompanyUser).where(
            CompanyUser.user_id == user_id,
            CompanyUser.company_id == company_id,
            CompanyUser.is_active.is_(True),
        )
    ).first()
    return membership is not None


def create_transaction(db: Session, *, current_user, account_id, concept_id, transaction_type,
                       amount, transaction_date=None, short_description=None,
                       long_description=None) -> Transaction:
    if current_user is None:
        raise Unauthenticated()

    amount = Decimal(str(amount))
    if amount <= 0:
        raise InvalidAmount()

    account = get_active_account_or_fail(db, account_id)
    concept = get_active_concept_or_fail(db, concept_id)

    if account.company_id != concept.company_id:
        raise CompanyMismatch("La cuenta y el concepto pertenecen a empresas distintas.")

    if not _user_belongs_to_company(db, current_user.id, account.company_id):
        raise CompanyMismatch("El usuario no pertenece a la empresa de la cuenta.")

    relation = db.scalars(
        select(AccountConcept).where(
            AccountConcept.account_id == account.id,
            AccountConcept.concept_id == concept.id,
            AccountConcept.is_active.is_(True),
        )
    ).first()
    if relation is None:
        raise ConceptNotAllowed()

    tx_type = TransactionType(transaction_type)
    if tx_type.value != concept.concept_type.value:
        raise TransactionTypeMismatch(
            f"El concepto es de tipo {concept.concept_type.value} "
            f"y el movimiento se registró como {tx_type.value}."
        )

    transaction = Transaction(
        account_id=account.id,
        concept_id=concept.id,
        transaction_type=tx_type,
        amount=amount,
        transaction_date=transaction_date or datetime.now(timezone.utc),
        captured_by=current_user.id,
        short_description=short_description.strip() if short_description else None,
        long_description=long_description.strip() if long_description else None,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def list_transactions(db: Session, *, account_id=None, transaction_type=None,
                      limit=None, offset=None) -> list[Transaction]:
    stmt = select(Transaction).where(Transaction.is_active.is_(True))
    if account_id is not None:
        stmt = stmt.where(Transaction.account_id == account_id)
    if transaction_type is not None:
        stmt = stmt.where(Transaction.transaction_type == TransactionType(transaction_type))
    stmt = stmt.order_by(Transaction.transaction_date.desc())
    if offset:
        stmt = stmt.offset(offset)
    if limit:
        stmt = stmt.limit(limit)
    return list(db.scalars(stmt))


def delete_transaction(db: Session, transaction_id: str) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None or not transaction.is_active:
        raise TransactionNotFound()
    transaction.is_active = False
    db.commit()
    db.refresh(transaction)
    return transaction
