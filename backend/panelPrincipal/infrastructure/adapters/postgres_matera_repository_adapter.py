from typing import Callable, Tuple

from psycopg2.extensions import connection as PostgresqlConnection

from backend.panelPrincipal.application.ports.output import MateraRepositoryPort
from backend.panelPrincipal.domain import MateraPanel

from .postgres_read_only_repository import PostgresReadOnlyRepository


class PostgresMateraRepositoryAdapter(
    PostgresReadOnlyRepository, MateraRepositoryPort
):
    def __init__(
        self,
        connection_factory: Callable[[], PostgresqlConnection],
    ) -> None:
        super().__init__(connection_factory)

    def listar_vinculadas_por_usuario(
        self, usuario_id: int
    ) -> Tuple[MateraPanel, ...]:
        rows = self._execute(
            "SELECT id, mac FROM materas "
            "WHERE usuario_id = %s AND estado = %s ORDER BY id",
            (usuario_id, "vinculada"),
        )
        return tuple(
            MateraPanel(matera_id=int(row[0]), mac=str(row[1]))
            for row in rows
        )
