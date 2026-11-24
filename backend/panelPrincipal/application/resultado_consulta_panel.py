from dataclasses import dataclass
from enum import Enum
from typing import Union

from backend.panelPrincipal.domain import PanelPrincipal


class ErrorConsultaPanel(str, Enum):
    USUARIO_NO_ENCONTRADO = "usuario_no_encontrado"
    ERROR_ACCESO_DATOS = "error_acceso_datos"
    ERROR_DESCONOCIDO = "error_desconocido"


@dataclass(frozen=True)
class ConsultaPanelExitosa:
    panel: PanelPrincipal


@dataclass(frozen=True)
class ConsultaPanelFallida:
    error: ErrorConsultaPanel


ResultadoConsultarPanelPrincipal = Union[
    ConsultaPanelExitosa, ConsultaPanelFallida
]
