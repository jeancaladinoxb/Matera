from abc import ABC, abstractmethod
from typing import Tuple

from backend.panelPrincipal.domain import MateraPanel


class MateraRepositoryPort(ABC):
    @abstractmethod
    def listar_vinculadas_por_usuario(
        self, usuario_id: int
    ) -> Tuple[MateraPanel, ...]:
        """Return all linked materas belonging to the given user."""
