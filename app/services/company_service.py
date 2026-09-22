"""Reglas de negocio de la gestion de empresas (Dia 1)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import CompanyNotFound, ValidationError
from app.core.validators import clean_text, normalize_email
from app.models import Company


def _validate_tax_id(db: Session, tax_id: str | None, exclude_id: str | None = None) -> str | None:
    if tax_id is None or not tax_id.strip():
        return None
    cleaned = tax_id.strip().upper()
    if len(cleaned) not in (12, 13):
        raise ValidationError("El RFC debe tener 12 o 13 caracteres.")
    stmt = select(Company).where(Company.tax_id == cleaned)
    if exclude_id:
        stmt = stmt.where(Company.id != exclude_id)
    if db.scalars(stmt).first():
        raise ValidationError("Ya existe una empresa registrada con ese RFC.")
    return cleaned


def create_company(db: Session, *, name, legal_name=None, tax_id=None, email=None, phone=None) -> Company:
    company = Company(
        name=clean_text(name, "name", min_len=2, max_len=150),
        legal_name=legal_name.strip() if legal_name else None,
        tax_id=_validate_tax_id(db, tax_id),
        email=normalize_email(email) if email else None,
        phone=phone.strip() if phone else None,
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def list_companies(db: Session, active_only: bool | None = None) -> list[Company]:
    stmt = select(Company)
    if active_only:
        stmt = stmt.where(Company.is_active.is_(True))
    return list(db.scalars(stmt.order_by(Company.created_at)))


def get_company(db: Session, company_id: str) -> Company | None:
    """Un identificador inexistente es un resultado vacio, no un error."""
    return db.get(Company, company_id)


def get_active_company_or_fail(db: Session, company_id: str) -> Company:
    """RN-05: no se opera sobre una empresa inexistente o inactiva."""
    company = db.get(Company, company_id)
    if company is None or not company.is_active:
        raise CompanyNotFound()
    return company


def update_company(db: Session, *, company_id, **fields) -> Company:
    company = db.get(Company, company_id)
    if company is None:
        raise CompanyNotFound()

    if fields.get("name") is not None:
        company.name = clean_text(fields["name"], "name", min_len=2, max_len=150)
    if fields.get("legal_name") is not None:
        company.legal_name = fields["legal_name"].strip() or None
    if fields.get("tax_id") is not None:
        company.tax_id = _validate_tax_id(db, fields["tax_id"], exclude_id=company_id)
    if fields.get("email") is not None:
        company.email = normalize_email(fields["email"]) if fields["email"] else None
    if fields.get("phone") is not None:
        company.phone = fields["phone"].strip() or None
    if fields.get("is_active") is not None:
        company.is_active = fields["is_active"]

    db.commit()
    db.refresh(company)
    return company


def deactivate_company(db: Session, company_id: str) -> Company:
    """RN-06: baja logica. El registro se conserva por trazabilidad."""
    company = db.get(Company, company_id)
    if company is None:
        raise CompanyNotFound()
    company.is_active = False
    db.commit()
    db.refresh(company)
    return company
