from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import (
    AccountNotFound,
    CompanyMismatch,
    ConceptNotFound,
    DuplicateAccount,
    RelationAlreadyExists,
    RelationNotFound,
)
from app.core.validators import clean_text
from app.models import Account, AccountConcept, AccountType, Concept
from app.services.company_service import get_active_company_or_fail


def create_account(db: Session, *, company_id, account_type, name, bank_name=None,
                   account_number=None, clabe=None, card_last_digits=None,
                   short_description=None, long_description=None) -> Account:
    company = get_active_company_or_fail(db, company_id)
    clean_name = clean_text(name, "name", min_len=2, max_len=150)

    existing = db.scalars(
        select(Account).where(
            Account.company_id == company.id,
            Account.name == clean_name,
        )
    ).first()
    if existing:
        raise DuplicateAccount()

    account = Account(
        company_id=company.id,
        account_type=AccountType(account_type),
        name=clean_name,
        bank_name=bank_name.strip() if bank_name else None,
        account_number=account_number.strip() if account_number else None,
        clabe=clabe.strip() if clabe else None,
        card_last_digits=card_last_digits.strip() if card_last_digits else None,
        short_description=short_description.strip() if short_description else None,
        long_description=long_description.strip() if long_description else None,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def list_accounts(db: Session, *, company_id, account_type=None, active_only=None) -> list[Account]:
    stmt = select(Account).where(Account.company_id == company_id)
    if account_type is not None:
        stmt = stmt.where(Account.account_type == AccountType(account_type))
    if active_only:
        stmt = stmt.where(Account.is_active.is_(True))
    return list(db.scalars(stmt.order_by(Account.created_at)))


def get_active_account_or_fail(db: Session, account_id: str) -> Account:
    account = db.get(Account, account_id)
    if account is None or not account.is_active:
        raise AccountNotFound()
    return account


def assign_concept_to_account(db: Session, *, account_id, concept_id) -> AccountConcept:
    account = get_active_account_or_fail(db, account_id)

    concept = db.get(Concept, concept_id)
    if concept is None or not concept.is_active:
        raise ConceptNotFound()

    if account.company_id != concept.company_id:
        raise CompanyMismatch("La cuenta y el concepto pertenecen a empresas distintas.")

    existing = db.scalars(
        select(AccountConcept).where(
            AccountConcept.account_id == account.id,
            AccountConcept.concept_id == concept.id,
        )
    ).first()
    if existing:
        if existing.is_active:
            raise RelationAlreadyExists()
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing

    relation = AccountConcept(account_id=account.id, concept_id=concept.id)
    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation


def list_account_concepts(db: Session, account_id: str) -> list[AccountConcept]:
    get_active_account_or_fail(db, account_id)
    return list(
        db.scalars(
            select(AccountConcept)
            .where(AccountConcept.account_id == account_id)
            .order_by(AccountConcept.created_at)
        )
    )


def remove_concept_from_account(db: Session, *, account_id, concept_id) -> bool:
    relation = db.scalars(
        select(AccountConcept).where(
            AccountConcept.account_id == account_id,
            AccountConcept.concept_id == concept_id,
        )
    ).first()
    if relation is None or not relation.is_active:
        raise RelationNotFound()
    relation.is_active = False
    db.commit()
    return True
