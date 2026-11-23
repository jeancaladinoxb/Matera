from abc import ABC, abstractmethod
from typing import Optional

from backend.materas.domain import Matera


class ConsultarMateraDelUsuarioPort(ABC):
    @abstractmethod
    def consultar(self, token: str) -> Optional[Matera]:
        """Return the linked matera for the user identified by the session."""
