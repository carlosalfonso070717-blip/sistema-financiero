"""Control de acceso: la persona que llama sale del token, no de la operación."""
import jwt
from strawberry.types import Info

from app.core.errors import Unauthenticated
from app.core.security import leer_token
from app.models import CompanyUser


def leer_actor(info: Info) -> str:
    """Devuelve el id de la membresía del token después de validarlo.

    1. ¿Vino el encabezado y la firma es válida?  2. ¿exp todavía no pasó?
    3. ¿La membresía existe, está activa y su empresa es el companyId del token?
    El permiso de la ruta (paso 4) lo sigue decidiendo exigir_permiso con el rol activo.
    """
    db = info.context.db
    encabezado = info.context.request.headers.get("authorization", "")
    if not encabezado.lower().startswith("bearer "):
        raise Unauthenticated("Falta el token en el encabezado Authorization.")

    try:
        datos = leer_token(encabezado[len("bearer "):].strip())
    except jwt.PyJWTError:
        # Cubre una firma alterada y un token vencido.
        raise Unauthenticated("El token no es válido o ya venció.") from None

    membresia = db.get(CompanyUser, str(datos["companyUserId"]))
    if membresia is None or not membresia.is_active:
        raise Unauthenticated("La membresía del token no existe o no está activa.")
    if membresia.company_id != str(datos["companyId"]):
        raise Unauthenticated("El token no corresponde a esa empresa.")
    return membresia.id
