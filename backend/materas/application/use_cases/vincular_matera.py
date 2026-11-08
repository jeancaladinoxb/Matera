from backend.materas.application.ports.input import VincularMateraPort
from backend.materas.application.ports.output import (
    ClaimCodeVerifierPort,
    MateraRepositoryPort,
)
from backend.materas.domain import Mac, MateraOCodigoInvalidoError, MateraYaVinculadaError
from backend.usuarios.application.ports.output import TokenProviderPort


class VincularMateraUseCase(VincularMateraPort):
    def __init__(
        self,
        matera_repository: MateraRepositoryPort,
        claim_code_verifier: ClaimCodeVerifierPort,
        token_provider: TokenProviderPort,
    ) -> None:
        self._matera_repository = matera_repository
        self._claim_code_verifier = claim_code_verifier
        self._token_provider = token_provider

    def vincular(self, token: str, mac: str, codigo: str) -> None:
        usuario_id = self._token_provider.verificar_token(token)
        mac_normalizada = Mac(mac)

        # The code is checked before touching the database.
        if not self._claim_code_verifier.verificar(mac_normalizada, codigo):
            raise MateraOCodigoInvalidoError()

        matera = self._matera_repository.buscar_por_mac(mac_normalizada)
        if matera is None:
            raise MateraOCodigoInvalidoError()

        matera.reclamar(usuario_id)  # raises MateraYaVinculadaError

        if not self._matera_repository.reclamar(mac_normalizada, usuario_id):
            # Lost a race: someone else claimed it after our lookup.
            raise MateraYaVinculadaError()
