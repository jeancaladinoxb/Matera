from abc import ABC, abstractmethod
from typing import Optional

from backend.panelPrincipal.domain import UsuarioPanel


class UsuarioRepositoryPort(ABC):
    @abstractmethod
    def consultar_por_id(self, usuario_id: int) -> Optional[UsuarioPanel]:
        """Return the panel profile for a user, or None when it does not exist."""
