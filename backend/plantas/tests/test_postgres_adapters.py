import unittest
from typing import Any, List, Optional, Tuple

import psycopg2

from backend.plantas.domain import NivelLuz, NivelRiego
from backend.plantas.infrastructure.adapters import (
    PostgresAsignacionPlantaAdapter,
    PostgresPlantaRepositoryAdapter,
)
from backend.usuarios.application.ports.errors import RepositoryError

FILA_MONSTERA = (1, "monstera", "Monstera", "Monstera deliciosa", "indirecta", "moderado", 40, 60, 18, 30, 8000, 20000)
FILA_BONSAI = (5, "bonsai", "Bonsai", "Ficus microcarpa", "directa", "moderado", 40, 60, 15, 28, 10000, 30000)


class FakeCursor:
    def __init__(self, connection: "FakeConnection") -> None:
        self.connection = connection

    def __enter__(self) -> "FakeCursor":
        return self

    def __exit__(self, *args: Any) -> None:
        return None

    @property
    def rowcount(self) -> int:
        return self.connection.rowcount

    def execute(self, query: str, parameters: Optional[Tuple[Any, ...]] = None) -> None:
        self.connection.statements.append((query, parameters))
        if self.connection.fail:
            raise psycopg2.OperationalError("database detail")

    def fetchall(self) -> List[Tuple[Any, ...]]:
        return self.connection.rows


class FakeConnection:
    def __init__(self, rows: Optional[List[Tuple[Any, ...]]] = None, rowcount: int = 0) -> None:
        self.rows = rows or []
        self.rowcount = rowcount
        self.statements = []
        self.fail = False
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


class PostgresPlantaRepositoryAdapterTests(unittest.TestCase):
    def test_listar_traduce_las_filas_a_plantas(self) -> None:
        connection = FakeConnection([FILA_MONSTERA, FILA_BONSAI])

        plantas = PostgresPlantaRepositoryAdapter(lambda: connection).listar()

        self.assertEqual([p.id for p in plantas], [1, 5])
        self.assertEqual(plantas[0].slug, "monstera")
        self.assertIs(plantas[0].luz, NivelLuz.INDIRECTA)
        self.assertIs(plantas[1].riego, NivelRiego.MODERADO)
        self.assertEqual((plantas[0].humedad_suelo_min, plantas[0].luz_lux_max), (40, 20000))
        query, parameters = connection.statements[0]
        self.assertIn("FROM plantas ORDER BY id", query)
        self.assertEqual(parameters, ())
        self.assertTrue(connection.committed)
        self.assertTrue(connection.closed)

    def test_buscar_por_id_esta_parametrizado(self) -> None:
        connection = FakeConnection([FILA_BONSAI])

        planta = PostgresPlantaRepositoryAdapter(lambda: connection).buscar_por_id(5)

        self.assertEqual(planta.nombre_cientifico, "Ficus microcarpa")
        query, parameters = connection.statements[0]
        self.assertIn("WHERE id = %s", query)
        self.assertEqual(parameters, (5,))
        self.assertTrue(connection.closed)

    def test_buscar_por_id_inexistente_es_none(self) -> None:
        connection = FakeConnection([])

        self.assertIsNone(PostgresPlantaRepositoryAdapter(lambda: connection).buscar_por_id(99))

    def test_id_fuera_del_rango_de_integer_no_consulta(self) -> None:
        def sin_conexion():
            raise AssertionError("No debe abrir una conexión")

        self.assertIsNone(PostgresPlantaRepositoryAdapter(sin_conexion).buscar_por_id(2147483648))

    def test_errores_de_base_de_datos_se_envuelven_y_se_revierte(self) -> None:
        connection = FakeConnection()
        connection.fail = True

        with self.assertRaises(RepositoryError) as ctx:
            PostgresPlantaRepositoryAdapter(lambda: connection).listar()

        self.assertNotIn("database detail", str(ctx.exception))
        self.assertTrue(connection.rolled_back)
        self.assertTrue(connection.closed)


class PostgresAsignacionPlantaAdapterTests(unittest.TestCase):
    def test_asignar_es_una_sola_sentencia_atomica_y_parametrizada(self) -> None:
        connection = FakeConnection(rowcount=1)

        resultado = PostgresAsignacionPlantaAdapter(lambda: connection).asignar(7, 12, 3)

        self.assertTrue(resultado)
        self.assertEqual(len(connection.statements), 1)
        query, parameters = connection.statements[0]
        self.assertIn("UPDATE materas SET planta_id = %s", query)
        self.assertIn("WHERE id = %s AND usuario_id = %s AND estado = 'vinculada'", query)
        self.assertEqual(parameters, (3, 12, 7))
        self.assertTrue(connection.committed)
        self.assertTrue(connection.closed)

    def test_sin_filas_afectadas_es_false(self) -> None:
        connection = FakeConnection(rowcount=0)

        self.assertFalse(PostgresAsignacionPlantaAdapter(lambda: connection).asignar(7, 12, 3))

    def test_ids_fuera_del_rango_de_integer_no_consultan(self) -> None:
        def sin_conexion():
            raise AssertionError("No debe abrir una conexión")

        adapter = PostgresAsignacionPlantaAdapter(sin_conexion)

        self.assertFalse(adapter.asignar(7, 2147483648, 3))
        self.assertFalse(adapter.asignar(7, 12, 2147483648))

    def test_errores_de_base_de_datos_se_envuelven_y_se_revierte(self) -> None:
        connection = FakeConnection()
        connection.fail = True

        with self.assertRaises(RepositoryError) as ctx:
            PostgresAsignacionPlantaAdapter(lambda: connection).asignar(7, 12, 3)

        self.assertNotIn("database detail", str(ctx.exception))
        self.assertTrue(connection.rolled_back)
        self.assertTrue(connection.closed)


if __name__ == "__main__":
    unittest.main()
