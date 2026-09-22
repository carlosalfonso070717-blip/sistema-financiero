"""Validaciones de entrada compartidas entre servicios."""
from email_validator import EmailNotValidError, validate_email

from app.core.errors import ValidationError

MIN_PASSWORD_LENGTH = 8


def clean_text(value: str | None, field: str, min_len: int = 1, max_len: int = 150) -> str:
    if value is None or not value.strip():
        raise ValidationError(f"El campo '{field}' es obligatorio.")
    cleaned = value.strip()
    if not (min_len <= len(cleaned) <= max_len):
        raise ValidationError(
            f"El campo '{field}' debe tener entre {min_len} y {max_len} caracteres."
        )
    return cleaned


def normalize_email(value: str) -> str:
    """Normaliza a minúsculas antes de comparar y guardar.
    """
    try:
        result = validate_email(value.strip(), check_deliverability=False)
    except EmailNotValidError as exc:
        raise ValidationError(f"El correo electrónico no es válido: {exc}") from exc
    return result.normalized.lower()


def validate_password(value: str) -> str:
    if value is None or len(value) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres."
        )
    return value
