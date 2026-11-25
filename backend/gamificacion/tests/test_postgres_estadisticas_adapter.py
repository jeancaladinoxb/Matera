import unittest
from datetime import datetime, timezone
from typing import Any, List, Optional, Tuple

import psycopg2

from backend.gamificacion.application.errors import (
    ErrorAccesoDatosGamificacionError,
)
from backend.gamificacion.infrastructure.adapters import (
    PostgresEstadisticasRepositoryAdapter,
)


REGISTRO = datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc)
VINCULACION = datetime(2026, 10, 1, 15, 0, tzinfo=timezone.utc)


class FakeCursor:
    def __init__(self, connection: "FakeConnection") -> None:
        self.connection = connection
        self.last_query = ""

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    def execute(self, query: str, parameters: Optional[Tuple[Any, ...]] = None) -> None:
        self.connection.statements.append((query, parameters))
        if self.connection.fail:
            raise psycopg2.OperationalError("database detail")
        if query == "SET TRANSACTION READ ONLY":
            self.connection.read_only = True
        elif not self.connection.read_only:
            raise AssertionError("Query was not executed in a read-only transaction.")
        self.last_query = query

    def fetchall(self) -> List[Tuple[Any, ...]]:
        if "FROM usuarios" in self.last_query:
            return self.connection.usuarios
        return self.connection.materas


class FakeConnection:
    def __init__(self, usuarios, materas) -> None:
        self.usuarios = usuarios
        self.materas = materas
        self.statements = []
        self.read_only = False
        self.fail = False
        self.rolled_back = False
        self.closed = False

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


class PostgresEstadisticasAdapterTests(unittest.TestCase):
    def _adapter(self, connection: FakeConnection):
        connections = []

        def factory():
            connection.read_only = False
            connections.append(connection)
            return connection

        return PostgresEstadisticasRepositoryAdapter(factory), connections

    def test_construye_estadisticas_con_consultas_parametrizadas(self) -> None:
        connection = FakeConnection([(7, REGISTRO)], [(VINCULACION,)])
        adapter, _ = self._adapter(connection)

        estadisticas = adapter.obtener_por_usuario(7)

        self.assertEqual(estadisticas.usuario_id, 7)
        self.assertEqual(estadisticas.fecha_registro, REGISTRO)
        self.assertEqual(estadisticas.fechas_vinculacion, (VINCULACION,))
        consultas = [s for s in connection.statements if s[0] != "SET TRANSACTION READ ONLY"]
        self.assertEqual(consultas[0][1], (7,))
        self.assertEqual(consultas[1][1], (7, "vinculada"))
        self.assertTrue(connection.closed)

    def test_usuario_inexistente_devuelve_none(self) -> None:
        adapter, _ = self._adapter(FakeConnection([], []))

        self.assertIsNone(adapter.obtener_por_usuario(7))

    def test_fechas_sin_zona_se_asumen_utc(self) -> None:
        connection = FakeConnection([(7, datetime(2026, 10, 1, 12))], [])
        adapter, _ = self._adapter(connection)

        self.assertEqual(adapter.obtener_por_usuario(7).fecha_registro, REGISTRO)

    def test_error_de_base_de_datos_se_traduce_y_no_filtra_detalles(self) -> None:
        connection = FakeConnection([], [])
        connection.fail = True
        adapter, _ = self._adapter(connection)

        with self.assertRaises(ErrorAccesoDatosGamificacionError) as contexto:
            adapter.obtener_por_usuario(7)

        self.assertNotIn("database detail", str(contexto.exception))
        self.assertTrue(connection.rolled_back)
        self.assertTrue(connection.closed)


if __name__ == "__main__":
    unittest.main()
