"""Tipos e inputs de GraphQL para Company."""
from datetime import datetime

import strawberry


@strawberry.type
class Company:
    id: strawberry.ID
    name: str
    legal_name: str | None
    tax_id: str | None
    email: str | None
    phone: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, model) -> "Company":
        return cls(
            id=strawberry.ID(model.id),
            name=model.name,
            legal_name=model.legal_name,
            tax_id=model.tax_id,
            email=model.email,
            phone=model.phone,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


@strawberry.input
class CreateCompanyInput:
    name: str
    legal_name: str | None = None
    tax_id: str | None = None
    email: str | None = None
    phone: str | None = None


@strawberry.input
class UpdateCompanyInput:
    id: strawberry.ID
    name: str | None = None
    legal_name: str | None = None
    tax_id: str | None = None
    email: str | None = None
    phone: str | None = None
    is_active: bool | None = None
