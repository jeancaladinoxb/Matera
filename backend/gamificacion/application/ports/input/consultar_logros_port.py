from abc import ABC, abstractmethod

from backend.gamificacion.application.resultado_consulta_logros import (
    ResultadoConsultarLogros,
)


class ConsultarLogrosPort(ABC):
    @abstractmethod
    def consultar(self, usuario_id: int) -> ResultadoConsultarLogros:
        """Return the authenticated user's gamification profile."""
