from abc import ABC, abstractmethod


class TokenProviderPort(ABC):
    @abstractmethod
    def generar_token(self, usuario_id: int) -> str:
        """Generate a session token for the user with the given id.

        The expiration is defined by the adapter's configuration.
        """

    @abstractmethod
    def verificar_token(self, token: str) -> int:
        """Return the user id carried by a valid session token.

        Raises:
            InvalidTokenError: if the token is malformed, expired, has a bad
                signature or is not a user token.
        """
