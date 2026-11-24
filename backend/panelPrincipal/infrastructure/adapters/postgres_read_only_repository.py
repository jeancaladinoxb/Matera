import logging
from typing import Any, Callable, List, Tuple

import psycopg2
from psycopg2.extensions import connection as PostgresqlConnection

from backend.panelPrincipal.application.errors import ErrorAccesoDatosPanelError


logger = logging.getLogger(__name__)


class PostgresReadOnlyRepository:
    def __init__(
        self,
        connection_factory: Callable[[], PostgresqlConnection],
    ) -> None:
        self._connection_factory = connection_factory

    def _execute(
        self, query: str, parameters: Tuple[Any, ...]
    ) -> List[Tuple[Any, ...]]:
        connection = None
        try:
            connection = self._connection_factory()
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute(query, parameters)
                rows = cursor.fetchall()
            connection.commit()
            return rows
        except psycopg2.Error as error:
            if connection is not None:
                connection.rollback()
            logger.error(
                "Panel PostgreSQL operation failed (%s, pgcode=%s).",
                type(error).__name__,
                error.pgcode,
            )
            raise ErrorAccesoDatosPanelError() from None
        finally:
            if connection is not None:
                connection.close()
