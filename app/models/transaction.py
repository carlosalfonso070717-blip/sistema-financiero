import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TransactionType(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id"), nullable=False)
    concept_id: Mapped[str] = mapped_column(String(36), ForeignKey("concepts.id"), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, default=_now, nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=_now, nullable=False)
    captured_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(200))
    long_description: Mapped[str | None] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now, nullable=False
    )

    account: Mapped["Account"] = relationship()
    concept: Mapped["Concept"] = relationship()
    captured_by_user: Mapped["User"] = relationship()
