from abc import ABC, abstractmethod

from backend.usuarios.domain import Password


class PasswordHasherPort(ABC):
    @abstractmethod
    def hashear(self, contrasena: Password) -> str:
        """Return a one-way hash of the validated password."""
        raise NotImplementedError

    @abstractmethod
    def verificar(self, contrasena: str, password_hash: str) -> bool:
        """Check clear-text login input against a previously generated hash."""
        raise NotImplementedError
