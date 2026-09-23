from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import (
    AccountDisabled,
    AdminAlreadyExists,
    EmailAlreadyExists,
    InvalidCredentials,
    MembershipAlreadyExists,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.core.validators import clean_text, normalize_email, validate_password
from app.models import CompanyUser, User
from app.services.company_service import get_active_company_or_fail


def _get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()


def _create_membership(db: Session, *, company_id, name, email, password, is_admin) -> CompanyUser:
    company = get_active_company_or_fail(db, company_id)

    clean_name = clean_text(name, "name", min_len=2, max_len=150)
    clean_email = normalize_email(email)
    validate_password(password)

    if is_admin:
        existing_admin = db.scalars(
            select(CompanyUser).where(
                CompanyUser.company_id == company.id,
                CompanyUser.is_admin.is_(True),
            )
        ).first()
        if existing_admin:
            raise AdminAlreadyExists()

    if _get_user_by_email(db, clean_email):
        raise EmailAlreadyExists()

    user = User(name=clean_name, email=clean_email, password_hash=hash_password(password))
    db.add(user)
    db.flush()

    duplicate = db.scalars(
        select(CompanyUser).where(
            CompanyUser.company_id == company.id,
            CompanyUser.user_id == user.id,
        )
    ).first()
    if duplicate:
        db.rollback()
        raise MembershipAlreadyExists()

    membership = CompanyUser(company_id=company.id, user_id=user.id, is_admin=is_admin)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def create_company_admin(db: Session, *, company_id, name, email, password) -> CompanyUser:
    return _create_membership(
        db, company_id=company_id, name=name, email=email, password=password, is_admin=True
    )


def create_company_user(db: Session, *, company_id, name, email, password) -> CompanyUser:
    return _create_membership(
        db, company_id=company_id, name=name, email=email, password=password, is_admin=False
    )


def list_company_users(db: Session, company_id: str) -> list[CompanyUser]:
    get_active_company_or_fail(db, company_id)
    return list(
        db.scalars(
            select(CompanyUser)
            .where(CompanyUser.company_id == company_id)
            .order_by(CompanyUser.joined_at)
        )
    )


def deactivate_company_user(db: Session, membership_id: str) -> CompanyUser:
    membership = db.get(CompanyUser, membership_id)
    if membership is None:
        raise MembershipAlreadyExists("La membresía indicada no existe.")
    membership.is_active = False
    db.commit()
    db.refresh(membership)
    return membership


def login(db: Session, *, email: str, password: str) -> tuple[str, User]:
    try:
        clean_email = normalize_email(email)
    except Exception:
        raise InvalidCredentials()

    user = _get_user_by_email(db, clean_email)

    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentials()

    if not user.is_active:
        raise AccountDisabled()
    if user.memberships and not any(m.is_active for m in user.memberships):
        raise AccountDisabled()

    return create_access_token(user.id), user
