from datetime import datetime

import strawberry

from app.schemas.company import Company
from app.schemas.role import Role


@strawberry.type
class User:
    id: strawberry.ID
    name: str
    email: str
    email_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, model) -> "User":
        return cls(
            id=strawberry.ID(model.id),
            name=model.name,
            email=model.email,
            email_verified=model.email_verified,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


@strawberry.type
class CompanyUser:
    id: strawberry.ID
    company_id: strawberry.ID
    user_id: strawberry.ID
    is_admin: bool
    is_active: bool
    joined_at: datetime
    company: Company
    user: User
    role: Role | None

    @classmethod
    def from_model(cls, model) -> "CompanyUser":
        role = model.active_role
        return cls(
            id=strawberry.ID(model.id),
            company_id=strawberry.ID(model.company_id),
            user_id=strawberry.ID(model.user_id),
            is_admin=model.is_admin,
            is_active=model.is_active,
            joined_at=model.joined_at,
            company=Company.from_model(model.company),
            user=User.from_model(model.user),
            role=Role.from_model(role) if role else None,
        )


@strawberry.type
class CompanyUserRole:
    id: strawberry.ID
    company_user: CompanyUser
    role: Role
    is_active: bool
    assigned_at: datetime

    @classmethod
    def from_model(cls, model) -> "CompanyUserRole":
        return cls(
            id=strawberry.ID(model.id),
            company_user=CompanyUser.from_model(model.company_user),
            role=Role.from_model(model.role),
            is_active=model.is_active,
            assigned_at=model.assigned_at,
        )


@strawberry.input
class AssignRoleInput:
    actor_company_user_id: strawberry.ID
    company_user_id: strawberry.ID
    role_id: strawberry.ID


@strawberry.input
class LoginInput:
    email: str
    password: str


@strawberry.type
class AuthUser:
    id: strawberry.ID
    name: str
    email: str


@strawberry.type
class AuthPayload:
    token: str
    token_type: str
    user: AuthUser


@strawberry.input
class CreateCompanyAdminInput:
    company_id: strawberry.ID
    name: str
    email: str
    password: str


@strawberry.input
class CreateCompanyUserInput:
    actor_company_user_id: strawberry.ID
    company_id: strawberry.ID
    name: str
    email: str
    password: str
