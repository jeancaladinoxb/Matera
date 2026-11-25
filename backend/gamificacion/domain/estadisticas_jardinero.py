from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from .errors import EstadisticasInvalidasError


def _es_fecha_con_zona(valor: object) -> bool:
    return isinstance(valor, datetime) and valor.tzinfo is not None


@dataclass(frozen=True)
class EstadisticasJardinero:
    """Hechos del usuario a partir de los cuales se evalúan los logros."""

    usuario_id: int
    fecha_registro: datetime
    fechas_vinculacion: Tuple[datetime, ...]

    def __post_init__(self) -> None:
        if (
            isinstance(self.usuario_id, bool)
            or not isinstance(self.usuario_id, int)
            or self.usuario_id <= 0
        ):
            raise EstadisticasInvalidasError()
        if not _es_fecha_con_zona(self.fecha_registro):
            raise EstadisticasInvalidasError()
        if not isinstance(self.fechas_vinculacion, (tuple, list)):
            raise EstadisticasInvalidasError()
        fechas = tuple(self.fechas_vinculacion)
        if any(not _es_fecha_con_zona(fecha) for fecha in fechas):
            raise EstadisticasInvalidasError()

        object.__setattr__(self, "fechas_vinculacion", tuple(sorted(fechas)))

    @property
    def materas_vinculadas(self) -> int:
        return len(self.fechas_vinculacion)

    @property
    def primera_vinculacion(self) -> Optional[datetime]:
        return self.fechas_vinculacion[0] if self.fechas_vinculacion else None

    def fecha_vinculacion_numero(self, numero: int) -> Optional[datetime]:
        """Fecha en la que se vinculó la matera número `numero` (1, 2, 3...)."""
        if numero <= 0 or numero > len(self.fechas_vinculacion):
            return None
        return self.fechas_vinculacion[numero - 1]
