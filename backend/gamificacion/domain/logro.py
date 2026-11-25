from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .errors import LogroInvalidoError


@dataclass(frozen=True)
class Logro:
    """Estado de un logro para un usuario concreto."""

    codigo: str
    nombre: str
    descripcion: str
    icono: str
    puntos: int
    progreso: int
    meta: int
    fecha_desbloqueo: Optional[datetime] = None

    def __post_init__(self) -> None:
        if any(
            not isinstance(valor, str) or not valor.strip()
            for valor in (self.codigo, self.nombre, self.descripcion, self.icono)
        ):
            raise LogroInvalidoError()
        for valor in (self.puntos, self.progreso, self.meta):
            if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
                raise LogroInvalidoError()
        if self.meta == 0:
            raise LogroInvalidoError()

        # El progreso nunca supera la meta (3/1 materas se muestra como 1/1).
        object.__setattr__(self, "progreso", min(self.progreso, self.meta))

    @property
    def desbloqueado(self) -> bool:
        return self.fecha_desbloqueo is not None
