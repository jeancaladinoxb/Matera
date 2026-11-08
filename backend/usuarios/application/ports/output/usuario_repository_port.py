from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from backend.usuarios.domain import Email, Usuario


@dataclass(frozen=True)
class CredencialesUsuario:
    usuario_id: int
    password_hash: str = field(repr=False)


class UsuarioRepositoryPort(ABC):
    @abstractmethod
    def existe_por_correo(self, correo: Email) -> bool:
        """Return whether a user with this email is persisted.

        Raises:
            RepositoryError: if the persistence layer fails.
        """

    @abstractmethod
    def guardar(self, usuario: Usuario, password_hash: str) -> int:
        """Persist the user with its password hash and return the new user id.

        Never persists the clear-text password.

        Raises:
            EmailAlreadyRegisteredError: if the email violates the unique constraint.
            RepositoryError: if the persistence layer fails.
        """

    @abstractmethod
    def obtener_credenciales(self, correo: Email) -> Optional[CredencialesUsuario]:
        """Return the user id and password hash, or None when no user matches.

        Raises:
            RepositoryError: if the persistence layer fails.
        """
