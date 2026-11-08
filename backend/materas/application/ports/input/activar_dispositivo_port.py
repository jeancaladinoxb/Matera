from abc import ABC, abstractmethod


class ActivarDispositivoPort(ABC):
    @abstractmethod
    def activar(self, mac: str, codigo: str) -> str:
        """Return a device token for a linked matera.

        Raises:
            ValidationError: if the MAC format is invalid.
            MateraOCodigoInvalidoError: if the code is wrong or the matera is unknown.
            MateraNoVinculadaError: if the matera is not linked yet.
        """
