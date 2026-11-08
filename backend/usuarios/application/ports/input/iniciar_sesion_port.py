from abc import ABC, abstractmethod


class IniciarSesionPort(ABC):
    @abstractmethod
    def iniciar_sesion(self, correo: str, contrasena: str) -> str:
        """Authenticate a user and return the issued session token."""
        raise NotImplementedError
