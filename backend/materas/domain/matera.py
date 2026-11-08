from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from .errors import MateraYaVinculadaError
from .mac import Mac


class EstadoMatera(str, Enum):
    SIN_RECLAMAR = "sin_reclamar"
    VINCULADA = "vinculada"


@dataclass(frozen=True)
class Matera:
    mac: Mac
    usuario_id: Optional[int] = None
    estado: EstadoMatera = EstadoMatera.SIN_RECLAMAR
    fecha_vinculacion: Optional[datetime] = None

    def __post_init__(self) -> None:
        vinculada = self.estado == EstadoMatera.VINCULADA
        if vinculada != (self.usuario_id is not None) or vinculada != (
            self.fecha_vinculacion is not None
        ):
            raise ValueError("Estado de la matera incoherente con su usuario o fecha.")

    @property
    def esta_vinculada(self) -> bool:
        return self.estado == EstadoMatera.VINCULADA

    def reclamar(
        self, usuario_id: int, fecha: Optional[datetime] = None
    ) -> "Matera":
        """Return this matera claimed by the user. A matera belongs to one user."""
        if self.esta_vinculada:
            raise MateraYaVinculadaError()
        return replace(
            self,
            usuario_id=usuario_id,
            estado=EstadoMatera.VINCULADA,
            fecha_vinculacion=fecha or datetime.now(timezone.utc),
        )
