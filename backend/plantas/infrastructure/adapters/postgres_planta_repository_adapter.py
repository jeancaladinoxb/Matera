from typing import Callable, Optional, Tuple

from psycopg2.extensions import connection as PostgresqlConnection

from backend.plantas.application.ports.output import PlantaCatalogoPort
from backend.plantas.domain import Planta

from ._postgres import ID_MAXIMO, ejecutar

_COLUMNAS = (
    "id, slug, nombre_comun, nombre_cientifico, luz, riego, "
    "humedad_suelo_min, humedad_suelo_max, temperatura_min, temperatura_max, "
    "luz_lux_min, luz_lux_max"
)


class PostgresPlantaRepositoryAdapter(PlantaCatalogoPort):
    def __init__(
        self,
        connection_factory: Callable[[], PostgresqlConnection],
    ) -> None:
        self._connection_factory = connection_factory

    def listar(self) -> Tuple[Planta, ...]:
        filas, _ = ejecutar(
            self._connection_factory,
            "SELECT {} FROM plantas ORDER BY id".format(_COLUMNAS),
            (),
            leer_filas=True,
        )
        return tuple(Planta(*fila) for fila in filas)

    def buscar_por_id(self, planta_id: int) -> Optional[Planta]:
        if planta_id > ID_MAXIMO:
            return None
        filas, _ = ejecutar(
            self._connection_factory,
            "SELECT {} FROM plantas WHERE id = %s".format(_COLUMNAS),
            (planta_id,),
            leer_filas=True,
        )
        return Planta(*filas[0]) if filas else None
