import os
import unittest
import uuid

import psycopg2
import pytest

from backend.plantas.application.use_cases import VincularPlantaAMateraUseCase
from backend.plantas.domain import MateraNoEncontradaError, NivelLuz
from backend.plantas.infrastructure.adapters import (
    PostgresAsignacionPlantaAdapter,
    PostgresPlantaRepositoryAdapter,
)
from backend.usuarios.application.ports.errors import RepositoryError
from backend.usuarios.application.ports.output import TokenProviderPort


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
pytestmark = pytest.mark.integration

ESPECIES_INICIALES = {"monstera", "calathea", "sansevieria", "pothos", "bonsai"}


class FakeUserTokens(TokenProviderPort):
    def generar_token(self, usuario_id: int) -> str:
        return "user-token-{}".format(usuario_id)

    def verificar_token(self, token: str) -> int:
        return int(token.rsplit("-", 1)[1])


@unittest.skipUnless(
    TEST_DATABASE_URL,
    "Set TEST_DATABASE_URL to run PostgreSQL integration tests.",
)
class PostgresPlantasIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        suffix = uuid.uuid4().hex
        self.usuario_ids = [
            self._insert_user("planta-{}@example.test".format(suffix), "planta-{}".format(suffix)),
            self._insert_user("otra-{}@example.test".format(suffix), "otra-{}".format(suffix)),
        ]
        self.macs = [uuid.uuid4().hex[:12].upper() for _ in range(4)]
        # 0 y 1: vinculadas al usuario 0 · 2: vinculada al usuario 1 · 3: sin reclamar
        self._execute(
            """
            INSERT INTO materas (mac, usuario_id, estado, fecha_vinculacion)
            VALUES (%s, %s, 'vinculada', now()),
                   (%s, %s, 'vinculada', now()),
                   (%s, %s, 'vinculada', now())
            """,
            (
                self.macs[0], self.usuario_ids[0],
                self.macs[1], self.usuario_ids[0],
                self.macs[2], self.usuario_ids[1],
            ),
        )
        self._execute("INSERT INTO materas (mac) VALUES (%s)", (self.macs[3],))
        self.matera_ids = [self._matera_id(mac) for mac in self.macs]

        factory = lambda: psycopg2.connect(TEST_DATABASE_URL)
        self.catalogo = PostgresPlantaRepositoryAdapter(factory)
        self.asignacion = PostgresAsignacionPlantaAdapter(factory)
        plantas = {planta.slug: planta.id for planta in self.catalogo.listar()}
        self.monstera, self.pothos = plantas["monstera"], plantas["pothos"]

    def tearDown(self) -> None:
        self._execute("DELETE FROM materas WHERE mac = ANY(%s)", (self.macs,))
        self._execute("DELETE FROM usuarios WHERE id = ANY(%s)", (self.usuario_ids,))

    # Catálogo

    def test_listar_devuelve_las_especies_iniciales_ordenadas(self) -> None:
        plantas = self.catalogo.listar()

        self.assertTrue(ESPECIES_INICIALES <= {planta.slug for planta in plantas})
        self.assertEqual([p.id for p in plantas], sorted(p.id for p in plantas))
        bonsai = next(p for p in plantas if p.slug == "bonsai")
        self.assertEqual(bonsai.nombre_cientifico, "Ficus microcarpa")
        self.assertIs(bonsai.luz, NivelLuz.DIRECTA)

    def test_buscar_por_id(self) -> None:
        self.assertEqual(self.catalogo.buscar_por_id(self.monstera).slug, "monstera")
        self.assertIsNone(self.catalogo.buscar_por_id(2147483647))
        self.assertIsNone(self.catalogo.buscar_por_id(2147483648))

    # Asignación

    def test_asigna_a_una_matera_propia_vinculada(self) -> None:
        self.assertTrue(self.asignacion.asignar(self.usuario_ids[0], self.matera_ids[0], self.monstera))

        self.assertEqual(self._planta_de(0), self.monstera)
        self.assertIsNone(self._planta_de(1))

    def test_elegir_otra_planta_reemplaza_y_repetir_es_valido(self) -> None:
        usuario, matera = self.usuario_ids[0], self.matera_ids[0]

        self.assertTrue(self.asignacion.asignar(usuario, matera, self.monstera))
        self.assertTrue(self.asignacion.asignar(usuario, matera, self.pothos))
        self.assertEqual(self._planta_de(0), self.pothos)
        self.assertTrue(self.asignacion.asignar(usuario, matera, self.pothos))
        self.assertEqual(self._planta_de(0), self.pothos)

    def test_no_asigna_a_la_matera_de_otro_usuario(self) -> None:
        self.assertFalse(self.asignacion.asignar(self.usuario_ids[0], self.matera_ids[2], self.monstera))

        self.assertIsNone(self._planta_de(2))

    def test_no_asigna_a_una_matera_sin_reclamar(self) -> None:
        self.assertFalse(self.asignacion.asignar(self.usuario_ids[0], self.matera_ids[3], self.monstera))

        self.assertIsNone(self._planta_de(3))

    def test_matera_inexistente_o_fuera_de_rango(self) -> None:
        self.assertFalse(self.asignacion.asignar(self.usuario_ids[0], 2147483647, self.monstera))
        self.assertFalse(self.asignacion.asignar(self.usuario_ids[0], 2147483648, self.monstera))

    def test_planta_inexistente_lo_impide_la_clave_foranea(self) -> None:
        with self.assertRaises(RepositoryError):
            self.asignacion.asignar(self.usuario_ids[0], self.matera_ids[0], 2147483647)

        self.assertIsNone(self._planta_de(0))

    def test_caso_de_uso_con_adaptadores_reales(self) -> None:
        use_case = VincularPlantaAMateraUseCase(self.catalogo, self.asignacion, FakeUserTokens())
        token = "user-token-{}".format(self.usuario_ids[0])

        use_case.vincular(token, self.matera_ids[1], self.pothos)
        with self.assertRaises(MateraNoEncontradaError):
            use_case.vincular(token, self.matera_ids[2], self.pothos)

        self.assertEqual(self._planta_de(1), self.pothos)
        self.assertIsNone(self._planta_de(2))

    # Ayudas

    def _planta_de(self, indice: int):
        return self._fetch("SELECT planta_id FROM materas WHERE id = %s", (self.matera_ids[indice],))[0][0]

    def _matera_id(self, mac: str) -> int:
        return self._fetch("SELECT id FROM materas WHERE mac = %s", (mac,))[0][0]

    def _insert_user(self, correo: str, nickname: str) -> int:
        return self._fetch(
            """
            INSERT INTO usuarios (nombre, apellido, nickname, correo, password_hash)
            VALUES ('Planta', 'Test', %s, %s, 'test-hash')
            RETURNING id
            """,
            (nickname, correo),
        )[0][0]

    @staticmethod
    def _fetch(query: str, parameters: tuple):
        connection = psycopg2.connect(TEST_DATABASE_URL)
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, parameters)
                filas = cursor.fetchall()
            connection.commit()
            return filas
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
