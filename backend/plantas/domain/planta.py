import re
from dataclasses import dataclass
from enum import Enum
from typing import Union

from .errors import PlantaIdInvalidoError, PlantaInvalidaError
from .identificadores import es_entero_positivo

_SLUG_PATTERN = re.compile(r"[a-z0-9_]+")


class NivelLuz(str, Enum):
    BAJA = "baja"
    INDIRECTA = "indirecta"
    DIRECTA = "directa"


class NivelRiego(str, Enum):
    BAJO = "bajo"
    MODERADO = "moderado"
    ALTO = "alto"


Numero = Union[int, float]


def _es_numero(valor: object) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def _validar_rango(nombre: str, minimo: object, maximo: object) -> None:
    if not _es_numero(minimo) or not _es_numero(maximo):
        raise PlantaInvalidaError("El rango de {} debe ser numérico.".format(nombre))
    if minimo >= maximo:
        raise PlantaInvalidaError(
            "El mínimo del rango de {} debe ser menor que el máximo.".format(nombre)
        )


@dataclass(frozen=True)
class Planta:
    """Especie del catálogo con sus rangos ideales (provisionales)."""

    id: int
    slug: str
    nombre_comun: str
    nombre_cientifico: str
    luz: NivelLuz
    riego: NivelRiego
    humedad_suelo_min: Numero
    humedad_suelo_max: Numero
    temperatura_min: Numero
    temperatura_max: Numero
    luz_lux_min: Numero
    luz_lux_max: Numero

    def __post_init__(self) -> None:
        if not es_entero_positivo(self.id):
            raise PlantaIdInvalidoError()
        if not isinstance(self.slug, str) or _SLUG_PATTERN.fullmatch(self.slug) is None:
            raise PlantaInvalidaError(
                "El slug solo admite minúsculas, números y guion bajo."
            )
        for campo in (self.nombre_comun, self.nombre_cientifico):
            if not isinstance(campo, str) or not campo.strip():
                raise PlantaInvalidaError("Los nombres de la planta son obligatorios.")

        # Acepta el texto de la base de datos y lo normaliza a su enumeración
        try:
            object.__setattr__(self, "luz", NivelLuz(self.luz))
            object.__setattr__(self, "riego", NivelRiego(self.riego))
        except ValueError:
            raise PlantaInvalidaError("La luz o el riego no son válidos.") from None

        _validar_rango("humedad del suelo", self.humedad_suelo_min, self.humedad_suelo_max)
        if self.humedad_suelo_min < 0 or self.humedad_suelo_max > 100:
            raise PlantaInvalidaError("La humedad del suelo debe estar entre 0 y 100.")
        _validar_rango("temperatura", self.temperatura_min, self.temperatura_max)
        _validar_rango("luz", self.luz_lux_min, self.luz_lux_max)
        if self.luz_lux_min < 0:
            raise PlantaInvalidaError("La luz no puede ser negativa.")
