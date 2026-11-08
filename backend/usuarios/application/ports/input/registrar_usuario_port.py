from abc import ABC, abstractmethod


class RegistrarUsuarioPort(ABC):
    @abstractmethod
    def registrar(
        self,
        *,
        nombre: str,
        apellido: str,
        nickname: str,
        correo: str,
        contrasena: str,
    ) -> str:
        """Register a user and return the issued session token."""
        raise NotImplementedError
