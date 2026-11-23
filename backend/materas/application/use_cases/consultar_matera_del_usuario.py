from typing import Optional

from backend.materas.application.ports.input import (
    ConsultarMateraDelUsuarioPort,
)
from backend.materas.application.ports.output import MateraRepositoryPort
from backend.materas.domain import Matera
from backend.usuarios.application.ports.output import TokenProviderPort


class ConsultarMateraDelUsuarioUseCase(
    ConsultarMateraDelUsuarioPort
):
    def __init__(
        self,
        matera_repository: MateraRepositoryPort,
        token_provider: TokenProviderPort,
    ) -> None:
        self._matera_repository = matera_repository
        self._token_provider = token_provider

    def consultar(self, token: str) -> Optional[Matera]:
        usuario_id = self._token_provider.verificar_token(token)
        return self._matera_repository.buscar_por_usuario(usuario_id)
