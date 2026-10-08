"""Roles, permisos, matriz de permisos por rol y rol de cada membresía."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import (
    CompanyMismatch,
    DuplicatePermission,
    DuplicateRole,
    MembershipNotFound,
    PermissionDenied,
    PermissionNotFound,
    RoleNotFound,
    RolePermissionAlreadyExists,
    RolePermissionNotFound,
)
from app.core.validators import clean_text
from app.models import CompanyUser, CompanyUserRole, Permission, Role, RolePermission

ADMINISTRADOR = "ADMINISTRADOR"
CONTADOR = "CONTADOR"
CAPTURISTA = "CAPTURISTA"
CONSULTA = "CONSULTA"

DEFAULT_ROLES = [
    (ADMINISTRADOR, "Administrador", "El administrador principal de la empresa"),
    (CONTADOR, "Contador", "Quien arma cuentas y conceptos"),
    (CAPTURISTA, "Capturista", "Quien registra movimientos"),
    (CONSULTA, "Consulta", "Quien solo lee"),
]

DEFAULT_PERMISSIONS = [
    ("company.users.read", "Ver usuarios", "Ver las membresías de la empresa"),
    ("company.users.write", "Administrar usuarios", "Crear usuarios y desactivar membresías"),
    ("accounts.read", "Ver cuentas", "Consultar cuentas"),
    ("accounts.write", "Crear cuentas", "Crear cuentas"),
    ("concepts.read", "Ver conceptos", "Consultar conceptos"),
    ("concepts.write", "Administrar conceptos", "Crear conceptos y asignarlos a una cuenta"),
    ("transactions.read", "Ver movimientos", "Consultar movimientos"),
    ("transactions.write", "Registrar movimientos", "Registrar un ingreso o un egreso"),
    ("roles.read", "Ver roles", "Ver roles y la matriz de permisos"),
    (
        "roles.write",
        "Administrar roles",
        "Asignar o quitar permisos de un rol, y asignar un rol a una membresía",
    ),
]

# Variante plana: cada rol tiene su propia lista completa.
DEFAULT_MATRIX = {
    ADMINISTRADOR: [code for code, _, _ in DEFAULT_PERMISSIONS],
    CONTADOR: [
        "company.users.read",
        "accounts.read",
        "accounts.write",
        "concepts.read",
        "concepts.write",
        "transactions.read",
        "transactions.write",
        "roles.read",
    ],
    CAPTURISTA: [
        "accounts.read",
        "concepts.read",
        "transactions.read",
        "transactions.write",
    ],
    CONSULTA: [
        "company.users.read",
        "accounts.read",
        "concepts.read",
        "transactions.read",
    ],
}


def seed_access_catalog(db: Session) -> None:
    """Carga roles, permisos y matriz inicial sin duplicar en cada reinicio."""
    if db.scalar(select(func.count()).select_from(Role)) == 0:
        for code, name, description in DEFAULT_ROLES:
            db.add(Role(code=code, name=name, description=description))
        db.flush()

    if db.scalar(select(func.count()).select_from(Permission)) == 0:
        for code, name, description in DEFAULT_PERMISSIONS:
            db.add(Permission(code=code, name=name, description=description))
        db.flush()

    permissions = {p.code: p for p in db.scalars(select(Permission))}
    for role_code, permission_codes in DEFAULT_MATRIX.items():
        role = _get_role_by_code(db, role_code)
        if role is None:
            continue
        has_rows = db.scalars(
            select(RolePermission).where(RolePermission.role_id == role.id)
        ).first()
        if has_rows:
            continue
        for permission_code in permission_codes:
            permission = permissions.get(permission_code)
            if permission is not None:
                db.add(RolePermission(role_id=role.id, permission_id=permission.id))

    db.flush()
    _backfill_membership_roles(db)
    db.commit()


def _backfill_membership_roles(db: Session) -> None:
    """Las membresías creadas antes de esta actividad reciben un rol inicial."""
    admin_role = _get_role_by_code(db, ADMINISTRADOR)
    consulta_role = _get_role_by_code(db, CONSULTA)
    if admin_role is None or consulta_role is None:
        return

    for membership in db.scalars(select(CompanyUser)):
        if membership.active_role is not None:
            continue
        role = admin_role if membership.is_admin else consulta_role
        db.add(CompanyUserRole(company_user_id=membership.id, role_id=role.id))


def _get_role_by_code(db: Session, code: str) -> Role | None:
    return db.scalars(select(Role).where(Role.code == code)).first()


def _normalize_code(value: str, field: str) -> str:
    return clean_text(value, field, min_len=2, max_len=50)


# --- Control de acceso ---------------------------------------------------


def get_active_membership_or_fail(db: Session, company_user_id: str) -> CompanyUser:
    membership = db.get(CompanyUser, company_user_id)
    if membership is None or not membership.is_active:
        raise MembershipNotFound()
    return membership


def exigir_permiso(db: Session, company_user_id: str, codigo: str,
                   company_id: str | None = None) -> CompanyUser:
    """Membresía -> rol activo -> permisos activos del rol -> ¿está el código?

    Si se indica company_id, la membresía además debe pertenecer a esa empresa.
    """
    membership = get_active_membership_or_fail(db, company_user_id)

    if company_id is not None and membership.company_id != company_id:
        raise CompanyMismatch("La membresía no pertenece a la empresa del recurso.")

    asignacion = db.scalars(
        select(CompanyUserRole).where(
            CompanyUserRole.company_user_id == membership.id,
            CompanyUserRole.is_active.is_(True),
        )
    ).first()
    if asignacion is None:
        raise PermissionDenied("La membresía no tiene un rol activo.")

    permitido = db.scalars(
        select(RolePermission)
        .join(Role, Role.id == RolePermission.role_id)
        .join(Permission, Permission.id == RolePermission.permission_id)
        .where(
            RolePermission.role_id == asignacion.role_id,
            RolePermission.is_active.is_(True),
            Role.is_active.is_(True),
            Permission.code == codigo,
            Permission.is_active.is_(True),
        )
    ).first()
    if permitido is None:
        raise PermissionDenied(f"El rol no tiene el permiso {codigo}.")

    return membership


# --- Roles ---------------------------------------------------------------


def list_roles(db: Session, active_only: bool | None = None) -> list[Role]:
    stmt = select(Role)
    if active_only:
        stmt = stmt.where(Role.is_active.is_(True))
    return list(db.scalars(stmt.order_by(Role.created_at)))


def get_role(db: Session, role_id: str) -> Role | None:
    return db.get(Role, role_id)


def get_active_role_or_fail(db: Session, role_id: str) -> Role:
    role = db.get(Role, role_id)
    if role is None or not role.is_active:
        raise RoleNotFound()
    return role


def create_role(db: Session, *, code, name, description=None) -> Role:
    clean_code = _normalize_code(code, "code").upper()
    if _get_role_by_code(db, clean_code):
        raise DuplicateRole()

    role = Role(
        code=clean_code,
        name=clean_text(name, "name", min_len=2, max_len=100),
        description=description.strip() if description else None,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def deactivate_role(db: Session, role_id: str) -> Role:
    """Baja lógica: el historial sigue apuntando al rol."""
    role = db.get(Role, role_id)
    if role is None:
        raise RoleNotFound()
    role.is_active = False
    db.commit()
    db.refresh(role)
    return role


# --- Permisos ------------------------------------------------------------


def list_permissions(db: Session, active_only: bool | None = None) -> list[Permission]:
    stmt = select(Permission)
    if active_only:
        stmt = stmt.where(Permission.is_active.is_(True))
    return list(db.scalars(stmt.order_by(Permission.created_at)))


def create_permission(db: Session, *, code, name, description=None) -> Permission:
    clean_code = _normalize_code(code, "code").lower()
    if db.scalars(select(Permission).where(Permission.code == clean_code)).first():
        raise DuplicatePermission()

    permission = Permission(
        code=clean_code,
        name=clean_text(name, "name", min_len=2, max_len=100),
        description=description.strip() if description else None,
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


# --- Permisos por rol ----------------------------------------------------


def list_role_permissions(db: Session, role_id: str) -> list[RolePermission]:
    if db.get(Role, role_id) is None:
        raise RoleNotFound()
    return list(
        db.scalars(
            select(RolePermission)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .where(
                RolePermission.role_id == role_id,
                RolePermission.is_active.is_(True),
                Permission.is_active.is_(True),
            )
            .order_by(RolePermission.created_at)
        )
    )


def assign_permission_to_role(db: Session, *, actor_company_user_id, role_id,
                              permission_id) -> RolePermission:
    exigir_permiso(db, actor_company_user_id, "roles.write")

    role = get_active_role_or_fail(db, role_id)
    permission = db.get(Permission, permission_id)
    if permission is None or not permission.is_active:
        raise PermissionNotFound()

    existing = db.scalars(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
    ).first()
    if existing:
        if existing.is_active:
            raise RolePermissionAlreadyExists()
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing

    relation = RolePermission(role_id=role.id, permission_id=permission.id)
    db.add(relation)
    db.commit()
    db.refresh(relation)
    return relation


def remove_permission_from_role(db: Session, *, actor_company_user_id, role_id,
                                permission_id) -> bool:
    exigir_permiso(db, actor_company_user_id, "roles.write")

    relation = db.scalars(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
    ).first()
    if relation is None or not relation.is_active:
        raise RolePermissionNotFound()
    relation.is_active = False
    db.commit()
    return True


# --- Rol de la membresía -------------------------------------------------


def set_membership_role(db: Session, membership: CompanyUser, role: Role) -> CompanyUserRole:
    """Deja un solo rol activo por membresía. No hace commit."""
    target = None
    for assignment in db.scalars(
        select(CompanyUserRole).where(CompanyUserRole.company_user_id == membership.id)
    ):
        if assignment.role_id == role.id:
            target = assignment
        else:
            assignment.is_active = False

    if target is None:
        target = CompanyUserRole(company_user_id=membership.id, role_id=role.id)
        db.add(target)
    else:
        target.is_active = True
    db.flush()
    return target


def assign_role(db: Session, *, actor_company_user_id, company_user_id,
                role_id) -> CompanyUserRole:
    membership = get_active_membership_or_fail(db, company_user_id)
    exigir_permiso(db, actor_company_user_id, "roles.write", company_id=membership.company_id)

    role = get_active_role_or_fail(db, role_id)
    assignment = set_membership_role(db, membership, role)
    db.commit()
    db.refresh(assignment)
    return assignment


def get_role_by_code_or_fail(db: Session, code: str) -> Role:
    role = _get_role_by_code(db, code)
    if role is None or not role.is_active:
        raise RoleNotFound(f"El rol {code} no existe o está inactivo.")
    return role
