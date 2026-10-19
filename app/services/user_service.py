from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import (
    AccountDisabled,
    AdminAlreadyExists,
    EmailAlreadyExists,
    InvalidCredentials,
    MembershipAlreadyExists,
    ValidationError,
)
from app.core.security import crear_token, hash_password, verify_password
from app.core.validators import clean_text, normalize_email, validate_password
from app.models import CompanyUser, User
from app.services.company_service import get_active_company_or_fail
from app.services.role_service import (
    ADMINISTRADOR,
    CONSULTA,
    exigir_permiso,
    get_role_by_code_or_fail,
    set_membership_role,
)


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
    db.flush()

    # isAdmin cuida que haya un solo administrador; el rol cuida qué puede ejecutar.
    role = get_role_by_code_or_fail(db, ADMINISTRADOR if is_admin else CONSULTA)
    set_membership_role(db, membership, role)
    db.commit()
    db.refresh(membership)
    return membership


def create_company_admin(db: Session, *, company_id, name, email, password) -> CompanyUser:
    return _create_membership(
        db, company_id=company_id, name=name, email=email, password=password, is_admin=True
    )


def create_company_user(db: Session, *, actor_company_user_id, company_id, name, email,
                        password) -> CompanyUser:
    exigir_permiso(db, actor_company_user_id, "company.users.write", company_id=company_id)
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


def deactivate_company_user(db: Session, *, actor_company_user_id,
                            membership_id: str) -> CompanyUser:
    membership = db.get(CompanyUser, membership_id)
    if membership is None:
        raise MembershipAlreadyExists("La membresía indicada no existe.")
    exigir_permiso(
        db, actor_company_user_id, "company.users.write", company_id=membership.company_id
    )
    membership.is_active = False
    db.commit()
    db.refresh(membership)
    return membership


def login(db: Session, *, email: str, password: str,
          company_id: str | None = None) -> tuple[str, User]:
    """Comprueba el hash y, si coincide, firma un token para una sola membresía."""
    try:
        clean_email = normalize_email(email)
    except Exception:
        raise InvalidCredentials()

    user = _get_user_by_email(db, clean_email)

    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentials()

    if not user.is_active:
        raise AccountDisabled()

    active = [m for m in user.memberships if m.is_active]
    if not active:
        raise AccountDisabled()

    # Cada token vale para una empresa. Si la persona está en varias, indica cuál.
    if company_id is not None:
        active = [m for m in active if m.company_id == str(company_id)]
        if not active:
            raise InvalidCredentials("El usuario no tiene una membresía activa en esa empresa.")
    elif len(active) > 1:
        raise ValidationError(
            "El usuario pertenece a varias empresas; indica companyId para iniciar sesión."
        )

    membership = active[0]
    # companyId sale de la fila de la membresía, no de lo que envía el cliente.
    return crear_token(membership.id, membership.company_id), user
