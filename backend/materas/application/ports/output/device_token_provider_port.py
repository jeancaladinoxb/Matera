from abc import ABC, abstractmethod

from backend.materas.domain import Mac


class DeviceTokenProviderPort(ABC):
    @abstractmethod
    def generar_token(self, mac: Mac) -> str:
        """Generate a device token for the matera with this MAC.

        The expiration is defined by the adapter's configuration.
        """
