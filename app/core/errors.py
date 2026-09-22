"""Errores de dominio con codigo estable en extensions.
"""
from graphql import GraphQLError


class DomainError(GraphQLError):
    code = "DOMAIN_ERROR"

    def __init__(self, message: str | None = None):
        super().__init__(
            message or self.default_message,
            extensions={"code": self.code},
        )


class ValidationError(DomainError):
    code = "VALIDATION_ERROR"
    default_message = "Los datos enviados no son válidos."


class CompanyNotFound(DomainError):
    code = "COMPANY_NOT_FOUND"
    default_message = "La empresa especificada no existe o está inactiva."


class EmailAlreadyExists(DomainError):
    code = "EMAIL_ALREADY_EXISTS"
    default_message = "El correo electrónico ya esta registrado."


class AdminAlreadyExists(DomainError):
    code = "ADMIN_ALREADY_EXISTS"
    default_message = "La empresa ya cuenta con un administrador principal."


class MembershipAlreadyExists(DomainError):
    code = "MEMBERSHIP_ALREADY_EXISTS"
    default_message = "El usuario ya esta registrado en esta empresa."


class InvalidCredentials(DomainError):
    code = "INVALID_CREDENTIALS"
    default_message = "Credenciales inválidas."


class AccountDisabled(DomainError):
    code = "ACCOUNT_DISABLED"
    default_message = "La cuenta se encuentra deshabilitada."


class Forbidden(DomainError):
    code = "FORBIDDEN"
    default_message = "No tiene permisos sobre este recurso."


class Unauthenticated(DomainError):
    code = "UNAUTHENTICATED"
    default_message = "Se requiere autenticación para esta operación."
