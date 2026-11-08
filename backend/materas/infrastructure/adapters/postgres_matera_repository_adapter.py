import logging
from typing import Any, Callable, Optional, Tuple

import psycopg2
from psycopg2.extensions import connection as PostgresqlConnection

from backend.materas.application.ports.output import MateraRepositoryPort
from backend.materas.domain import EstadoMatera, Mac, Matera
from backend.usuarios.application.ports.errors import RepositoryError


logger = logging.getLogger(__name__)


class PostgresMateraRepositoryAdapter(MateraRepositoryPort):
    def __init__(
        self,
        connection_factory: Callable[[], PostgresqlConnection],
    ) -> None:
        self._connection_factory = connection_factory

    def buscar_por_mac(self, mac: Mac) -> Optional[Matera]:
        row, _ = self._execute(
            "SELECT mac, usuario_id, estado, fecha_vinculacion "
            "FROM materas WHERE mac = %s",
            (mac.value,),
            fetch_one=True,
        )
        if row is None:
            return None
        return Matera(
            mac=Mac(row[0]),
            usuario_id=row[1],
            estado=EstadoMatera(row[2]),
            fecha_vinculacion=row[3],
        )

    def registrar(self, matera: Matera) -> bool:
        _, rowcount = self._execute(
            """
            INSERT INTO materas (mac, usuario_id, estado, fecha_vinculacion)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (mac) DO NOTHING
            """,
            (
                matera.mac.value,
                matera.usuario_id,
                matera.estado.value,
                matera.fecha_vinculacion,
            ),
        )
        return rowcount == 1

    def reclamar(self, mac: Mac, usuario_id: int) -> bool:
        # One statement: the WHERE clause makes the claim atomic, so of two
        # concurrent requests only one can update a row.
        _, rowcount = self._execute(
            """
            UPDATE materas
            SET usuario_id = %s, estado = 'vinculada', fecha_vinculacion = now()
            WHERE mac = %s AND usuario_id IS NULL
            """,
            (usuario_id, mac.value),
        )
        return rowcount == 1

    def _execute(
        self,
        query: str,
        parameters: Tuple[Any, ...],
        *,
        fetch_one: bool = False,
    ) -> Tuple[Any, int]:
        connection = None
        try:
            connection = self._connection_factory()
            with connection.cursor() as cursor:
                cursor.execute(query, parameters)
                row = cursor.fetchone() if fetch_one else None
                rowcount = cursor.rowcount
            connection.commit()
            return row, rowcount
        except psycopg2.Error as error:
            if connection is not None:
                connection.rollback()
            # pgcode is the SQLSTATE and carries no user data; never log str(error).
            logger.error(
                "PostgreSQL matera operation failed (%s, pgcode=%s).",
                type(error).__name__,
                error.pgcode,
            )
            raise RepositoryError("La operación de persistencia falló.") from None
        finally:
            if connection is not None:
                connection.close()
