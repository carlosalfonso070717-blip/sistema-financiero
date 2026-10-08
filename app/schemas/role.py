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
