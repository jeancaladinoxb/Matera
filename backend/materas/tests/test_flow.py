import unittest

import jwt
from flask import Flask

from backend.materas.application.use_cases import (
    ActivarDispositivoUseCase,
    VincularMateraUseCase,
)
from backend.materas.domain import Mac, Matera
from backend.materas.infrastructure.adapters import HmacClaimVerifier, JwtDeviceTokenAdapter
from backend.materas.infrastructure.controllers import MateraController
from backend.materas.tests.test_use_cases import InMemoryMateraRepository
from backend.usuarios.infrastructure.adapters import JwtTokenAdapter

USER_SECRET = "user-secret-that-is-long-enough-for-hs256-x"
DEVICE_SECRET = "device-secret-that-is-long-enough-for-hs256"


class VinculacionFlowTests(unittest.TestCase):
    """Whole flow with real adapters; only PostgreSQL is replaced."""

    def setUp(self) -> None:
        repository = InMemoryMateraRepository()
        verifier = HmacClaimVerifier("test-master-key-that-is-long-enough-1234")
        self.user_tokens = JwtTokenAdapter(USER_SECRET, 5)
        repository.registrar(Matera(Mac("246F28AB1234")))
        app = Flask(__name__)
        MateraController(
            VincularMateraUseCase(repository, verifier, self.user_tokens),
            ActivarDispositivoUseCase(repository, verifier, JwtDeviceTokenAdapter(DEVICE_SECRET)),
        ).register_routes(app)
        self.client = app.test_client()
        self.repository = repository
        self.body = {"mac": "246f28ab1234", "codigo": verifier.generar(Mac("246F28AB1234"))}

    def test_factory_to_device_token(self) -> None:
        auth = {"Authorization": "Bearer " + self.user_tokens.generar_token(7)}

        early = self.client.post("/dispositivos/activar", json=self.body)
        self.assertEqual(early.status_code, 409)

        self.assertEqual(self.client.post("/materas/vincular", json=self.body, headers=auth).status_code, 200)
        self.assertEqual(self.repository.materas["246F28AB1234"].usuario_id, 7)

        other = {"Authorization": "Bearer " + self.user_tokens.generar_token(8)}
        self.assertEqual(self.client.post("/materas/vincular", json=self.body, headers=other).status_code, 409)

        activated = self.client.post("/dispositivos/activar", json=self.body)
        self.assertEqual(activated.status_code, 200)
        claims = jwt.decode(activated.get_json()["token"], DEVICE_SECRET, algorithms=["HS256"])
        self.assertEqual((claims["sub"], claims["role"]), ("246F28AB1234", "device"))

    def test_device_token_cannot_link_and_wrong_code_is_404(self) -> None:
        device_token = JwtDeviceTokenAdapter(DEVICE_SECRET).generar_token(Mac("246F28AB1234"))
        response = self.client.post(
            "/materas/vincular", json=self.body, headers={"Authorization": "Bearer " + device_token}
        )
        self.assertEqual(response.status_code, 401)

        auth = {"Authorization": "Bearer " + self.user_tokens.generar_token(7)}
        bad = {"mac": "246F28AB1234", "codigo": "000000000000"}
        unknown = {"mac": "AAAAAAAAAAAA", "codigo": "000000000000"}
        for body in (bad, unknown):
            r = self.client.post("/materas/vincular", json=body, headers=auth)
            self.assertEqual((r.status_code, r.get_json()), (404, {"error": "Matera o código inválido"}))


if __name__ == "__main__":
    unittest.main()
