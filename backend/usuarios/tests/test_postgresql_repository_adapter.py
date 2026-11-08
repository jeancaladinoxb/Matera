import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

import psycopg2

from backend.usuarios.application.ports.errors import RepositoryError
from backend.usuarios.domain import Email, EmailAlreadyRegisteredError, Password, Usuario
from backend.usuarios.infrastructure.adapters import PostgresqlRepositoryAdapter


class EmailUniqueViolation(psycopg2.errors.UniqueViolation):
    @property
    def diag(self):
        return SimpleNamespace(constraint_name="usuarios_correo_un")


class PostgresqlRepositoryAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = MagicMock()
        self.cursor = self.connection.cursor.return_value.__enter__.return_value
        self.adapter = PostgresqlRepositoryAdapter(
            connection_factory=lambda: self.connection
        )
        self.usuario = Usuario(
            nombre="Ana",
            apellido="Pérez",
            nickname="anap",
            correo=Email(" Ana@Example.COM "),
            contrasena=Password("Clave123"),
        )

    def test_guardar_uses_parameters_commits_and_closes_connection(self) -> None:
        self.cursor.fetchone.return_value = (42,)

        result = self.adapter.guardar(self.usuario, "argon-hash")

        self.assertEqual(result, 42)
        query, parameters = self.cursor.execute.call_args.args
        self.assertIn("INSERT INTO usuarios", query)
        self.assertIn("RETURNING id", query)
        self.assertEqual(
            parameters,
            ("Ana", "Pérez", "anap", "ana@example.com", "argon-hash"),
        )
        self.connection.commit.assert_called_once_with()
        self.connection.close.assert_called_once_with()

    def test_existe_por_correo_uses_normalized_parameter(self) -> None:
        self.cursor.fetchone.return_value = (True,)

        self.assertTrue(self.adapter.existe_por_correo(self.usuario.correo))

        query, parameters = self.cursor.execute.call_args.args
        self.assertIn("WHERE correo = %s", query)
        self.assertEqual(parameters, ("ana@example.com",))

    def test_obtener_credenciales_returns_id_and_hash(self) -> None:
        self.cursor.fetchone.return_value = (42, "argon-hash")

        credentials = self.adapter.obtener_credenciales(self.usuario.correo)

        self.assertEqual(credentials.usuario_id, 42)
        self.assertEqual(credentials.password_hash, "argon-hash")
        query, parameters = self.cursor.execute.call_args.args
        self.assertEqual(parameters, ("ana@example.com",))

    def test_obtener_credenciales_returns_none_for_unknown_email(self) -> None:
        self.cursor.fetchone.return_value = None

        self.assertIsNone(
            self.adapter.obtener_credenciales(Email("unknown@example.com"))
        )

    def test_duplicate_email_rolls_back_and_raises_domain_error(self) -> None:
        self.cursor.execute.side_effect = EmailUniqueViolation(
            "duplicate key for ana@example.com"
        )

        with self.assertRaises(EmailAlreadyRegisteredError):
            self.adapter.guardar(self.usuario, "argon-hash")

        self.connection.rollback.assert_called_once_with()
        self.connection.commit.assert_not_called()
        self.connection.close.assert_called_once_with()

    def test_other_database_errors_are_logged_without_error_details(self) -> None:
        self.cursor.execute.side_effect = psycopg2.OperationalError(
            "sensitive database detail"
        )

        with self.assertLogs("backend.usuarios.infrastructure.adapters.postgresql_repository_adapter") as captured:
            with self.assertRaises(RepositoryError):
                self.adapter.existe_por_correo(self.usuario.correo)

        self.assertNotIn("sensitive database detail", "\n".join(captured.output))
        self.connection.rollback.assert_called_once_with()
        self.connection.close.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
