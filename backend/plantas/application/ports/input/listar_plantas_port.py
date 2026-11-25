from abc import ABC, abstractmethod
from typing import Tuple

from backend.plantas.domain import Planta


class ListarPlantasPort(ABC):
    @abstractmethod
    def listar(self, token: str) -> Tuple[Planta, ...]:
        """Return the plant catalog for the user identified by the session.

        Raises:
            InvalidTokenError: if the session token is not valid.
            RepositoryError: if the persistence layer fails.
        """
