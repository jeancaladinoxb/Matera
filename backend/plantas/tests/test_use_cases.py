import unittest
from typing import Dict, Optional, Tuple

from backend.plantas.application.ports.output import (
    AsignacionPlantaPort,
    PlantaCatalogoPort,
)
from backend.plantas.application.use_cases import (
    ListarPlantasUseCase,
    VincularPlantaAMateraUseCase,
)
from backend.plantas.domain import (
    MateraIdInvalidoError,
    MateraNoEncontradaError,
    Planta,
    PlantaIdInvalidoError,
    PlantaNoEncontradaError,
)
from backend.usuarios.application.ports.output import TokenProviderPort
from backend.usuarios.domain import InvalidTokenError

USUARIO = 7
OTRO_USUARIO = 8
MATERA = 12


def crear_planta(planta_id: int, slug: str) -> Planta:
    return Planta(
        id=planta_id,
        slug=slug,
        nombre_comun=slug.capitalize(),
        nombre_cientifico="Especie " + slug,
        luz="indirecta",
        riego="moderado",
        humedad_suelo_min=40,
        humedad_suelo_max=60,
        temperatura_min=18,
        temperatura_max=30,
        luz_lux_min=8000,
        luz_lux_max=20000,
    )


class InMemoryCatalogo(PlantaCatalogoPort):
    def __init__(self) -> None:
        self.plantas = {1: crear_planta(1, "monstera"), 2: crear_planta(2, "pothos")}
        self.listados = 0
        self.busquedas = 0

    def listar(self) -> Tuple[Planta, ...]:
        self.listados += 1
        return tuple(self.plantas.values())

    def buscar_por_id(self, planta_id: int) -> Optional[Planta]:
        self.busquedas += 1
        return self.plantas.get(planta_id)


class InMemoryAsignacion(AsignacionPlantaPort):
    """Imita la sentencia atómica: solo asigna a una matera vinculada del usuario."""

    def __init__(self) -> None:
        self.materas: Dict[int, dict] = {
            MATERA: {"usuario_id": USUARIO, "estado": "vinculada", "planta_id": None},
            20: {"usuario_id": OTRO_USUARIO, "estado": "vinculada", "planta_id": None},
            30: {"usuario_id": None, "estado": "sin_reclamar", "planta_id": None},
        }
        self.llamadas = 0

    def asignar(self, usuario_id: int, matera_id: int, planta_id: int) -> bool:
        self.llamadas += 1
        matera = self.materas.get(matera_id)
        if (
            matera is None
            or matera["usuario_id"] != usuario_id
            or matera["estado"] != "vinculada"
        ):
            return False
        matera["planta_id"] = planta_id
        return True


class FakeUserTokens(TokenProviderPort):
    def generar_token(self, usuario_id: int) -> str:
        return "user-token-{}".format(usuario_id)

    def verificar_token(self, token: str) -> int:
        if not token.startswith("user-token-"):
            raise InvalidTokenError()
        return int(token.rsplit("-", 1)[1])


TOKEN = "user-token-{}".format(USUARIO)


class ListarPlantasUseCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalogo = InMemoryCatalogo()
        self.use_case = ListarPlantasUseCase(self.catalogo, FakeUserTokens())

    def test_lista_el_catalogo(self) -> None:
        plantas = self.use_case.listar(TOKEN)

        self.assertEqual([p.slug for p in plantas], ["monstera", "pothos"])

    def test_token_invalido_no_consulta_el_catalogo(self) -> None:
        with self.assertRaises(InvalidTokenError):
            self.use_case.listar("token-malo")

        self.assertEqual(self.catalogo.listados, 0)


class VincularPlantaAMateraUseCaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalogo = InMemoryCatalogo()
        self.asignacion = InMemoryAsignacion()
        self.use_case = VincularPlantaAMateraUseCase(
            self.catalogo, self.asignacion, FakeUserTokens()
        )

    def planta_de(self, matera_id: int) -> Optional[int]:
        return self.asignacion.materas[matera_id]["planta_id"]

    def test_vincula_una_planta(self) -> None:
        self.use_case.vincular(TOKEN, MATERA, 1)

        self.assertEqual(self.planta_de(MATERA), 1)

    def test_elegir_otra_planta_reemplaza_la_anterior(self) -> None:
        self.use_case.vincular(TOKEN, MATERA, 1)
        self.use_case.vincular(TOKEN, MATERA, 2)

        self.assertEqual(self.planta_de(MATERA), 2)

    def test_repetir_la_misma_planta_es_valido(self) -> None:
        self.use_case.vincular(TOKEN, MATERA, 1)
        self.use_case.vincular(TOKEN, MATERA, 1)

        self.assertEqual(self.planta_de(MATERA), 1)

    def test_matera_de_otro_usuario(self) -> None:
        with self.assertRaises(MateraNoEncontradaError):
            self.use_case.vincular(TOKEN, 20, 1)

        self.assertIsNone(self.planta_de(20))

    def test_matera_inexistente(self) -> None:
        with self.assertRaises(MateraNoEncontradaError):
            self.use_case.vincular(TOKEN, 999, 1)

    def test_matera_sin_reclamar(self) -> None:
        with self.assertRaises(MateraNoEncontradaError):
            self.use_case.vincular(TOKEN, 30, 1)

    def test_planta_inexistente_no_intenta_asignar(self) -> None:
        with self.assertRaises(PlantaNoEncontradaError):
            self.use_case.vincular(TOKEN, MATERA, 99)

        self.assertEqual(self.asignacion.llamadas, 0)
        self.assertIsNone(self.planta_de(MATERA))

    def test_la_identidad_sale_del_token(self) -> None:
        otro = "user-token-{}".format(OTRO_USUARIO)

        self.use_case.vincular(otro, 20, 1)
        with self.assertRaises(MateraNoEncontradaError):
            self.use_case.vincular(otro, MATERA, 1)

        self.assertEqual(self.planta_de(20), 1)
        self.assertIsNone(self.planta_de(MATERA))

    def test_token_invalido_no_toca_nada(self) -> None:
        with self.assertRaises(InvalidTokenError):
            self.use_case.vincular("token-malo", MATERA, 1)

        self.assertEqual(self.catalogo.busquedas, 0)
        self.assertEqual(self.asignacion.llamadas, 0)

    def test_ids_invalidos(self) -> None:
        for invalido in (0, -1, True, "1", 1.5, None):
            with self.subTest(matera_id=invalido):
                with self.assertRaises(MateraIdInvalidoError):
                    self.use_case.vincular(TOKEN, invalido, 1)  # type: ignore[arg-type]
            with self.subTest(planta_id=invalido):
                with self.assertRaises(PlantaIdInvalidoError):
                    self.use_case.vincular(TOKEN, MATERA, invalido)  # type: ignore[arg-type]

        self.assertEqual(self.asignacion.llamadas, 0)


if __name__ == "__main__":
    unittest.main()
