import logging
from typing import Optional

from backend.gamificacion.application.errors import (
    ErrorAccesoDatosGamificacionError,
)
from backend.gamificacion.application.ports.input import ConsultarLogrosPort
from backend.gamificacion.application.ports.output import (
    EstadisticasRepositoryPort,
    RelojPort,
)
from backend.gamificacion.application.resultado_consulta_logros import (
    ConsultaLogrosExitosa,
    ConsultaLogrosFallida,
    ErrorConsultaLogros,
    ResultadoConsultarLogros,
)
from backend.gamificacion.domain import EvaluadorDeLogros


logger = logging.getLogger(__name__)


class ConsultarLogrosCasoDeUso(ConsultarLogrosPort):
    def __init__(
        self,
        estadisticas_repository: EstadisticasRepositoryPort,
        reloj: RelojPort,
        evaluador: Optional[EvaluadorDeLogros] = None,
    ) -> None:
        self._estadisticas_repository = estadisticas_repository
        self._reloj = reloj
        self._evaluador = evaluador or EvaluadorDeLogros()

    def consultar(self, usuario_id: int) -> ResultadoConsultarLogros:
        try:
            estadisticas = self._estadisticas_repository.obtener_por_usuario(
                usuario_id
            )
            if estadisticas is None or estadisticas.usuario_id != usuario_id:
                return ConsultaLogrosFallida(
                    ErrorConsultaLogros.USUARIO_NO_ENCONTRADO
                )

            perfil = self._evaluador.evaluar(estadisticas, self._reloj.ahora())
            return ConsultaLogrosExitosa(perfil)
        except ErrorAccesoDatosGamificacionError:
            return ConsultaLogrosFallida(ErrorConsultaLogros.ERROR_ACCESO_DATOS)
        except Exception as error:
            logger.error(
                "Gamification query failed unexpectedly (%s).",
                type(error).__name__,
            )
            return ConsultaLogrosFallida(ErrorConsultaLogros.ERROR_DESCONOCIDO)
