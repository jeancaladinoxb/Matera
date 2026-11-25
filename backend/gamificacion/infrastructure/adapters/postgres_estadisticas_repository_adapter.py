import logging
from datetime import timezone
from typing import Any, Callable, List, Optional, Tuple

import psycopg2
from psycopg2.extensions import connection as PostgresqlConnection

from backend.gamificacion.application.errors import (
    ErrorAccesoDatosGamificacionError,
)
from backend.gamificacion.application.ports.output import (
    EstadisticasRepositoryPort,
)
from backend.gamificacion.domain import EstadisticasJardinero


logger = logging.getLogger(__name__)


class PostgresEstadisticasRepositoryAdapter(EstadisticasRepositoryPort):
    """Lee los hechos del jardinero desde las tablas usuarios y materas.

    No escribe nada: los logros se calculan a partir de los datos existentes.
    `usuarios.fecha_creacion` es TIMESTAMP sin zona, por eso se convierte a
    TIMESTAMPTZ con la zona de la sesión (la misma con la que `now()` lo guardó).
    """

    def __init__(
        self,
        connection_factory: Callable[[], PostgresqlConnection],
    ) -> None:
        self._connection_factory = connection_factory

    def obtener_por_usuario(
        self, usuario_id: int
    ) -> Optional[EstadisticasJardinero]:
        usuarios = self._execute(
            "SELECT id, fecha_creacion::timestamptz FROM usuarios WHERE id = %s",
            (usuario_id,),
        )
        if not usuarios:
            return None

        vinculaciones = self._execute(
            "SELECT fecha_vinculacion FROM materas "
            "WHERE usuario_id = %s AND estado = %s "
            "ORDER BY fecha_vinculacion",
            (usuario_id, "vinculada"),
        )
        return EstadisticasJardinero(
            usuario_id=int(usuarios[0][0]),
            fecha_registro=_con_zona(usuarios[0][1]),
            fechas_vinculacion=tuple(_con_zona(row[0]) for row in vinculaciones),
        )

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
                "Gamification PostgreSQL operation failed (%s, pgcode=%s).",
                type(error).__name__,
                error.pgcode,
            )
            raise ErrorAccesoDatosGamificacionError() from None
        finally:
            if connection is not None:
                connection.close()


def _con_zona(fecha):
    # Defensa extra: si el driver devolviera una fecha sin zona, se asume UTC.
    if fecha is not None and fecha.tzinfo is None:
        return fecha.replace(tzinfo=timezone.utc)
    return fecha
