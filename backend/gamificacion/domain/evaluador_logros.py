"""Reglas de negocio de la gamificación.

Cada regla recibe las estadísticas del jardinero y la fecha actual y devuelve
el progreso y, si se cumplió, la fecha en la que se desbloqueó. Las fechas se
derivan de los datos (por ejemplo, la fecha en que se vinculó la tercera
matera), así que el resultado es el mismo sin importar cuándo se consulte.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Optional, Tuple

from .errors import GamificacionDomainError
from .estadisticas_jardinero import EstadisticasJardinero
from .logro import Logro
from .perfil_gamificacion import PerfilGamificacion


DIAS_CUIDANDO = 30
HORAS_VINCULACION_EXPRES = 24

ResultadoRegla = Tuple[int, Optional[datetime]]
Regla = Callable[[EstadisticasJardinero, datetime], ResultadoRegla]


@dataclass(frozen=True)
class DefinicionLogro:
    codigo: str
    nombre: str
    descripcion: str
    icono: str
    puntos: int
    meta: int
    regla: Regla


def _por_cantidad_de_materas(cantidad: int) -> Regla:
    def regla(estadisticas: EstadisticasJardinero, _ahora: datetime) -> ResultadoRegla:
        return (
            estadisticas.materas_vinculadas,
            estadisticas.fecha_vinculacion_numero(cantidad),
        )

    return regla


def _dias_cuidando(estadisticas: EstadisticasJardinero, ahora: datetime) -> ResultadoRegla:
    primera = estadisticas.primera_vinculacion
    if primera is None:
        return 0, None
    dias = max(0, (ahora - primera).days)
    cumplido = primera + timedelta(days=DIAS_CUIDANDO)
    return dias, cumplido if cumplido <= ahora else None


def _vinculacion_expres(estadisticas: EstadisticasJardinero, _ahora: datetime) -> ResultadoRegla:
    primera = estadisticas.primera_vinculacion
    if primera is None:
        return 0, None
    limite = estadisticas.fecha_registro + timedelta(hours=HORAS_VINCULACION_EXPRES)
    if primera <= limite:
        return 1, primera
    return 0, None


CATALOGO_LOGROS: Tuple[DefinicionLogro, ...] = (
    DefinicionLogro(
        "primer_brote", "Primer brote", "Vincula tu primera matera.",
        "🌱", 10, 1, _por_cantidad_de_materas(1),
    ),
    DefinicionLogro(
        "vinculacion_expres", "Vinculación exprés",
        "Vincula tu primera matera en las primeras 24 horas desde tu registro.",
        "⚡", 15, 1, _vinculacion_expres,
    ),
    DefinicionLogro(
        "jardin_en_casa", "Jardín en casa", "Ten 3 materas vinculadas.",
        "🪴", 25, 3, _por_cantidad_de_materas(3),
    ),
    DefinicionLogro(
        "un_mes_cuidando", "Un mes cuidando",
        "Cumple 30 días desde que vinculaste tu primera matera.",
        "📅", 20, DIAS_CUIDANDO, _dias_cuidando,
    ),
    DefinicionLogro(
        "botanico_urbano", "Botánico urbano", "Ten 5 materas vinculadas.",
        "🌳", 50, 5, _por_cantidad_de_materas(5),
    ),
)


class EvaluadorDeLogros:
    def __init__(
        self, catalogo: Tuple[DefinicionLogro, ...] = CATALOGO_LOGROS
    ) -> None:
        self._catalogo = catalogo

    def evaluar(
        self, estadisticas: EstadisticasJardinero, ahora: datetime
    ) -> PerfilGamificacion:
        if not isinstance(estadisticas, EstadisticasJardinero):
            raise GamificacionDomainError("Las estadísticas no son válidas.")
        if not isinstance(ahora, datetime) or ahora.tzinfo is None:
            raise GamificacionDomainError("La fecha actual debe tener zona horaria.")

        logros = []
        for definicion in self._catalogo:
            progreso, fecha = definicion.regla(estadisticas, ahora)
            logros.append(
                Logro(
                    codigo=definicion.codigo,
                    nombre=definicion.nombre,
                    descripcion=definicion.descripcion,
                    icono=definicion.icono,
                    puntos=definicion.puntos,
                    progreso=progreso,
                    meta=definicion.meta,
                    fecha_desbloqueo=fecha,
                )
            )
        return PerfilGamificacion(estadisticas.usuario_id, tuple(logros))
