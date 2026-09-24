from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ConceptNotFound, DuplicateConcept
from app.core.validators import clean_text
from app.models import Concept, ConceptType
from app.services.company_service import get_active_company_or_fail


def create_concept(db: Session, *, company_id, concept_type, name,
                   short_description=None, long_description=None) -> Concept:
    company = get_active_company_or_fail(db, company_id)
    clean_name = clean_text(name, "name", min_len=2, max_len=150)

    existing = db.scalars(
        select(Concept).where(
            Concept.company_id == company.id,
            Concept.name == clean_name,
        )
    ).first()
    if existing:
        raise DuplicateConcept()

    concept = Concept(
        company_id=company.id,
        concept_type=ConceptType(concept_type),
        name=clean_name,
        short_description=short_description.strip() if short_description else None,
        long_description=long_description.strip() if long_description else None,
    )
    db.add(concept)
    db.commit()
    db.refresh(concept)
    return concept


def list_concepts(db: Session, *, company_id, concept_type=None, active_only=None) -> list[Concept]:
    stmt = select(Concept).where(Concept.company_id == company_id)
    if concept_type is not None:
        stmt = stmt.where(Concept.concept_type == ConceptType(concept_type))
    if active_only:
        stmt = stmt.where(Concept.is_active.is_(True))
    return list(db.scalars(stmt.order_by(Concept.created_at)))


def get_active_concept_or_fail(db: Session, concept_id: str) -> Concept:
    concept = db.get(Concept, concept_id)
    if concept is None or not concept.is_active:
        raise ConceptNotFound()
    return concept
