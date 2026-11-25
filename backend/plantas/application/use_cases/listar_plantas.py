from typing import Tuple

from backend.plantas.application.ports.input import ListarPlantasPort
from backend.plantas.application.ports.output import PlantaCatalogoPort
from backend.plantas.domain import Planta
from backend.usuarios.application.ports.output import TokenProviderPort


class ListarPlantasUseCase(ListarPlantasPort):
    def __init__(
        self,
        planta_catalogo: PlantaCatalogoPort,
        token_provider: TokenProviderPort,
    ) -> None:
        self._planta_catalogo = planta_catalogo
        self._token_provider = token_provider

    def listar(self, token: str) -> Tuple[Planta, ...]:
        self._token_provider.verificar_token(token)
        return self._planta_catalogo.listar()
