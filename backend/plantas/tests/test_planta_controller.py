import unittest
from typing import Tuple

from flask import Flask

from backend.plantas.application.ports.input import (
    ListarPlantasPort,
    VincularPlantaAMateraPort,
)
from backend.plantas.domain import (
    MateraIdInvalidoError,
    MateraNoEncontradaError,
    Planta,
    PlantaIdInvalidoError,
    PlantaNoEncontradaError,
)
from backend.plantas.infrastructure.controllers import PlantaController
from backend.usuarios.application.ports.errors import RepositoryError
from backend.usuarios.domain import InvalidTokenError

COOKIE = "cuida_mate_session"


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


class FakeListar(ListarPlantasPort):
    def __init__(self) -> None:
        self.error = None
        self.tokens = []

    def listar(self, token: str) -> Tuple[Planta, ...]:
        self.tokens.append(token)
        if self.error is not None:
            raise self.error
        return (crear_planta(1, "monstera"), crear_planta(2, "pothos"))


class FakeVincular(VincularPlantaAMateraPort):
    def __init__(self) -> None:
        self.error = None
        self.calls = []

    def vincular(self, token: str, matera_id: int, planta_id: int) -> None:
        self.calls.append((token, matera_id, planta_id))
        if self.error is not None:
            raise self.error


class PlantaControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.listar = FakeListar()
        self.vincular = FakeVincular()
        app = Flask(__name__)
        PlantaController(self.listar, self.vincular).register_routes(app)
        self.client = app.test_client()
        self.client.set_cookie(COOKIE, "user-jwt")

    # GET /plantas

    def test_listar_devuelve_el_catalogo_sin_rangos(self) -> None:
        response = self.client.get("/plantas")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "plantas": [
                    {
                        "id": 1,
                        "slug": "monstera",
                        "nombre_comun": "Monstera",
                        "nombre_cientifico": "Especie monstera",
                        "luz": "indirecta",
                        "riego": "moderado",
                    },
                    {
                        "id": 2,
                        "slug": "pothos",
                        "nombre_comun": "Pothos",
                        "nombre_cientifico": "Especie pothos",
                        "luz": "indirecta",
                        "riego": "moderado",
                    },
                ]
            },
        )
        self.assertEqual(self.listar.tokens, ["user-jwt"])

    def test_listar_sin_cookie_es_401(self) -> None:
        self.client.delete_cookie(COOKIE)

        response = self.client.get("/plantas")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"error": "No autorizado"})
        self.assertEqual(self.listar.tokens, [])

    def test_listar_con_token_invalido_es_401(self) -> None:
        self.listar.error = InvalidTokenError()

        response = self.client.get("/plantas")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"error": "No autorizado"})

    def test_listar_error_inesperado_es_500_generico(self) -> None:
        self.listar.error = RepositoryError("detalle interno secreto")

        response = self.client.get("/plantas")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "Error interno del servidor"})
        self.assertNotIn("secreto", response.get_data(as_text=True))

    # POST /materas/<id>/planta

    def test_vincular_correcto(self) -> None:
        response = self.client.post("/materas/12/planta", json={"planta_id": 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"mensaje": "Planta vinculada", "matera_id": 12, "planta_id": 2},
        )
        self.assertEqual(self.vincular.calls, [("user-jwt", 12, 2)])

    def test_la_identidad_sale_de_la_cookie_no_del_cuerpo(self) -> None:
        response = self.client.post(
            "/materas/12/planta",
            json={"planta_id": 2, "usuario_id": 999, "token": "otro"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.vincular.calls, [("user-jwt", 12, 2)])

    def test_vincular_sin_cookie_es_401(self) -> None:
        self.client.delete_cookie(COOKIE)

        response = self.client.post("/materas/12/planta", json={"planta_id": 2})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"error": "No autorizado"})
        self.assertEqual(self.vincular.calls, [])

    def test_vincular_con_token_invalido_es_401(self) -> None:
        self.vincular.error = InvalidTokenError()

        response = self.client.post("/materas/12/planta", json={"planta_id": 2})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"error": "No autorizado"})

    def test_cuerpo_que_no_es_json_es_400(self) -> None:
        response = self.client.post(
            "/materas/12/planta", data="planta_id=2", content_type="text/plain"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Se requiere un cuerpo JSON válido"})
        self.assertEqual(self.vincular.calls, [])

    def test_json_que_no_es_objeto_es_400(self) -> None:
        for cuerpo in ([2], 2, "2", None):
            with self.subTest(cuerpo=cuerpo):
                response = self.client.post("/materas/12/planta", json=cuerpo)

                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    response.get_json(), {"error": "Se requiere un cuerpo JSON válido"}
                )

    def test_falta_planta_id_es_400(self) -> None:
        response = self.client.post("/materas/12/planta", json={"otro": 1})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Faltan campos obligatorios"})

    def test_planta_id_invalido_es_400(self) -> None:
        for invalido in ("2", 2.5, 2.0, True, False, None, 0, -1, [2], {"id": 2}):
            with self.subTest(planta_id=invalido):
                response = self.client.post(
                    "/materas/12/planta", json={"planta_id": invalido}
                )

                self.assertEqual(response.status_code, 400)
                self.assertEqual(
                    response.get_json(), {"error": "planta_id debe ser un entero positivo"}
                )
        self.assertEqual(self.vincular.calls, [])

    def test_ids_invalidos_del_caso_de_uso_son_400(self) -> None:
        self.vincular.error = MateraIdInvalidoError()
        r1 = self.client.post("/materas/0/planta", json={"planta_id": 2})
        self.vincular.error = PlantaIdInvalidoError()
        r2 = self.client.post("/materas/12/planta", json={"planta_id": 2})

        self.assertEqual(r1.status_code, 400)
        self.assertEqual(r1.get_json(), {"error": "El id de la matera no es válido."})
        self.assertEqual(r2.status_code, 400)

    def test_planta_o_matera_inexistente_dan_el_mismo_404(self) -> None:
        self.vincular.error = PlantaNoEncontradaError()
        planta = self.client.post("/materas/12/planta", json={"planta_id": 99})
        self.vincular.error = MateraNoEncontradaError()
        matera = self.client.post("/materas/12/planta", json={"planta_id": 2})

        self.assertEqual(planta.status_code, 404)
        self.assertEqual(matera.status_code, 404)
        self.assertEqual(planta.get_json(), {"error": "Recurso no encontrado"})
        self.assertEqual(planta.get_json(), matera.get_json())

    def test_vincular_error_inesperado_es_500_generico(self) -> None:
        self.vincular.error = RepositoryError("detalle interno secreto")

        response = self.client.post("/materas/12/planta", json={"planta_id": 2})

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "Error interno del servidor"})
        self.assertNotIn("secreto", response.get_data(as_text=True))

    def test_metodos_no_permitidos(self) -> None:
        self.assertEqual(self.client.post("/plantas", json={}).status_code, 405)
        self.assertEqual(self.client.get("/materas/12/planta").status_code, 405)
        self.assertEqual(self.client.put("/materas/12/planta", json={"planta_id": 2}).status_code, 405)


if __name__ == "__main__":
    unittest.main()
