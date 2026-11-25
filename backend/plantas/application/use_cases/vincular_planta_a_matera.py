from backend.plantas.application.ports.input import VincularPlantaAMateraPort
from backend.plantas.application.ports.output import (
    AsignacionPlantaPort,
    PlantaCatalogoPort,
)
from backend.plantas.domain import (
    MateraIdInvalidoError,
    MateraNoEncontradaError,
    PlantaIdInvalidoError,
    PlantaNoEncontradaError,
    es_entero_positivo,
)
from backend.usuarios.application.ports.output import TokenProviderPort


class VincularPlantaAMateraUseCase(VincularPlantaAMateraPort):
    def __init__(
        self,
        planta_catalogo: PlantaCatalogoPort,
        asignacion_planta: AsignacionPlantaPort,
        token_provider: TokenProviderPort,
    ) -> None:
        self._planta_catalogo = planta_catalogo
        self._asignacion_planta = asignacion_planta
        self._token_provider = token_provider

    def vincular(self, token: str, matera_id: int, planta_id: int) -> None:
        # La identidad sale solo de la sesión, nunca de los datos de la petición
        usuario_id = self._token_provider.verificar_token(token)
        if not es_entero_positivo(matera_id):
            raise MateraIdInvalidoError()
        if not es_entero_positivo(planta_id):
            raise PlantaIdInvalidoError()

        if self._planta_catalogo.buscar_por_id(planta_id) is None:
            raise PlantaNoEncontradaError()

        # Una sola sentencia atómica decide si la matera existe y es del usuario
        if not self._asignacion_planta.asignar(usuario_id, matera_id, planta_id):
            raise MateraNoEncontradaError()
