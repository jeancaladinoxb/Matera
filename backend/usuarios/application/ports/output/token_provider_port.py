from abc import ABC, abstractmethod


class TokenProviderPort(ABC):
    @abstractmethod
    def generar_token(self, usuario_id: int) -> str:
        """Generate a session token for the user with the given id.

        The expiration is defined by the adapter's configuration.
        """
