from dataclasses import dataclass
from typing import Optional, Tuple

from .errors import GamificacionDomainError
from .logro import Logro
from .nivel import Nivel, nivel_para, siguiente_nivel


@dataclass(frozen=True)
class PerfilGamificacion:
    usuario_id: int
    logros: Tuple[Logro, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.logros, (tuple, list)):
            raise GamificacionDomainError("Los logros del perfil no son válidos.")
        logros = tuple(self.logros)
        if any(not isinstance(logro, Logro) for logro in logros):
            raise GamificacionDomainError("Los logros del perfil no son válidos.")
        if len({logro.codigo for logro in logros}) != len(logros):
            raise GamificacionDomainError("El perfil no puede repetir logros.")
        object.__setattr__(self, "logros", logros)

    @property
    def puntos(self) -> int:
        return sum(logro.puntos for logro in self.logros if logro.desbloqueado)

    @property
    def nivel(self) -> Nivel:
        return nivel_para(self.puntos)

    @property
    def siguiente_nivel(self) -> Optional[Nivel]:
        return siguiente_nivel(self.nivel)

    @property
    def puntos_para_siguiente_nivel(self) -> int:
        siguiente = self.siguiente_nivel
        if siguiente is None:
            return 0
        return siguiente.puntos_minimos - self.puntos

    @property
    def logros_desbloqueados(self) -> int:
        return sum(1 for logro in self.logros if logro.desbloqueado)
