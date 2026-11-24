from dataclasses import dataclass
from typing import Tuple

from .errors import PanelPrincipalDomainError
from .matera_panel import MateraPanel
from .usuario_panel import UsuarioPanel


@dataclass(frozen=True)
class PanelPrincipal:
    usuario: UsuarioPanel
    materas: Tuple[MateraPanel, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.usuario, UsuarioPanel):
            raise PanelPrincipalDomainError("El usuario del panel no es válido.")
        if not isinstance(self.materas, (tuple, list)):
            raise PanelPrincipalDomainError("Las materas del panel no son válidas.")

        materas = tuple(self.materas)
        if any(not isinstance(matera, MateraPanel) for matera in materas):
            raise PanelPrincipalDomainError("Las materas del panel no son válidas.")
        if len({matera.matera_id for matera in materas}) != len(materas):
            raise PanelPrincipalDomainError(
                "El panel no puede contener materas duplicadas."
            )

        object.__setattr__(self, "materas", materas)
