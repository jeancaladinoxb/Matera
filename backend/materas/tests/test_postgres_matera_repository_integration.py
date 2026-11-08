import os
import threading
import unittest
import uuid

import psycopg2
import pytest

from backend.materas.domain import EstadoMatera, Mac, Matera
from backend.materas.infrastructure.adapters import PostgresMateraRepositoryAdapter


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.integration


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "Set TEST_DATABASE_URL to run PostgreSQL integration tests.",
)
class PostgresMateraRepositoryIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.mac = Mac(uuid.uuid4().hex[:12])
        self.email = "matera-test-{}@example.test".format(uuid.uuid4().hex)
        self.repository = PostgresMateraRepositoryAdapter(
            connection_factory=lambda: psycopg2.connect(TEST_DATABASE_URL)
        )
        self.user_ids = [self._insert_user(self.email), self._insert_user("2" + self.email)]

    def tearDown(self) -> None:
        self._run("DELETE FROM materas WHERE mac = %s", (self.mac.value,))
        self._run("DELETE FROM usuarios WHERE id = ANY(%s)", (self.user_ids,))

    def test_registrar_is_idempotent_and_does_not_overwrite(self) -> None:
        self.assertTrue(self.repository.registrar(Matera(self.mac)))
        self.assertTrue(self.repository.reclamar(self.mac, self.user_ids[0]))
        self.assertFalse(self.repository.registrar(Matera(self.mac)))
        self.assertEqual(self.repository.buscar_por_mac(self.mac).usuario_id, self.user_ids[0])

    def test_buscar_por_mac(self) -> None:
        self.assertIsNone(self.repository.buscar_por_mac(self.mac))
        self.repository.registrar(Matera(self.mac))
        matera = self.repository.buscar_por_mac(self.mac)
        self.assertEqual(matera.estado, EstadoMatera.SIN_RECLAMAR)
        self.assertIsNone(matera.usuario_id)

    def test_reclamar_links_once(self) -> None:
        self.repository.registrar(Matera(self.mac))
        self.assertTrue(self.repository.reclamar(self.mac, self.user_ids[0]))
        self.assertFalse(self.repository.reclamar(self.mac, self.user_ids[1]))
        matera = self.repository.buscar_por_mac(self.mac)
        self.assertEqual(matera.estado, EstadoMatera.VINCULADA)
        self.assertEqual(matera.usuario_id, self.user_ids[0])
        self.assertIsNotNone(matera.fecha_vinculacion)

    def test_reclamar_unknown_mac_is_false(self) -> None:
        self.assertFalse(self.repository.reclamar(self.mac, self.user_ids[0]))

    def test_concurrent_claims_have_a_single_winner(self) -> None:
        self.repository.registrar(Matera(self.mac))
        results = []
        barrier = threading.Barrier(2)

        def claim(user_id: int) -> None:
            barrier.wait()
            results.append(self.repository.reclamar(self.mac, user_id))

        threads = [threading.Thread(target=claim, args=(uid,)) for uid in self.user_ids]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(sorted(results), [False, True])

    def _insert_user(self, correo: str) -> int:
        connection = psycopg2.connect(TEST_DATABASE_URL)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO usuarios (nombre, apellido, nickname, correo, password_hash) "
                    "VALUES ('P', 'I', 'p', %s, 'hash') RETURNING id",
                    (correo,),
                )
                user_id = cursor.fetchone()[0]
            connection.commit()
            return user_id
        finally:
            connection.close()

    def _run(self, query: str, params) -> None:
        connection = psycopg2.connect(TEST_DATABASE_URL)
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
            connection.commit()
        finally:
            connection.close()


if __name__ == "__main__":
    unittest.main()
