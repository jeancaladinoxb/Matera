from abc import ABC, abstractmethod
from typing import Optional

from backend.materas.domain import Mac, Matera


class MateraRepositoryPort(ABC):
    @abstractmethod
    def buscar_por_mac(self, mac: Mac) -> Optional[Matera]:
        """Return the matera with this MAC, or None.

        Raises:
            RepositoryError: if the persistence layer fails.
        """

    @abstractmethod
    def registrar(self, matera: Matera) -> bool:
        """Insert the matera if its MAC is new. Never overwrites an existing one.

        Returns True if it was inserted, False if the MAC already existed.

        Raises:
            RepositoryError: if the persistence layer fails.
        """

    @abstractmethod
    def reclamar(self, mac: Mac, usuario_id: int) -> bool:
        """Atomically link an unclaimed matera to the user.

        Returns True if this call claimed it, False if it was not claimable
        (already linked, possibly by a concurrent request, or unknown).

        Raises:
            RepositoryError: if the persistence layer fails.
        """
