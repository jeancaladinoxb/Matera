from dataclasses import dataclass
from enum import Enum
from typing import Union

from backend.gamificacion.domain import PerfilGamificacion


class ErrorConsultaLogros(str, Enum):
    USUARIO_NO_ENCONTRADO = "usuario_no_encontrado"
    ERROR_ACCESO_DATOS = "error_acceso_datos"
    ERROR_DESCONOCIDO = "error_desconocido"


@dataclass(frozen=True)
class ConsultaLogrosExitosa:
    perfil: PerfilGamificacion


@dataclass(frozen=True)
class ConsultaLogrosFallida:
    error: ErrorConsultaLogros


ResultadoConsultarLogros = Union[ConsultaLogrosExitosa, ConsultaLogrosFallida]
