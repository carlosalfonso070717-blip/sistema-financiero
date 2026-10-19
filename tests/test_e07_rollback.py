"""E07: un fallo después de modificar relaciones y antes del commit revierte todo.

Ejecutar desde la raíz del proyecto:
    python -m unittest tests.test_e07_rollback -v
"""
import os
import tempfile
import unittest
from unittest import mock

# Base de datos temporal: la prueba no toca financial.db.
_tmp = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmp.name, 'e07.db')}"
os.environ.setdefault("JWT_SECRET", "secreto-solo-para-pruebas")

from sqlalchemy import select  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Permission, Role, RolePermission  # noqa: E402
from app.services import company_service, role_service, user_service  # noqa: E402

S0 = ["accounts.read", "concepts.read", "transactions.read", "transactions.write"]
S1 = S0 + ["accounts.write"]


def relaciones(db, role_code):
    """Estado persistido de las relaciones del rol: {codigo: (id_relacion, activa)}."""
    rows = db.execute(
        select(Permission.code, RolePermission.id, RolePermission.is_active)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .where(Role.code == role_code)
    )
    return {code: (rel_id, active) for code, rel_id, active in rows}


class E07ReversionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            role_service.seed_access_catalog(db)
            company = company_service.create_company(db, name="Empresa E07")
            ana = user_service.create_company_admin(
                db, company_id=company.id, name="Ana", email="ana@laboratorio-e07.com",
                password="Laboratorio1",
            )
            cls.ana_id = ana.id
            cls.capturista_id = role_service.get_role_by_code_or_fail(db, "CAPTURISTA").id
            cls.ids = {p.code: p.id for p in db.scalars(select(Permission))}

    @classmethod
    def tearDownClass(cls):
        engine.dispose()
        _tmp.cleanup()

    def test_fallo_antes_del_commit_revierte_todo(self):
        with SessionLocal() as db:
            antes = relaciones(db, "CAPTURISTA")
        self.assertEqual({c for c, (_, a) in antes.items() if a}, set(S0))

        # Lista deseada: quita transactions.write y agrega accounts.write y
        # concepts.write. Son tres escrituras en la misma transacción.
        deseada = ["accounts.read", "concepts.read", "transactions.read",
                   "accounts.write", "concepts.write"]
        punto_de_fallo = {}

        with SessionLocal() as db:
            def commit_que_falla():
                # El flush ya se hizo: la sesión ve los cambios pendientes.
                pendiente = relaciones(db, "CAPTURISTA")
                punto_de_fallo["activas"] = {c for c, (_, a) in pendiente.items() if a}
                raise RuntimeError("Fallo controlado antes del commit")

            with mock.patch.object(db, "commit", side_effect=commit_que_falla):
                with self.assertRaises(RuntimeError):
                    role_service.set_role_permissions(
                        db,
                        actor_company_user_id=self.ana_id,
                        role_id=self.capturista_id,
                        permission_ids=[self.ids[c] for c in deseada],
                    )

        # En el punto de fallo los cambios ya estaban escritos (flush), sin confirmar.
        self.assertEqual(punto_de_fallo["activas"], set(deseada))

        # Una sesión nueva lee lo persistido: la configuración previa, intacta.
        with SessionLocal() as db:
            despues = relaciones(db, "CAPTURISTA")
        self.assertEqual(despues, antes)
        self.assertEqual({c for c, (_, a) in despues.items() if a}, set(S0))

    def test_aplicacion_normal_si_confirma(self):
        """Control: sin fallo, la misma operación sí persiste y luego se restaura."""
        with SessionLocal() as db:
            role_service.set_role_permissions(
                db, actor_company_user_id=self.ana_id, role_id=self.capturista_id,
                permission_ids=[self.ids[c] for c in S1],
            )
        with SessionLocal() as db:
            activas = {c for c, (_, a) in relaciones(db, "CAPTURISTA").items() if a}
        self.assertEqual(activas, set(S1))

        with SessionLocal() as db:
            role_service.set_role_permissions(
                db, actor_company_user_id=self.ana_id, role_id=self.capturista_id,
                permission_ids=[self.ids[c] for c in S0],
            )


if __name__ == "__main__":
    unittest.main()
