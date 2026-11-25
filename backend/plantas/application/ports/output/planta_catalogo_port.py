from abc import ABC, abstractmethod
from typing import Optional, Tuple

from backend.plantas.domain import Planta


class PlantaCatalogoPort(ABC):
    @abstractmethod
    def listar(self) -> Tuple[Planta, ...]:
        """Return every plant of the catalog.

        Raises:
            RepositoryError: if the persistence layer fails.
        """

    @abstractmethod
    def buscar_por_id(self, planta_id: int) -> Optional[Planta]:
        """Return the plant with this id, or None.

        Raises:
            RepositoryError: if the persistence layer fails.
        """
