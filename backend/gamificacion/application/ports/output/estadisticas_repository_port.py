from abc import ABC, abstractmethod
from typing import Optional

from backend.gamificacion.domain import EstadisticasJardinero


class EstadisticasRepositoryPort(ABC):
    @abstractmethod
    def obtener_por_usuario(
        self, usuario_id: int
    ) -> Optional[EstadisticasJardinero]:
        """Return the user's gardening facts, or None when the user does not exist."""
