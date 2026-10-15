import enum
from datetime import datetime

import strawberry


@strawberry.type
class Role:
    id: strawberry.ID
    code: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime

    @classmethod
    def from_model(cls, model) -> "Role":
        return cls(
            id=strawberry.ID(model.id),
            code=model.code,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
        )


@strawberry.type
class Permission:
    id: strawberry.ID
    code: str
    name: str
    description: str | None
    is_active: bool
    created_at: datetime

    @classmethod
    def from_model(cls, model) -> "Permission":
        return cls(
            id=strawberry.ID(model.id),
            code=model.code,
            name=model.name,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
        )


@strawberry.type
class RolePermission:
    id: strawberry.ID
    role: Role
    permission: Permission
    is_active: bool

    @classmethod
    def from_model(cls, model) -> "RolePermission":
        return cls(
            id=strawberry.ID(model.id),
            role=Role.from_model(model.role),
            permission=Permission.from_model(model.permission),
            is_active=model.is_active,
        )


@strawberry.input
class CreateRoleInput:
    code: str
    name: str
    description: str | None = None


@strawberry.input
class CreatePermissionInput:
    code: str
    name: str
    description: str | None = None


@strawberry.input
class AssignPermissionToRoleInput:
    actor_company_user_id: strawberry.ID
    role_id: strawberry.ID
    permission_id: strawberry.ID


@strawberry.enum
class PermissionResource(enum.Enum):
    COMPANY_USERS = "COMPANY_USERS"
    ACCOUNTS = "ACCOUNTS"
    CONCEPTS = "CONCEPTS"
    TRANSACTIONS = "TRANSACTIONS"
    ROLES = "ROLES"


@strawberry.input
class SetRolePermissionsInput:
    role_id: strawberry.ID
    permission_ids: list[strawberry.ID]


def _permissions(rows) -> list[Permission]:
    return [Permission.from_model(p) for p in rows]


@strawberry.type
class RolePermissionPlan:
    role: Role
    current: list[Permission]
    to_activate: list[Permission]
    to_deactivate: list[Permission]
    unchanged: list[Permission]
    final_count: int

    @classmethod
    def from_plan(cls, plan) -> "RolePermissionPlan":
        return cls(
            role=Role.from_model(plan.role),
            current=_permissions(plan.current),
            to_activate=_permissions(plan.to_activate),
            to_deactivate=_permissions(plan.to_deactivate),
            unchanged=_permissions(plan.unchanged),
            final_count=plan.final_count,
        )


@strawberry.type
class RolePermissionUpdate:
    role: Role
    activated: list[Permission]
    deactivated: list[Permission]
    unchanged: list[Permission]
    final_count: int
    changed: bool

    @classmethod
    def from_plan(cls, plan) -> "RolePermissionUpdate":
        return cls(
            role=Role.from_model(plan.role),
            activated=_permissions(plan.to_activate),
            deactivated=_permissions(plan.to_deactivate),
            unchanged=_permissions(plan.unchanged),
            final_count=plan.final_count,
            changed=plan.changed,
        )
