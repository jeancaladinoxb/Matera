import logging
import os
from typing import Any, Callable, Dict, Optional, Tuple

import psycopg2
import psycopg2.errors
from psycopg2.extensions import connection as PostgresqlConnection

from backend.usuarios.application.ports.errors import RepositoryError
from backend.usuarios.application.ports.output import (
    CredencialesUsuario,
    UsuarioRepositoryPort,
)
from backend.usuarios.domain import Email, EmailAlreadyRegisteredError, Usuario


logger = logging.getLogger(__name__)

# Debe coincidir con el nombre de la restricción en el CREATE TABLE.
_EMAIL_UNIQUE_CONSTRAINT = "usuarios_correo_un"

_ENVIRONMENT_NAMES = {
    "host": "DB_HOST",
    "port": "DB_PORT",
    "dbname": "DB_NAME",
    "user": "DB_USER",
    "password": "DB_PASSWORD",
}


def connection_factory_from_environment() -> Callable[[], PostgresqlConnection]:
    """Read and validate the DB configuration once, at startup.

    Raises RuntimeError right away if any variable is missing, so the app
    fails when it starts and not on the first request.
    """
    missing = [
        variable
        for variable in _ENVIRONMENT_NAMES.values()
        if not os.environ.get(variable)
    ]
    if missing:
        raise RuntimeError(
            "Faltan variables de configuración de base de datos: {}.".format(
                ", ".join(missing)
            )
        )

    connection_parameters: Dict[str, str] = {
        parameter: os.environ[variable]
        for parameter, variable in _ENVIRONMENT_NAMES.items()
    }

    def factory() -> PostgresqlConnection:
        return psycopg2.connect(**connection_parameters)

    return factory


class PostgresqlRepositoryAdapter(UsuarioRepositoryPort):
    def __init__(
        self,
        connection_factory: Callable[[], PostgresqlConnection],
    ) -> None:
        self._connection_factory = connection_factory

    def existe_por_correo(self, correo: Email) -> bool:
        row = self._execute(
            "SELECT EXISTS (SELECT 1 FROM usuarios WHERE correo = %s)",
            (correo.value,),
            fetch_one=True,
        )
        return bool(row[0])

    def guardar(self, usuario: Usuario, password_hash: str) -> int:
        row = self._execute(
            """
            INSERT INTO usuarios (nombre, apellido, nickname, correo, password_hash)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                usuario.nombre,
                usuario.apellido,
                usuario.nickname,
                usuario.correo.value,
                password_hash,
            ),
            fetch_one=True,
            email_unique_violation=True,
        )
        if row is None:
            raise RepositoryError("La base de datos no devolvió el id del usuario.")
        return int(row[0])

    def obtener_credenciales(
        self, correo: Email
    ) -> Optional[CredencialesUsuario]:
        row = self._execute(
            "SELECT id, password_hash FROM usuarios WHERE correo = %s",
            (correo.value,),
            fetch_one=True,
        )
        if row is None:
            return None
        return CredencialesUsuario(usuario_id=int(row[0]), password_hash=row[1])

    def _execute(
        self,
        query: str,
        parameters: Tuple[Any, ...],
        *,
        fetch_one: bool = False,
        email_unique_violation: bool = False,
    ) -> Any:
        connection = None
        try:
            connection = self._connection_factory()
            with connection.cursor() as cursor:
                cursor.execute(query, parameters)
                result = cursor.fetchone() if fetch_one else None
            connection.commit()
            return result
        except psycopg2.errors.UniqueViolation as error:
            if connection is not None:
                connection.rollback()
            if (
                email_unique_violation
                and error.diag.constraint_name == _EMAIL_UNIQUE_CONSTRAINT
            ):
                raise EmailAlreadyRegisteredError() from None
            self._log_database_error(error)
            raise RepositoryError("La operación de persistencia falló.") from None
        except psycopg2.Error as error:
            if connection is not None:
                connection.rollback()
            self._log_database_error(error)
            raise RepositoryError("La operación de persistencia falló.") from None
        finally:
            if connection is not None:
                connection.close()

    @staticmethod
    def _log_database_error(error: psycopg2.Error) -> None:
        # Never log str(error): it can include the duplicated email.
        # pgcode is the SQLSTATE and carries no user data.
        logger.error(
            "PostgreSQL repository operation failed (%s, pgcode=%s).",
            type(error).__name__,
            error.pgcode,
        )
