import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CompanyUser(Base):
    __tablename__ = "company_users"
    __table_args__ = (
        UniqueConstraint("company_id", "user_id", name="uq_company_user"),
        Index(
            "uq_company_admin",
            "company_id",
            unique=True,
            sqlite_where=text("is_admin = 1"),
            postgresql_where=text("is_admin = true"),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=_now, nullable=False)

    company: Mapped["Company"] = relationship(back_populates="memberships")
    user: Mapped["User"] = relationship(back_populates="memberships")
    role_assignments: Mapped[list["CompanyUserRole"]] = relationship(
        back_populates="company_user"
    )

    @property
    def active_role(self):
        for assignment in self.role_assignments:
            if assignment.is_active:
                return assignment.role
        return None
