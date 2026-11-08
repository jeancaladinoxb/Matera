from abc import ABC, abstractmethod

from backend.materas.domain import Mac


class ClaimCodeVerifierPort(ABC):
    @abstractmethod
    def verificar(self, mac: Mac, codigo: str) -> bool:
        """Return whether the code is the valid claim code for this MAC."""

    @abstractmethod
    def generar(self, mac: Mac) -> str:
        """Return the claim code for this MAC."""
