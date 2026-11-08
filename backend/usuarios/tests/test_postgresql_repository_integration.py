import os
import unittest
import uuid

import psycopg2
import pytest

from backend.usuarios.application.ports.output import CredencialesUsuario
from backend.usuarios.domain import Email, EmailAlreadyRegisteredError, Password, Usuario
from backend.usuarios.infrastructure.adapters import PostgresqlRepositoryAdapter


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.integration


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "Set TEST_DATABASE_URL to run PostgreSQL integration tests.",
)
class PostgresqlRepositoryIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.email = "repository-test-{}@example.test".format(uuid.uuid4().hex)
        self.repository = PostgresqlRepositoryAdapter(
            connection_factory=lambda: psycopg2.connect(TEST_DATABASE_URL)
        )
        self.usuario = Usuario(
            nombre="Prueba",
            apellido="Integracion",
            nickname="prueba",
            correo=Email(self.email),
            contrasena=Password("Clave123"),
        )

    def tearDown(self) -> None:
        connection = psycopg2.connect(TEST_DATABASE_URL)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM usuarios WHERE correo = %s",
                    (self.email,),
                )
            connection.commit()
        finally:
            connection.close()

    def test_guardar_returns_different_ids(self) -> None:
        first_id = self.repository.guardar(self.usuario, "hash-1")
        second_user = Usuario(
            nombre="Prueba",
            apellido="Integracion",
            nickname="prueba",
            correo=Email(
                "repository-test-{}@example.test".format(uuid.uuid4().hex)
            ),
            contrasena=Password("Clave123"),
        )
        self.addCleanup(self._delete_email, second_user.correo.value)
        second_id = self.repository.guardar(second_user, "hash-2")

        self.assertNotEqual(first_id, second_id)

    def test_duplicate_email_raises_email_already_registered(self) -> None:
        self.repository.guardar(self.usuario, "hash-1")

        with self.assertRaises(EmailAlreadyRegisteredError):
            self.repository.guardar(self.usuario, "hash-2")

    def test_obtener_credenciales_for_existing_and_unknown_email(self) -> None:
        usuario_id = self.repository.guardar(self.usuario, "hash-1")

        credentials = self.repository.obtener_credenciales(self.usuario.correo)
        self.assertEqual(
            credentials,
            CredencialesUsuario(usuario_id=usuario_id, password_hash="hash-1"),
        )
        self.assertIsNone(
            self.repository.obtener_credenciales(Email("missing@example.test"))
        )

    def _delete_email(self, correo: str) -> None:
        connection = psycopg2.connect(TEST_DATABASE_URL)
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM usuarios WHERE correo = %s", (correo,))
            connection.commit()
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
