from graphql import GraphQLError


class DomainError(GraphQLError):
    code = "DOMAIN_ERROR"
    default_message = "Ocurrió un error en la operación."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message, extensions={"code": self.code})


class ValidationError(DomainError):
    code = "VALIDATION_ERROR"
    default_message = "Los datos enviados no son válidos."


class CompanyNotFound(DomainError):
    code = "COMPANY_NOT_FOUND"
    default_message = "La empresa especificada no existe o está inactiva."


class EmailAlreadyExists(DomainError):
    code = "EMAIL_ALREADY_EXISTS"
    default_message = "El correo electrónico ya está registrado."


class AdminAlreadyExists(DomainError):
    code = "ADMIN_ALREADY_EXISTS"
    default_message = "La empresa ya cuenta con un administrador principal."


class MembershipAlreadyExists(DomainError):
    code = "MEMBERSHIP_ALREADY_EXISTS"
    default_message = "El usuario ya está registrado en esta empresa."


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


class AccountNotFound(DomainError):
    code = "ACCOUNT_NOT_FOUND"
    default_message = "La cuenta especificada no existe o está inactiva."


class ConceptNotFound(DomainError):
    code = "CONCEPT_NOT_FOUND"
    default_message = "El concepto especificado no existe o está inactivo."


class DuplicateAccount(DomainError):
    code = "DUPLICATE_ACCOUNT"
    default_message = "La empresa ya tiene una cuenta registrada con ese nombre."


class DuplicateConcept(DomainError):
    code = "DUPLICATE_CONCEPT"
    default_message = "La empresa ya tiene un concepto registrado con ese nombre."


class RelationAlreadyExists(DomainError):
    code = "RELATION_ALREADY_EXISTS"
    default_message = "El concepto ya está asignado a esta cuenta."


class RelationNotFound(DomainError):
    code = "RELATION_NOT_FOUND"
    default_message = "El concepto no está asignado a esta cuenta."


class CompanyMismatch(DomainError):
    code = "COMPANY_MISMATCH"
    default_message = "Los registros involucrados pertenecen a empresas distintas."


class ConceptNotAllowed(DomainError):
    code = "CONCEPT_NOT_ALLOWED"
    default_message = "El concepto no está permitido para la cuenta seleccionada."


class InvalidAmount(DomainError):
    code = "INVALID_AMOUNT"
    default_message = "El monto del movimiento debe ser mayor que cero."


class TransactionTypeMismatch(DomainError):
    code = "TRANSACTION_TYPE_MISMATCH"
    default_message = "El tipo de movimiento no corresponde con el tipo de concepto."


class TransactionNotFound(DomainError):
    code = "TRANSACTION_NOT_FOUND"
    default_message = "El movimiento especificado no existe."
