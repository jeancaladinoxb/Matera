import unittest
from typing import Any, List, Optional, Tuple

import psycopg2

from backend.panelPrincipal.application.errors import ErrorAccesoDatosPanelError
from backend.panelPrincipal.infrastructure.adapters import (
    PostgresMateraRepositoryAdapter,
    PostgresUsuarioRepositoryAdapter,
)


class FakeCursor:
    def __init__(self, connection: "FakeConnection") -> None:
        self.connection = connection

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

    def fetchall(self) -> List[Tuple[Any, ...]]:
        return self.connection.rows


class FakeConnection:
    def __init__(self, rows: List[Tuple[Any, ...]]) -> None:
        self.rows = rows
        self.statements = []
        self.read_only = False
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


class PostgresPanelAdapterTests(unittest.TestCase):
    def test_usuario_lookup_is_parameterized_and_read_only(self) -> None:
        connection = FakeConnection([(7, "Ana", "anap")])
        adapter = PostgresUsuarioRepositoryAdapter(lambda: connection)

        usuario = adapter.consultar_por_id(7)

        self.assertEqual((usuario.usuario_id, usuario.nombre, usuario.nickname), (7, "Ana", "anap"))
        self.assertEqual(
            connection.statements,
            [
                ("SET TRANSACTION READ ONLY", None),
                ("SELECT id, nombre, nickname FROM usuarios WHERE id = %s", (7,)),
            ],
        )
        self.assertTrue(connection.committed)
        self.assertTrue(connection.closed)

    def test_matera_lookup_filters_by_user_and_returns_all_linked_rows(self) -> None:
        connection = FakeConnection(
            [(12, "E072A1D55B18", None), (13, "246F28AB1234", 5)]
        )
        adapter = PostgresMateraRepositoryAdapter(lambda: connection)

        materas = adapter.listar_vinculadas_por_usuario(7)

        self.assertEqual(
            [(matera.matera_id, matera.dispositivo_id) for matera in materas],
            [(12, 12), (13, 13)],
        )
        self.assertEqual([matera.planta_id for matera in materas], [None, 5])
        query, parameters = connection.statements[1]
        self.assertIn("SELECT id, mac, planta_id FROM materas", query)
        self.assertIn("WHERE usuario_id = %s AND estado = %s", query)
        self.assertEqual(parameters, (7, "vinculada"))
        self.assertTrue(connection.read_only)
        self.assertTrue(connection.committed)
        self.assertTrue(connection.closed)

    def test_database_errors_are_wrapped_and_connection_is_rolled_back(self) -> None:
        connection = FakeConnection([])
        connection.fail = True
        adapter = PostgresUsuarioRepositoryAdapter(lambda: connection)

        with self.assertRaises(ErrorAccesoDatosPanelError):
            adapter.consultar_por_id(7)

        self.assertTrue(connection.rolled_back)
        self.assertTrue(connection.closed)


if __name__ == "__main__":
    unittest.main()
