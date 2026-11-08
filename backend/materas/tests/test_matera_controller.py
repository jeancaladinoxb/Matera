import unittest

from flask import Flask

from backend.materas.application.ports.input import (
    ActivarDispositivoPort,
    VincularMateraPort,
)
from backend.materas.domain import (
    InvalidMacError,
    MateraNoVinculadaError,
    MateraOCodigoInvalidoError,
    MateraYaVinculadaError,
)
from backend.materas.infrastructure.controllers import MateraController
from backend.usuarios.application.ports.errors import RepositoryError
from backend.usuarios.domain import InvalidTokenError


class FakeVincular(VincularMateraPort):
    def __init__(self) -> None:
        self.error = None
        self.calls = []

    def vincular(self, token: str, mac: str, codigo: str) -> None:
        self.calls.append((token, mac, codigo))
        if self.error is not None:
            raise self.error


class FakeActivar(ActivarDispositivoPort):
    def __init__(self) -> None:
        self.error = None
        self.calls = []

    def activar(self, mac: str, codigo: str) -> str:
        self.calls.append((mac, codigo))
        if self.error is not None:
            raise self.error
        return "device-token"


class MateraControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.vincular = FakeVincular()
        self.activar = FakeActivar()
        app = Flask(__name__)
        MateraController(self.vincular, self.activar).register_routes(app)
        self.client = app.test_client()
        self.body = {"mac": "24:6F:28:AB:12:34", "codigo": "9f3a1c7e0b52"}
        self.auth = {"Authorization": "Bearer user-jwt"}

    def test_vincular_success(self) -> None:
        response = self.client.post("/materas/vincular", json=self.body, headers=self.auth)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"mensaje": "Matera vinculada"})
        self.assertEqual(self.vincular.calls, [("user-jwt", "24:6F:28:AB:12:34", "9f3a1c7e0b52")])

    def test_vincular_ignores_user_id_in_body(self) -> None:
        self.client.post("/materas/vincular", json={**self.body, "usuario_id": 99}, headers=self.auth)
        self.assertEqual(self.vincular.calls[0][0], "user-jwt")
        self.assertEqual(len(self.vincular.calls[0]), 3)

    def test_vincular_without_valid_bearer_header_is_401(self) -> None:
        for headers in ({}, {"Authorization": "Bearer"}, {"Authorization": "Bearer "}, {"Authorization": "Basic abc"}):
            response = self.client.post("/materas/vincular", json=self.body, headers=headers)
            self.assertEqual(response.status_code, 401, headers)
        self.assertEqual(self.vincular.calls, [])

    def test_vincular_error_mapping(self) -> None:
        cases = [
            (InvalidTokenError(), 401, "No autorizado"),
            (InvalidMacError(), 400, "La MAC no tiene un formato válido."),
            (MateraOCodigoInvalidoError(), 404, "Matera o código inválido"),
            (MateraYaVinculadaError(), 409, "La matera ya está vinculada"),
            (RepositoryError("secret db detail"), 500, "Error interno del servidor"),
            (RuntimeError("boom"), 500, "Error interno del servidor"),
        ]
        for error, status, message in cases:
            self.vincular.error = error
            response = self.client.post("/materas/vincular", json=self.body, headers=self.auth)
            self.assertEqual(response.status_code, status, error)
            self.assertEqual(response.get_json(), {"error": message})

    def test_invalid_bodies_are_400(self) -> None:
        for path, headers in (("/materas/vincular", self.auth), ("/dispositivos/activar", {})):
            for kwargs in (
                {"data": "x"},
                {"json": [1]},
                {"json": {"mac": "A"}},
                {"json": {"mac": 1, "codigo": "x"}},
            ):
                response = self.client.post(path, headers=headers, **kwargs)
                self.assertEqual(response.status_code, 400, (path, kwargs))

    def test_activar_success_does_not_cache(self) -> None:
        response = self.client.post("/dispositivos/activar", json=self.body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"token": "device-token"})
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_activar_error_mapping(self) -> None:
        cases = [
            (InvalidMacError(), 400, "La MAC no tiene un formato válido."),
            (MateraOCodigoInvalidoError(), 404, "Matera o código inválido"),
            (MateraNoVinculadaError(), 409, "La matera aún no está vinculada"),
            (RepositoryError("x"), 500, "Error interno del servidor"),
        ]
        for error, status, message in cases:
            self.activar.error = error
            response = self.client.post("/dispositivos/activar", json=self.body)
            self.assertEqual(response.status_code, status, error)
            self.assertEqual(response.get_json(), {"error": message})


if __name__ == "__main__":
    unittest.main()
