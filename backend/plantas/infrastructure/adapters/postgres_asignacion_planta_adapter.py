from typing import Callable

from psycopg2.extensions import connection as PostgresqlConnection

from backend.plantas.application.ports.output import AsignacionPlantaPort

from ._postgres import ID_MAXIMO, ejecutar


class PostgresAsignacionPlantaAdapter(AsignacionPlantaPort):
    def __init__(
        self,
        connection_factory: Callable[[], PostgresqlConnection],
    ) -> None:
        self._connection_factory = connection_factory

    def asignar(self, usuario_id: int, matera_id: int, planta_id: int) -> bool:
        if matera_id > ID_MAXIMO or planta_id > ID_MAXIMO:
            return False
        # One statement: the WHERE clause checks ownership and state atomically, and
        # the outcome is decided by the affected rows. Assigning the same plant again
        # still matches the row, so repeating is valid.
        _, rowcount = ejecutar(
            self._connection_factory,
            "UPDATE materas SET planta_id = %s "
            "WHERE id = %s AND usuario_id = %s AND estado = 'vinculada'",
            (planta_id, matera_id, usuario_id),
        )
        return rowcount == 1
