from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.config import settings

ALGORITMO = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _secreto() -> str:
    """El secreto vive en la variable de ambiente JWT_SECRET, nunca en el código."""
    if not settings.jwt_secret:
        raise RuntimeError(
            "Falta la variable de ambiente JWT_SECRET. Genera una con: "
            'python -c "import secrets; print(secrets.token_hex(32))" '
            "y guárdala en el archivo .env."
        )
    return settings.jwt_secret


def crear_token(company_user_id: str, company_id: str, minutos: int | None = None) -> str:
    """Firma el token con la membresía, su empresa y el vencimiento.

    No lleva la contraseña, el hash ni los permisos: el rol se lee en cada petición.
    """
    ahora = datetime.now(timezone.utc)
    vigencia = settings.access_token_expire_minutes if minutos is None else minutos
    datos = {
        "companyUserId": str(company_user_id),
        "companyId": str(company_id),
        "exp": ahora + timedelta(minutes=vigencia),
    }
    return jwt.encode(datos, _secreto(), algorithm=ALGORITMO)


def leer_token(token: str) -> dict:
    """Valida firma y vencimiento. Solo se acepta HS256. Lanza jwt.PyJWTError si falla."""
    return jwt.decode(
        token,
        _secreto(),
        algorithms=[ALGORITMO],
        options={"require": ["exp", "companyUserId", "companyId"]},
    )
