import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ConceptType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Concept(Base):
    __tablename__ = "concepts"
    __table_args__ = (UniqueConstraint("company_id", "name", name="uq_concept_name"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False)
    concept_type: Mapped[ConceptType] = mapped_column(Enum(ConceptType), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(200))
    long_description: Mapped[str | None] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now, nullable=False
    )

    company: Mapped["Company"] = relationship()
    account_concepts: Mapped[list["AccountConcept"]] = relationship(back_populates="concept")
