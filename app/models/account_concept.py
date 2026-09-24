import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AccountConcept(Base):
    __tablename__ = "account_concepts"
    __table_args__ = (
        UniqueConstraint("account_id", "concept_id", name="uq_account_concept"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id"), nullable=False)
    concept_id: Mapped[str] = mapped_column(String(36), ForeignKey("concepts.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, nullable=False)

    account: Mapped["Account"] = relationship(back_populates="account_concepts")
    concept: Mapped["Concept"] = relationship(back_populates="account_concepts")
