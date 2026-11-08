import logging
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)

from backend.usuarios.application.ports.output import PasswordHasherPort
from backend.usuarios.domain import Password


logger = logging.getLogger(__name__)


class Argon2Hasher(PasswordHasherPort):
    def __init__(self, password_hasher: Optional[PasswordHasher] = None) -> None:
        self._password_hasher = password_hasher or PasswordHasher()

    def hashear(self, contrasena: Password) -> str:
        return self._password_hasher.hash(contrasena.value)

    def verificar(self, contrasena: str, password_hash: str) -> bool:
        try:
            return self._password_hasher.verify(password_hash, contrasena)
        except VerifyMismatchError:
            # Wrong password: the normal, expected failure.
            return False
        except (InvalidHashError, VerificationError) as error:
            # A stored hash that cannot be processed is a data problem, not a
            # wrong password. Log only the type: never the hash or the password.
            logger.error(
                "Password verification failed unexpectedly (%s).",
                type(error).__name__,
            )
            return False
