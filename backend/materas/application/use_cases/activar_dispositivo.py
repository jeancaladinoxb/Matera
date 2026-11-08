from backend.materas.application.ports.input import ActivarDispositivoPort
from backend.materas.application.ports.output import (
    ClaimCodeVerifierPort,
    DeviceTokenProviderPort,
    MateraRepositoryPort,
)
from backend.materas.domain import Mac, MateraNoVinculadaError, MateraOCodigoInvalidoError


class ActivarDispositivoUseCase(ActivarDispositivoPort):
    def __init__(
        self,
        matera_repository: MateraRepositoryPort,
        claim_code_verifier: ClaimCodeVerifierPort,
        device_token_provider: DeviceTokenProviderPort,
    ) -> None:
        self._matera_repository = matera_repository
        self._claim_code_verifier = claim_code_verifier
        self._device_token_provider = device_token_provider

    def activar(self, mac: str, codigo: str) -> str:
        mac_normalizada = Mac(mac)

        if not self._claim_code_verifier.verificar(mac_normalizada, codigo):
            raise MateraOCodigoInvalidoError()

        matera = self._matera_repository.buscar_por_mac(mac_normalizada)
        if matera is None:
            raise MateraOCodigoInvalidoError()
        if not matera.esta_vinculada:
            raise MateraNoVinculadaError()

        return self._device_token_provider.generar_token(mac_normalizada)
