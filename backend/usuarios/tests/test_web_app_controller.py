import unittest

from flask import Flask

from backend.usuarios.application.ports.errors import RepositoryError
from backend.usuarios.application.ports.input import (
    IniciarSesionPort,
    RegistrarUsuarioPort,
)
from backend.usuarios.domain import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidEmailError,
)
from backend.usuarios.infrastructure.controllers import WebAppController


class FakeRegistrarUsuario(RegistrarUsuarioPort):
    def __init__(self) -> None:
        self.error = None
        self.calls = []

    def registrar(
        self,
        *,
        nombre: str,
        apellido: str,
        nickname: str,
        correo: str,
        contrasena: str,
    ) -> str:
        self.calls.append(
            {
                "nombre": nombre,
                "apellido": apellido,
                "nickname": nickname,
                "correo": correo,
                "contrasena": contrasena,
            }
        )
        if self.error is not None:
            raise self.error
        return "registration-token"


class FakeIniciarSesion(IniciarSesionPort):
    def __init__(self) -> None:
        self.error = None
        self.calls = []

    def iniciar_sesion(self, correo: str, contrasena: str) -> str:
        self.calls.append((correo, contrasena))
        if self.error is not None:
            raise self.error
        return "login-token"


class WebAppControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registrar = FakeRegistrarUsuario()
        self.iniciar_sesion = FakeIniciarSesion()
        self.app = Flask(__name__)
        self.controller = WebAppController(self.registrar, self.iniciar_sesion)
        self.controller.register_routes(self.app)
        self.client = self.app.test_client()

    def test_registration_returns_token_and_calls_input_port(self) -> None:
        response = self.client.post(
            "/registro",
            json={
                "nombre": "Ana",
                "apellido": "Pérez",
                "nickname": "anap",
                "correo": "ana@example.com",
                "contrasena": "Clave123",
            },
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"token": "registration-token"})
        self.assertEqual(len(self.registrar.calls), 1)

    def test_login_returns_token_and_calls_input_port(self) -> None:
        response = self.client.post(
            "/login",
            json={"correo": "ana@example.com", "contrasena": "wrong-is-port-input"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"token": "login-token"})
        self.assertEqual(
            self.iniciar_sesion.calls,
            [("ana@example.com", "wrong-is-port-input")],
        )

    def test_invalid_or_missing_json_body_returns_400(self) -> None:
        invalid_responses = (
            self.client.post("/registro", data="{", content_type="application/json"),
            self.client.post("/login", data="not json", content_type="text/plain"),
            self.client.post("/registro", json=["not", "an", "object"]),
        )
        for response in invalid_responses:
            with self.subTest(path=response.request.path):
                self.assertEqual(response.status_code, 400)

    def test_missing_fields_return_400_without_calling_ports(self) -> None:
        registration_response = self.client.post(
            "/registro",
            json={"nombre": "Ana"},
        )
        login_response = self.client.post("/login", json={"correo": "ana@example.com"})

        self.assertEqual(registration_response.status_code, 400)
        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(self.registrar.calls, [])
        self.assertEqual(self.iniciar_sesion.calls, [])

    def test_non_string_fields_return_400_without_calling_ports(self) -> None:
        response = self.client.post(
            "/login",
            json={"correo": "ana@example.com", "contrasena": 123},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.iniciar_sesion.calls, [])

    def test_validation_error_returns_400_with_domain_message(self) -> None:
        self.registrar.error = InvalidEmailError()

        response = self.client.post(
            "/registro",
            json={
                "nombre": "Ana",
                "apellido": "Pérez",
                "nickname": "anap",
                "correo": "invalid",
                "contrasena": "Clave123",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"error": "El correo electrónico no tiene un formato válido."},
        )

    def test_duplicate_email_returns_generic_registration_error(self) -> None:
        self.registrar.error = EmailAlreadyRegisteredError()

        response = self.client.post(
            "/registro",
            json={
                "nombre": "Ana",
                "apellido": "Pérez",
                "nickname": "anap",
                "correo": "ana@example.com",
                "contrasena": "Clave123",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {"error": "No se pudo completar el registro"},
        )
        self.assertNotIn("correo", response.get_json()["error"].lower())

    def test_invalid_credentials_return_generic_401(self) -> None:
        self.iniciar_sesion.error = InvalidCredentialsError()

        response = self.client.post(
            "/login",
            json={"correo": "ana@example.com", "contrasena": "Clave123"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.get_json(), {"error": "Credenciales inválidas"})
        self.assertNotIn("correo", response.get_json()["error"].lower())
        self.assertNotIn("contraseña", response.get_json()["error"].lower())

    def test_repository_error_returns_generic_500_without_logging_details(self) -> None:
        self.registrar.error = RepositoryError("secret database detail")

        with self.assertLogs(
            "backend.usuarios.infrastructure.controllers.web_app_controller"
        ) as captured:
            response = self.client.post(
                "/registro",
                json={
                    "nombre": "Ana",
                    "apellido": "Pérez",
                    "nickname": "anap",
                    "correo": "ana@example.com",
                    "contrasena": "Clave123",
                },
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "Error interno del servidor"})
        self.assertNotIn("secret database detail", "\n".join(captured.output))

    def test_unexpected_error_returns_generic_500(self) -> None:
        self.iniciar_sesion.error = RuntimeError("sensitive exception")

        with self.assertLogs(
            "backend.usuarios.infrastructure.controllers.web_app_controller"
        ) as captured:
            response = self.client.post(
                "/login",
                json={"correo": "ana@example.com", "contrasena": "Clave123"},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json(), {"error": "Error interno del servidor"})
        self.assertNotIn("sensitive exception", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
