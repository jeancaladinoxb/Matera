import logging
from typing import Any, Callable, List, Tuple

import psycopg2
from psycopg2.extensions import connection as PostgresqlConnection

from backend.usuarios.application.ports.errors import RepositoryError


logger = logging.getLogger(__name__)

# Mayor valor de una columna INTEGER de PostgreSQL: un id mayor no puede existir
ID_MAXIMO = 2147483647


def ejecutar(
    connection_factory: Callable[[], PostgresqlConnection],
    query: str,
    parameters: Tuple[Any, ...],
    *,
    leer_filas: bool = False,
) -> Tuple[List[Tuple[Any, ...]], int]:
    """Run one parameterized statement on its own connection; return (rows, rowcount)."""
    connection = None
    try:
        connection = connection_factory()
        with connection.cursor() as cursor:
            cursor.execute(query, parameters)
            filas = cursor.fetchall() if leer_filas else []
            rowcount = cursor.rowcount
        connection.commit()
        return filas, rowcount
    except psycopg2.Error as error:
        if connection is not None:
            connection.rollback()
        # pgcode is the SQLSTATE and carries no user data; never log str(error).
        logger.error(
            "PostgreSQL plantas operation failed (%s, pgcode=%s).",
            type(error).__name__,
            error.pgcode,
        )
        raise RepositoryError("La operación de persistencia falló.") from None
    finally:
        if connection is not None:
            connection.close()
