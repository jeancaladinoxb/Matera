import logging

from backend.panelPrincipal.application.errors import ErrorAccesoDatosPanelError
from backend.panelPrincipal.application.ports.input import (
    ConsultarPanelPrincipalPort,
)
from backend.panelPrincipal.application.ports.output import (
    MateraRepositoryPort,
    UsuarioRepositoryPort,
)
from backend.panelPrincipal.application.resultado_consulta_panel import (
    ConsultaPanelExitosa,
    ConsultaPanelFallida,
    ErrorConsultaPanel,
    ResultadoConsultarPanelPrincipal,
)
from backend.panelPrincipal.domain import PanelPrincipal


logger = logging.getLogger(__name__)


class ConsultarPanelPrincipalCasoDeUso(ConsultarPanelPrincipalPort):
    def __init__(
        self,
        usuario_repository: UsuarioRepositoryPort,
        matera_repository: MateraRepositoryPort,
    ) -> None:
        self._usuario_repository = usuario_repository
        self._matera_repository = matera_repository

    def consultar(self, usuario_id: int) -> ResultadoConsultarPanelPrincipal:
        try:
            usuario = self._usuario_repository.consultar_por_id(usuario_id)
            if usuario is None or usuario.usuario_id != usuario_id:
                return ConsultaPanelFallida(
                    ErrorConsultaPanel.USUARIO_NO_ENCONTRADO
                )

            materas = self._matera_repository.listar_vinculadas_por_usuario(
                usuario_id
            )
            return ConsultaPanelExitosa(PanelPrincipal(usuario, materas))
        except ErrorAccesoDatosPanelError:
            return ConsultaPanelFallida(ErrorConsultaPanel.ERROR_ACCESO_DATOS)
        except Exception as error:
            logger.error(
                "Panel query failed unexpectedly (%s).",
                type(error).__name__,
            )
            return ConsultaPanelFallida(ErrorConsultaPanel.ERROR_DESCONOCIDO)
