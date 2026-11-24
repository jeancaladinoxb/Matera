from typing import Callable, Optional

from psycopg2.extensions import connection as PostgresqlConnection

from backend.panelPrincipal.application.ports.output import UsuarioRepositoryPort
from backend.panelPrincipal.domain import UsuarioPanel

from .postgres_read_only_repository import PostgresReadOnlyRepository


class PostgresUsuarioRepositoryAdapter(
    PostgresReadOnlyRepository, UsuarioRepositoryPort
):
    def __init__(
        self,
        connection_factory: Callable[[], PostgresqlConnection],
    ) -> None:
        super().__init__(connection_factory)

    def consultar_por_id(self, usuario_id: int) -> Optional[UsuarioPanel]:
        rows = self._execute(
            "SELECT id, nombre, nickname FROM usuarios WHERE id = %s",
            (usuario_id,),
        )
        if not rows:
            return None

        row = rows[0]
        return UsuarioPanel(
            usuario_id=int(row[0]),
            nombre=str(row[1]),
            nickname=str(row[2]),
        )
