import os
import unittest
import uuid

import psycopg2
import pytest

from backend.panelPrincipal.infrastructure.adapters import (
    PostgresMateraRepositoryAdapter,
    PostgresUsuarioRepositoryAdapter,
)


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.integration


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "Set TEST_DATABASE_URL to run PostgreSQL integration tests.",
)
class PostgresPanelIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        suffix = uuid.uuid4().hex
        self.usuario_ids = [
            self._insert_user("panel-{}@example.test".format(suffix), "panel-{}".format(suffix)),
            self._insert_user("other-{}@example.test".format(suffix), "other-{}".format(suffix)),
        ]
        self.macs = [uuid.uuid4().hex[:12].upper() for _ in range(3)]
        self._execute(
            """
            INSERT INTO materas (mac, usuario_id, estado, fecha_vinculacion)
            VALUES
                (%s, %s, 'vinculada', now()),
                (%s, %s, 'vinculada', now()),
                (%s, %s, 'vinculada', now())
            """,
            (
                self.macs[0],
                self.usuario_ids[0],
                self.macs[1],
                self.usuario_ids[0],
                self.macs[2],
                self.usuario_ids[1],
            ),
        )
        self.usuario_repository = PostgresUsuarioRepositoryAdapter(
            lambda: psycopg2.connect(TEST_DATABASE_URL)
        )
        self.matera_repository = PostgresMateraRepositoryAdapter(
            lambda: psycopg2.connect(TEST_DATABASE_URL)
        )

    def tearDown(self) -> None:
        self._execute("DELETE FROM materas WHERE mac = ANY(%s)", (self.macs,))
        self._execute(
            "DELETE FROM usuarios WHERE id = ANY(%s)", (self.usuario_ids,)
        )

    def test_reads_user_and_only_their_linked_materas(self) -> None:
        usuario = self.usuario_repository.consultar_por_id(self.usuario_ids[0])
        materas = self.matera_repository.listar_vinculadas_por_usuario(
            self.usuario_ids[0]
        )

        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.usuario_id, self.usuario_ids[0])
        self.assertEqual(
            {matera.mac for matera in materas},
            {self.macs[0], self.macs[1]},
        )
        self.assertTrue(all(matera.planta_id is None for matera in materas))

    def _insert_user(self, correo: str, nickname: str) -> int:
        connection = psycopg2.connect(TEST_DATABASE_URL)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO usuarios (nombre, apellido, nickname, correo, password_hash)
                    VALUES ('Panel', 'Test', %s, %s, 'test-hash')
                    RETURNING id
                    """,
                    (nickname, correo),
                )
                usuario_id = cursor.fetchone()[0]
            connection.commit()
            return usuario_id
        finally:
            connection.close()

    @staticmethod
    def _execute(query: str, parameters: tuple) -> None:
        connection = psycopg2.connect(TEST_DATABASE_URL)
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, parameters)
            connection.commit()
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
