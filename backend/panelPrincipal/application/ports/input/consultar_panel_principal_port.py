from abc import ABC, abstractmethod

from backend.panelPrincipal.application.resultado_consulta_panel import (
    ResultadoConsultarPanelPrincipal,
)


class ConsultarPanelPrincipalPort(ABC):
    @abstractmethod
    def consultar(self, usuario_id: int) -> ResultadoConsultarPanelPrincipal:
        """Return the authenticated user's panel."""
